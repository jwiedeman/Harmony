#!/bin/bash

# Harmony QA System - macOS Launch Script
# This script automatically sets up and launches the Harmony QA System on macOS

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

# Function to install Homebrew if not present
install_homebrew() {
    if ! command_exists brew; then
        print_status "Installing Homebrew package manager..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        print_success "Homebrew installed successfully"
    else
        print_success "Homebrew already installed"
    fi
}

# Function to install Node.js
install_nodejs() {
    if ! command_exists node; then
        print_status "Installing Node.js..."
        brew install node
        print_success "Node.js installed successfully"
    else
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 16 ]; then
            print_warning "Node.js version is too old. Updating..."
            brew upgrade node
        else
            print_success "Node.js already installed ($(node --version))"
        fi
    fi
}

# Function to install Python
install_python() {
    if ! command_exists python3; then
        print_status "Installing Python 3..."
        brew install python@3.11
        print_success "Python 3 installed successfully"
    else
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$(echo $PYTHON_VERSION | cut -d'.' -f1)" -lt 3 ] || [ "$(echo $PYTHON_VERSION | cut -d'.' -f2)" -lt 8 ]; then
            print_warning "Python version is too old. Updating..."
            brew upgrade python@3.11
        else
            print_success "Python 3 already installed ($(python3 --version))"
        fi
    fi
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
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    
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
    open http://localhost:3000
    print_success "Application should now be open in your browser"
}

# Main execution
main() {
    clear
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                           HARMONY QA SYSTEM                                 ║"
    echo "║                        macOS Launch Script v1.0                             ║"
    echo "║                                                                              ║"
    echo "║  This script will automatically install all dependencies and launch         ║"
    echo "║  the Harmony QA System on your Mac.                                         ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    
    print_status "Starting Harmony QA System setup for macOS..."
    
    # Check if we're in the right directory
    if [ ! -f "harmony.py" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
        print_error "Please run this script from the Harmony QA System root directory"
        print_error "Make sure the following files/folders exist: harmony.py, frontend/, backend/"
        exit 1
    fi
    
    # Install dependencies
    install_homebrew
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