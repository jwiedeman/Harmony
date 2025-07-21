@echo off
setlocal enabledelayedexpansion

:: Harmony QA System - Windows Launch Script
:: This script automatically sets up and launches the Harmony QA System on Windows

title Harmony QA System - Windows Launcher

:: Set colors
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

:: Function to print colored output
:print_status
echo %BLUE%[HARMONY]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:: Function to check if command exists
:command_exists
where %1 >nul 2>&1
goto :eof

:: Function to check Node.js version
:check_node_version
for /f "tokens=1 delims=v" %%i in ('node --version 2^>nul') do (
    set NODE_VERSION=%%i
)
if defined NODE_VERSION (
    for /f "tokens=1 delims=." %%a in ("!NODE_VERSION!") do set NODE_MAJOR=%%a
    if !NODE_MAJOR! LSS 16 (
        call :print_warning "Node.js version is too old. Please install Node.js 16 or higher."
        set NODE_OLD=1
    ) else (
        call :print_success "Node.js already installed (!NODE_VERSION!)"
        set NODE_OK=1
    )
) else (
    set NODE_MISSING=1
)
goto :eof

:: Function to check Python version
:check_python_version
for /f "tokens=2 delims= " %%i in ('python --version 2^>nul') do (
    set PYTHON_VERSION=%%i
)
if not defined PYTHON_VERSION (
    for /f "tokens=2 delims= " %%i in ('python3 --version 2^>nul') do (
        set PYTHON_VERSION=%%i
    )
)
if defined PYTHON_VERSION (
    for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
        set PY_MAJOR=%%a
        set PY_MINOR=%%b
    )
    if !PY_MAJOR! LSS 3 (
        set PYTHON_OLD=1
    ) else if !PY_MAJOR! EQU 3 if !PY_MINOR! LSS 8 (
        set PYTHON_OLD=1
    ) else (
        call :print_success "Python already installed (!PYTHON_VERSION!)"
        set PYTHON_OK=1
    )
) else (
    set PYTHON_MISSING=1
)
goto :eof

:: Function to install Chocolatey
:install_chocolatey
call :print_status "Installing Chocolatey package manager..."
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
call :print_success "Chocolatey installed. Please restart this script."
pause
exit /b 1
goto :eof

:: Function to check dependencies
:check_dependencies
call :print_status "Checking system dependencies..."

:: Check for Chocolatey
call :command_exists choco
if errorlevel 1 (
    call :print_warning "Chocolatey not found. Installing Chocolatey..."
    call :install_chocolatey
)

:: Check Node.js
call :check_node_version
if defined NODE_MISSING (
    call :print_status "Installing Node.js..."
    choco install nodejs -y
    call :print_success "Node.js installed successfully"
) else if defined NODE_OLD (
    call :print_status "Updating Node.js..."
    choco upgrade nodejs -y
)

:: Check Python
call :check_python_version
if defined PYTHON_MISSING (
    call :print_status "Installing Python 3..."
    choco install python3 -y
    call :print_success "Python 3 installed successfully"
) else if defined PYTHON_OLD (
    call :print_warning "Python version is too old. Updating Python..."
    choco upgrade python3 -y
)

:: Check Git (needed for some npm packages)
call :command_exists git
if errorlevel 1 (
    call :print_status "Installing Git..."
    choco install git -y
    call :print_success "Git installed successfully"
)

:: Refresh environment variables
refreshenv

goto :eof

:: Function to install Yarn
:install_yarn
call :command_exists yarn
if errorlevel 1 (
    call :print_status "Installing Yarn package manager..."
    npm install -g yarn
    call :print_success "Yarn installed successfully"
) else (
    call :print_success "Yarn already installed"
)
goto :eof

:: Function to cleanup processes
:cleanup_processes
call :print_status "Cleaning up any existing processes..."

:: Kill processes on ports 3000 and 8001
netstat -ano | findstr :3000 > nul 2>&1
if not errorlevel 1 (
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :3000') do (
        taskkill /PID %%i /F > nul 2>&1
    )
)

