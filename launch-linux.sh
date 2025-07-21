#!/bin/bash

# Harmony QA System - Linux Launch Script
# This script automatically sets up and launches the Harmony QA System on Linux

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[HARMONY]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect Linux distribution
detect_distro() {
    if [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/redhat-release ]; then
        echo "redhat"
    elif [ -f /etc/arch-release ]; then
        echo "arch"
    else
        echo "unknown"
    fi
}

# Function to update package manager
update_packages() {
    DISTRO=$(detect_distro)
    print_status "Updating package manager..."
    
    case $DISTRO in
        debian)
            sudo apt update
            ;;
        redhat)
            sudo yum update -y || sudo dnf update -y
            ;;
        arch)
            sudo pacman -Sy
            ;;
        *)
            print_warning "Unknown Linux distribution. Package updates may need to be done manually."
            ;;
    esac
    
    print_success "Package manager updated"
}

# Function to install Node.js
install_nodejs() {
    if ! command_exists node; then
        print_status "Installing Node.js..."
        
        DISTRO=$(detect_distro)
        case $DISTRO in
            debian)
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            redhat)
                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                sudo yum install -y nodejs || sudo dnf install -y nodejs
                ;;
            arch)
                sudo pacman -S --noconfirm nodejs npm
                ;;
            *)
                print_error "Unable to install Node.js automatically for your distribution."
                print_error "Please install Node.js 16+ manually from https://nodejs.org/"
                exit 1
                ;;
        esac
        
        print_success "Node.js installed successfully"
    else
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 16 ]; then
            print_warning "Node.js version is too old. Please update to version 16 or higher."
            exit 1
        else
            print_success "Node.js already installed ($(node --version))"
        fi
    fi
}

# Function to install Python
install_python() {
    if ! command_exists python3; then
        print_status "Installing Python 3..."
        
        DISTRO=$(detect_distro)
        case $DISTRO in
            debian)
                sudo apt-get install -y python3 python3-pip python3-venv
                ;;
            redhat)
                sudo yum install -y python3 python3-pip || sudo dnf install -y python3 python3-pip
                ;;
            arch)
                sudo pacman -S --noconfirm python python-pip
                ;;
            *)
                print_error "Unable to install Python automatically for your distribution."
                print_error "Please install Python 3.8+ manually."
                exit 1
                ;;
        esac
        
        print_success "Python 3 installed successfully"
    else
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$(echo $PYTHON_VERSION | cut -d'.' -f1)" -lt 3 ] || [ "$(echo $PYTHON_VERSION | cut -d'.' -f2)" -lt 8 ]; then
            print_error "Python version is too old. Please update to Python 3.8 or higher."
            exit 1
        else
            print_success "Python 3 already installed ($(python3 --version))"
        fi
    fi
}

# Function to install additional dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    DISTRO=$(detect_distro)
    case $DISTRO in
        debian)
            sudo apt-get install -y curl wget git build-essential
            ;;
        redhat)
            sudo yum groupinstall -y "Development Tools" || sudo dnf groupinstall -y "Development Tools"
            sudo yum install -y curl wget git || sudo dnf install -y curl wget git
            ;;
        arch)
            sudo pacman -S --noconfirm curl wget git base-devel
            ;;
        *)
            print_warning "Please ensure curl, wget, git, and build tools are installed."
            ;;
    esac
    
    print_success "System dependencies installed"
}

# Function to install Yarn
install_yarn() {
    if ! command_exists yarn; then
        print_status "Installing Yarn package manager..."
        npm install -g yarn
        print_success "Yarn installed successfully"
    else
        print_success "Yarn already installed ($(yarn --version))"
    fi
}

# Function to check and kill existing processes
cleanup_processes() {
    print_status "Cleaning up any existing processes..."
    
    # Kill processes on ports 3000 and 8001
    sudo lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sudo lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    
    print_success "Process cleanup completed"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    print_success "Python dependencies installed"
}

# Function to install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    cd frontend
    yarn install
    cd ..
    
    print_success "Node.js dependencies installed"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    source venv/bin/activate
    cd backend
    python server.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is running
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_success "Backend server started (PID: $BACKEND_PID)"
    else
        print_error "Failed to start backend server"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend
    yarn start &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to compile
    print_status "Building frontend application..."
    sleep 15
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_success "Frontend server started (PID: $FRONTEND_PID)"
    else
        print_error "Failed to start frontend server"
        exit 1
    fi
}

# Function to open browser
open_application() {
    print_status "Opening Harmony QA System in browser..."
    sleep 2
    
    # Try different browser commands
    if command_exists xdg-open; then
        xdg-open http://localhost:3000
    elif command_exists google-chrome; then
        google-chrome http://localhost:3000
    elif command_exists firefox; then
        firefox http://localhost:3000
    else
        print_warning "Could not open browser automatically."
        print_warning "Please open http://localhost:3000 in your web browser."
    fi
    
    print_success "Application should now be accessible in your browser"
}

# Main execution
main() {
    clear
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                           HARMONY QA SYSTEM                                 ║"
    echo "║                        Linux Launch Script v1.0                             ║"
    echo "║                                                                              ║"
    echo "║  This script will automatically install all dependencies and launch         ║"
    echo "║  the Harmony QA System on your Linux machine.                               ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    
    print_status "Starting Harmony QA System setup for Linux..."
    
    # Check if we're in the right directory
    if [ ! -f "harmony.py" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
        print_error "Please run this script from the Harmony QA System root directory"
        print_error "Make sure the following files/folders exist: harmony.py, frontend/, backend/"
        exit 1
    fi
    
    # Install dependencies
    update_packages
    install_system_deps
    install_nodejs
    install_python
    install_yarn
    
    # Cleanup existing processes
    cleanup_processes
    
    # Install project dependencies
    install_python_deps
    install_node_deps
    
    # Start services
    start_backend
    start_frontend
    open_application
    
    echo
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          🚀 LAUNCH SUCCESSFUL! 🚀                           ║"
    echo "║                                                                              ║"
    echo "║  Harmony QA System is now running:                                          ║"
    echo "║                                                                              ║"
    echo "║  🌐 Web Interface: http://localhost:3000                                    ║"
    echo "║  🔧 API Endpoint:  http://localhost:8001                                    ║"
    echo "║                                                                              ║"
    echo "║  📖 Documentation: Open USER_GUIDE.md for usage instructions               ║"
    echo "║                                                                              ║"
    echo "║  ⚠️  Keep this terminal window open while using the application            ║"
    echo "║  🛑 Press Ctrl+C to stop all services                                      ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Wait for user interrupt
    trap 'print_status "Shutting down Harmony QA System..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT
    
    while true; do
        sleep 1
    done
}

# Run main function
main