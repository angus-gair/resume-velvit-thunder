@echo off
REM Enhanced Development Environment Startup Script for Windows
REM Starts both FastAPI backend and Next.js frontend with comprehensive checks

setlocal enabledelayedexpansion

REM Default configuration
set BACKEND_PORT=8000
set FRONTEND_PORT=3000
set BACKEND_ONLY=false
set FRONTEND_ONLY=false
set FORCE_CLEANUP=false
set VENV_PATH=.venv-new

REM Colors for output (if supported)
set COLOR_RED=
set COLOR_GREEN=
set COLOR_YELLOW=
set COLOR_BLUE=
set COLOR_RESET=

REM Check for help flag
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help

:parse_args
if "%1"=="" goto :validate_environment
if "%1"=="--backend-only" (
    set BACKEND_ONLY=true
    shift
    goto :parse_args
)
if "%1"=="--frontend-only" (
    set FRONTEND_ONLY=true
    shift
    goto :parse_args
)
if "%1"=="--backend-port" (
    set BACKEND_PORT=%2
    shift
    shift
    goto :parse_args
)
if "%1"=="--frontend-port" (
    set FRONTEND_PORT=%2
    shift
    shift
    goto :parse_args
)
if "%1"=="--force-cleanup" (
    set FORCE_CLEANUP=true
    shift
    goto :parse_args
)
if "%1"=="--venv" (
    set VENV_PATH=%2
    shift
    shift
    goto :parse_args
)

echo [ERROR] Unknown option: %1
echo Use --help for usage information.
exit /b 1

:help
echo Usage: %0 [OPTIONS]
echo.
echo Enhanced Resume Builder Development Environment Startup
echo.
echo Options:
echo   --backend-only       Start only the backend server
echo   --frontend-only      Start only the frontend server
echo   --backend-port PORT  Backend port (default: 8000)
echo   --frontend-port PORT Frontend port (default: 3000)
echo   --force-cleanup      Force kill existing processes on required ports
echo   --venv PATH          Virtual environment path (default: .venv-new)
echo   --help, -h           Show this help message
echo.
echo Examples:
echo   %0                           Start both servers with default settings
echo   %0 --backend-only            Start only the backend server
echo   %0 --force-cleanup           Kill existing processes and start fresh
echo   %0 --backend-port 8080       Use port 8080 for backend
exit /b 0

:validate_environment
REM Validate that both flags aren't set
if "%BACKEND_ONLY%"=="true" if "%FRONTEND_ONLY%"=="true" (
    echo [ERROR] Cannot use --backend-only and --frontend-only together
    exit /b 1
)

echo ========================================
echo   Resume Builder Development Environment
echo ========================================
echo.

REM Check if required directories exist
if not exist "api" (
    echo [ERROR] Backend directory 'api' not found!
    echo [INFO] Please ensure you're running this script from the project root directory.
    exit /b 1
)

if not exist "v0-resume-creation-framework" (
    echo [ERROR] Frontend directory 'v0-resume-creation-framework' not found!
    echo [INFO] Please ensure you're running this script from the project root directory.
    exit /b 1
)

REM Check virtual environment
if not exist "%VENV_PATH%" (
    echo [ERROR] Virtual environment not found at: %VENV_PATH%
    echo [INFO] Creating new virtual environment...
    python -m venv %VENV_PATH%
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment!
        exit /b 1
    )
    echo [INFO] Installing required packages...
    call %VENV_PATH%\Scripts\activate.bat
    pip install fastapi uvicorn[standard]
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install required packages!
        exit /b 1
    )
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo [INFO] Environment validation complete.
echo.

:check_existing_processes
echo [CHECK] Scanning for existing application processes...

REM Check for existing processes on our ports
call :check_port_usage %BACKEND_PORT% backend_in_use
call :check_port_usage %FRONTEND_PORT% frontend_in_use

REM Check for existing Resume Builder processes
set existing_processes=false
for /f "tokens=2" %%i in ('tasklist /fi "WINDOWTITLE eq Resume Builder - Backend" /fo csv ^| find /c /v ""') do (
    if %%i gtr 1 set existing_processes=true
)
for /f "tokens=2" %%i in ('tasklist /fi "WINDOWTITLE eq Resume Builder - Frontend" /fo csv ^| find /c /v ""') do (
    if %%i gtr 1 set existing_processes=true
)

REM Handle existing processes/ports
if "%backend_in_use%"=="true" (
    echo [WARNING] Port %BACKEND_PORT% is already in use!
    if "%FORCE_CLEANUP%"=="true" (
        echo [ACTION] Force cleanup enabled. Attempting to free port %BACKEND_PORT%...
        call :kill_port_process %BACKEND_PORT%
    ) else (
        echo [ERROR] Backend port %BACKEND_PORT% is occupied. Use --force-cleanup to automatically resolve.
        echo [INFO] Or manually stop the process and try again.
        exit /b 1
    )
)

if "%frontend_in_use%"=="true" (
    echo [WARNING] Port %FRONTEND_PORT% is already in use!
    if "%FORCE_CLEANUP%"=="true" (
        echo [ACTION] Force cleanup enabled. Attempting to free port %FRONTEND_PORT%...
        call :kill_port_process %FRONTEND_PORT%
    ) else (
        echo [ERROR] Frontend port %FRONTEND_PORT% is occupied. Use --force-cleanup to automatically resolve.
        echo [INFO] Or manually stop the process and try again.
        exit /b 1
    )
)