netstat -ano | findstr :8001 > nul 2>&1
if not errorlevel 1 (
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8001') do (
        taskkill /PID %%i /F > nul 2>&1
    )
)

call :print_success "Process cleanup completed"
goto :eof

:: Function to install Python dependencies
:install_python_deps
call :print_status "Installing Python dependencies..."

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install requirements
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

call :print_success "Python dependencies installed"
goto :eof

:: Function to install Node.js dependencies
:install_node_deps
call :print_status "Installing Node.js dependencies..."

cd frontend
yarn install
cd ..

call :print_success "Node.js dependencies installed"
goto :eof

:: Function to start backend
:start_backend
call :print_status "Starting backend server..."

call venv\Scripts\activate.bat
cd backend
start /B python server.py
cd ..

:: Wait for backend to start
timeout /t 3 /nobreak > nul

:: Check if backend is running
netstat -ano | findstr :8001 > nul 2>&1
if not errorlevel 1 (
    call :print_success "Backend server started"
) else (
    call :print_error "Failed to start backend server"
    pause
    exit /b 1
)
goto :eof

:: Function to start frontend
:start_frontend
call :print_status "Starting frontend server..."

cd frontend
start /B yarn start
cd ..

:: Wait for frontend to compile
call :print_status "Building frontend application..."
timeout /t 15 /nobreak > nul

:: Check if frontend is running
netstat -ano | findstr :3000 > nul 2>&1
if not errorlevel 1 (
    call :print_success "Frontend server started"
) else (
    call :print_error "Failed to start frontend server"
    pause
    exit /b 1
)
goto :eof

:: Function to open browser
:open_application
call :print_status "Opening Harmony QA System in browser..."
timeout /t 2 /nobreak > nul
start http://localhost:3000
call :print_success "Application should now be open in your browser"
goto :eof

:: Main execution
:main
cls
echo.
echo %BLUE%
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                           HARMONY QA SYSTEM                                 ║
echo ║                       Windows Launch Script v1.0                            ║
echo ║                                                                              ║
echo ║  This script will automatically install all dependencies and launch         ║
echo ║  the Harmony QA System on your Windows machine.                             ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo %NC%
echo.

call :print_status "Starting Harmony QA System setup for Windows..."

:: Check if we're in the right directory
if not exist "harmony.py" (
    call :print_error "harmony.py not found in current directory"
    call :print_error "Please run this script from the Harmony QA System root directory"
    pause
    exit /b 1
)
if not exist "frontend" (
    call :print_error "frontend folder not found in current directory"
    call :print_error "Please run this script from the Harmony QA System root directory"
    pause
    exit /b 1
)
if not exist "backend" (
    call :print_error "backend folder not found in current directory"
    call :print_error "Please run this script from the Harmony QA System root directory"
    pause
    exit /b 1
)

:: Install system dependencies
call :check_dependencies
call :install_yarn

:: Cleanup existing processes
call :cleanup_processes

:: Install project dependencies
call :install_python_deps
call :install_node_deps

:: Start services
call :start_backend
call :start_frontend
call :open_application

echo.
echo %GREEN%
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                          🚀 LAUNCH SUCCESSFUL! 🚀                           ║
echo ║                                                                              ║
echo ║  Harmony QA System is now running:                                          ║
echo ║                                                                              ║
echo ║  🌐 Web Interface: http://localhost:3000                                    ║
echo ║  🔧 API Endpoint:  http://localhost:8001                                    ║
echo ║                                                                              ║
echo ║  📖 Documentation: Open USER_GUIDE.md for usage instructions               ║
echo ║                                                                              ║
echo ║  ⚠️  Keep this terminal window open while using the application            ║
echo ║  🛑 Press Ctrl+C to stop all services                                      ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo %NC%

echo.
call :print_status "Press any key to stop all services..."
pause > nul

:: Cleanup on exit
call :print_status "Shutting down Harmony QA System..."
taskkill /F /IM python.exe > nul 2>&1
taskkill /F /IM node.exe > nul 2>&1
call :print_success "All services stopped"

pause
exit /b 0

:: Call main function
call :main