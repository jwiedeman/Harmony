#!/usr/bin/env python3

"""
Harmony QA System - Cross-Platform System Requirements Checker
This script checks if all required dependencies are installed and properly configured.
"""

import sys
import subprocess
import platform
import os
import shutil
from pathlib import Path

# ANSI color codes
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'

def print_status(message):
    print(f"{Colors.BLUE}[HARMONY]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def print_header():
    print(f"{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                     HARMONY QA SYSTEM - SYSTEM CHECK                        ║")
    print("║                         Requirements Verification                           ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")
    print()

def check_command(command, min_version=None, version_flag="--version"):
    """Check if a command exists and optionally verify version."""
    try:
        result = subprocess.run([command, version_flag], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_output = result.stdout.strip()
            if command == "node":
                # Extract version from "v16.14.2" format
                version = version_output.split()[0].replace('v', '')
            elif command == "python" or command == "python3":
                # Extract version from "Python 3.9.7" format
                version = version_output.split()[1]
            elif command == "yarn":
                # Yarn returns just the version number
                version = version_output.split()[0]
            else:
                version = version_output.split()[0]
            
            if min_version:
                if compare_versions(version, min_version):
                    print_success(f"{command} installed (v{version})")
                    return True
                else:
                    print_warning(f"{command} version {version} is below minimum required {min_version}")
                    return False
            else:
                print_success(f"{command} installed (v{version})")
                return True
        else:
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False

def compare_versions(current, minimum):
    """Compare version strings (e.g., '3.9.7' vs '3.8.0')"""
    current_parts = [int(x) for x in current.split('.')]
    minimum_parts = [int(x) for x in minimum.split('.')]
    
    # Pad shorter version with zeros
    max_length = max(len(current_parts), len(minimum_parts))
    current_parts.extend([0] * (max_length - len(current_parts)))
    minimum_parts.extend([0] * (max_length - len(minimum_parts)))
    
    return current_parts >= minimum_parts

def check_python():
    """Check Python installation and version."""
    print_status("Checking Python installation...")
    
    # Try different Python commands
    python_commands = ["python3", "python"]
    
    for cmd in python_commands:
        if check_command(cmd, "3.8.0", "--version"):
            # Check if pip is available
            try:
                subprocess.run([cmd, "-m", "pip", "--version"], 
                             capture_output=True, check=True, timeout=5)
                print_success(f"pip available with {cmd}")
                
                # Check if venv is available
                subprocess.run([cmd, "-m", "venv", "--help"], 
                             capture_output=True, check=True, timeout=5)
                print_success(f"venv module available with {cmd}")
                return True, cmd
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print_warning(f"pip or venv not available with {cmd}")
                continue
    
    print_error("Python 3.8+ with pip and venv not found")
    return False, None

def check_nodejs():
    """Check Node.js installation and version."""
    print_status("Checking Node.js installation...")
    
    if check_command("node", "16.0.0"):
        # Check if npm is available
        if check_command("npm", "8.0.0"):
            return True
        else:
            print_warning("npm not found or version too old")
            return False
    else:
        print_error("Node.js 16+ not found")
        return False

def check_yarn():
    """Check Yarn package manager."""
    print_status("Checking Yarn package manager...")
    
    if check_command("yarn", "1.22.0"):
        return True
    else:
        print_warning("Yarn not found (can be installed automatically)")
        return False

def check_git():
    """Check Git installation."""
    print_status("Checking Git installation...")
    
    if shutil.which("git"):
        print_success("Git installed")
        return True
    else:
        print_warning("Git not found (recommended for some npm packages)")
        return False

def check_ports():
    """Check if required ports are available."""
    print_status("Checking port availability...")
    
    import socket
    
    ports_to_check = [3000, 8001]
    all_available = True
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print_warning(f"Port {port} is already in use")
            all_available = False
        else:
            print_success(f"Port {port} is available")
    
    return all_available

def check_project_structure():
    """Check if all required project files exist."""
    print_status("Checking project structure...")
    
    required_files = [
        "harmony.py",
        "backend/server.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/src/App.js"
    ]
    
    all_present = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"Found {file_path}")
        else:
            print_error(f"Missing {file_path}")
            all_present = False
    
    return all_present

def get_platform_instructions():
    """Get platform-specific installation instructions."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return """
macOS Installation Instructions:

1. Install Homebrew (if not already installed):
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Install required packages:
   brew install node python@3.11 git

3. Install Yarn:
   npm install -g yarn

4. Run the launch script:
   chmod +x launch-mac.sh
   ./launch-mac.sh
"""
    
    elif system == "Linux":
        return """
Linux Installation Instructions:

Ubuntu/Debian:
1. Update package list:
   sudo apt update

2. Install required packages:
   sudo apt install nodejs npm python3 python3-pip python3-venv git curl build-essential

3. Install Node.js 16+:
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs

4. Install Yarn:
   npm install -g yarn

5. Run the launch script:
   chmod +x launch-linux.sh
   ./launch-linux.sh

Red Hat/CentOS/Fedora:
1. Install required packages:
   sudo yum install nodejs npm python3 python3-pip git curl gcc-c++ make
   # OR for newer versions:
   sudo dnf install nodejs npm python3 python3-pip git curl gcc-c++ make

2. Install Node.js 16+:
   curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
   sudo yum install nodejs

3. Install Yarn:
   npm install -g yarn

4. Run the launch script:
   chmod +x launch-linux.sh
   ./launch-linux.sh
"""
    
    elif system == "Windows":
        return """
Windows Installation Instructions:

Option 1 - Automatic (Recommended):
1. Run the Windows launch script as Administrator:
   launch-windows.bat
   
   This will automatically install Chocolatey and all dependencies.

Option 2 - Manual Installation:
1. Install Chocolatey (run as Administrator):
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

2. Install required packages:
   choco install nodejs python3 git -y

3. Install Yarn:
   npm install -g yarn

4. Run the launch script:
   launch-windows.bat

Option 3 - Manual Downloads:
1. Download and install Node.js 16+ from https://nodejs.org/
2. Download and install Python 3.8+ from https://python.org/
3. Download and install Git from https://git-scm.com/
4. Install Yarn: npm install -g yarn
5. Run: launch-windows.bat
"""
    
    else:
        return f"""
Unknown operating system: {system}

Please manually install:
- Node.js 16+ (https://nodejs.org/)
- Python 3.8+ (https://python.org/)
- Git (https://git-scm.com/)
- Yarn: npm install -g yarn

Then run the appropriate launch script for your platform.
"""

def main():
    """Main system check function."""
    print_header()
    
    print_status(f"Checking system: {platform.system()} {platform.release()}")
    print_status(f"Architecture: {platform.machine()}")
    print()
    
    checks_passed = 0
    total_checks = 6
    
    # Check project structure
    if check_project_structure():
        checks_passed += 1
    
    # Check Python
    python_ok, python_cmd = check_python()
    if python_ok:
        checks_passed += 1
    
    # Check Node.js
    if check_nodejs():
        checks_passed += 1
    
    # Check Yarn
    if check_yarn():
        checks_passed += 1
    
    # Check Git
    if check_git():
        checks_passed += 1
    
    # Check ports
    if check_ports():
        checks_passed += 1
    
    print()
    print("=" * 80)
    
    if checks_passed == total_checks:
        print_success(f"All checks passed! ({checks_passed}/{total_checks})")
        print()
        print(f"{Colors.GREEN}✓ Your system is ready to run Harmony QA System!{Colors.NC}")
        print()
        print("Run the appropriate launch script for your platform:")
        print("  • macOS:   ./launch-mac.sh")
        print("  • Linux:   ./launch-linux.sh")
        print("  • Windows: launch-windows.bat")
    else:
        print_warning(f"Some checks failed ({checks_passed}/{total_checks})")
        print()
        print(f"{Colors.YELLOW}⚠ Please install missing dependencies before running Harmony QA System{Colors.NC}")
        print()
        print(get_platform_instructions())
    
    print()
    return checks_passed == total_checks

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n")
        print_status("System check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error during system check: {e}")
        sys.exit(1)