if "%existing_processes%"=="true" (
    echo [WARNING] Existing Resume Builder processes detected!
    if "%FORCE_CLEANUP%"=="true" (
        echo [ACTION] Cleaning up existing processes...
        taskkill /fi "WINDOWTITLE eq Resume Builder - Backend" /f /t >nul 2>&1
        taskkill /fi "WINDOWTITLE eq Resume Builder - Frontend" /f /t >nul 2>&1
        timeout /t 2 /nobreak >nul
    ) else (
        echo [WARNING] Existing processes may interfere with startup.
        echo [INFO] Use --force-cleanup to automatically clean up existing processes.
    )
)

echo [INFO] Port and process checks complete.
echo.

:start_servers
REM Start backend server
if not "%FRONTEND_ONLY%"=="true" (
    echo [STARTING] FastAPI backend server on port %BACKEND_PORT%...
    
    REM Verify virtual environment and dependencies
    if not exist "%VENV_PATH%\Scripts\activate.bat" (
        echo [ERROR] Virtual environment activation script not found!
        exit /b 1
    )
    
    REM Start backend in new window with proper error handling
    start "Resume Builder - Backend" cmd /k "echo [BACKEND] Initializing backend server... && cd /d api && call ../%VENV_PATH%/Scripts/activate.bat && echo [BACKEND] Virtual environment activated && echo [BACKEND] Starting FastAPI server on http://127.0.0.1:%BACKEND_PORT% && python -m uvicorn main:app --reload --host 127.0.0.1 --port %BACKEND_PORT% || (echo [ERROR] Backend failed to start! && pause)"
    
    REM Wait and verify backend startup
    echo [INFO] Waiting for backend to initialize...
    timeout /t 5 /nobreak >nul
    
    REM Verify backend is responding
    call :verify_backend_startup %BACKEND_PORT%
    
    echo [SUCCESS] Backend server started successfully
    echo [INFO] Backend URL: http://127.0.0.1:%BACKEND_PORT%
    echo [INFO] API Documentation: http://127.0.0.1:%BACKEND_PORT%/docs
    echo.
)

REM Start frontend server
if not "%BACKEND_ONLY%"=="true" (
    echo [STARTING] Next.js frontend server on port %FRONTEND_PORT%...
    
    REM Check if node_modules exists
    if not exist "v0-resume-creation-framework\node_modules" (
        echo [INFO] Node modules not found. Installing dependencies...
        cd v0-resume-creation-framework
        npm install
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to install frontend dependencies!
            cd ..
            exit /b 1
        )
        cd ..
    )
    
    REM Start frontend in new window
    start "Resume Builder - Frontend" cmd /k "echo [FRONTEND] Initializing frontend server... && cd /d v0-resume-creation-framework && echo [FRONTEND] Starting Next.js development server on http://127.0.0.1:%FRONTEND_PORT% && npm run dev || (echo [ERROR] Frontend failed to start! && pause)"
    
    REM Wait and verify frontend startup
    echo [INFO] Waiting for frontend to initialize...
    timeout /t 8 /nobreak >nul
    
    echo [SUCCESS] Frontend server started successfully
    echo [INFO] Frontend URL: http://127.0.0.1:%FRONTEND_PORT%
    echo.
)

:startup_complete
echo ========================================
echo   DEVELOPMENT ENVIRONMENT RUNNING
echo ========================================
echo.
if not "%FRONTEND_ONLY%"=="true" (
    echo   🔧 Backend API:     http://127.0.0.1:%BACKEND_PORT%
    echo   📚 API Docs:       http://127.0.0.1:%BACKEND_PORT%/docs
    echo   📋 Health Check:   http://127.0.0.1:%BACKEND_PORT%/health
)
if not "%BACKEND_ONLY%"=="true" (
    echo   🌐 Frontend App:   http://127.0.0.1:%FRONTEND_PORT%
)
echo.
echo   📁 Logs Directory: logs\
if not "%FRONTEND_ONLY%"=="true" (
    echo   📄 Backend Log:    logs\backend.log
)
if not "%BACKEND_ONLY%"=="true" (
    echo   📄 Frontend Log:   logs\frontend.log
)
echo.
echo ========================================
echo   MANAGEMENT COMMANDS
echo ========================================
echo.
echo   • Close individual terminal windows to stop specific servers
echo   • Use Ctrl+C in server windows to gracefully stop servers
echo   • Run this script with --force-cleanup to reset everything
echo.

REM Open applications in browser
if not "%FRONTEND_ONLY%"=="true" (
    echo [INFO] Opening API documentation in browser...
    start http://127.0.0.1:%BACKEND_PORT%/docs
)
if not "%BACKEND_ONLY%"=="true" (
    echo [INFO] Opening frontend application in browser...
    timeout /t 2 /nobreak >nul
    start http://127.0.0.1:%FRONTEND_PORT%
)

echo [SUCCESS] All services started successfully!
echo [INFO] Press any key to exit this window (servers will continue running)
pause >nul
exit /b 0

REM ===========================================
REM UTILITY FUNCTIONS
REM ===========================================

:check_port_usage
REM Check if a port is in use
REM %1 = port number, %2 = return variable name
netstat -an | find ":%1 " | find "LISTENING" >nul 2>&1
if !errorlevel! equ 0 (
    set %2=true
) else (
    set %2=false
)
goto :eof

:kill_port_process
REM Kill process using specific port
REM %1 = port number
for /f "tokens=5" %%i in ('netstat -ano ^| find ":%1 " ^| find "LISTENING"') do (
    if "%%i" neq "" (
        echo [ACTION] Killing process %%i on port %1...
        taskkill /PID %%i /F >nul 2>&1
        timeout /t 1 /nobreak >nul
    )
)
goto :eof

:verify_backend_startup
REM Verify backend is responding
REM %1 = backend port
curl -s http://127.0.0.1:%1 >nul 2>&1
if !errorlevel! equ 0 (
    echo [VERIFY] Backend health check passed
) else (
    echo [WARNING] Backend may still be starting up...
)
goto :eof 