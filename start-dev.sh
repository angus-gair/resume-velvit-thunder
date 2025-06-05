#!/bin/bash
# Development environment startup script
# Starts both FastAPI backend and Next.js frontend

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[DEV]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to cleanup processes on exit
cleanup() {
    print_status "Shutting down development environment..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        print_status "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        print_status "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Force kill if still running
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        print_warning "Force killing backend process..."
        kill -9 $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        print_warning "Force killing frontend process..."
        kill -9 $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_success "Development environment stopped."
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM EXIT

# Parse command line arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
BACKEND_PORT=8000
FRONTEND_PORT=3000

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only       Start only the backend server"
            echo "  --frontend-only      Start only the frontend server"
            echo "  --backend-port PORT  Backend port (default: 8000)"
            echo "  --frontend-port PORT Frontend port (default: 3000)"
            echo "  --help, -h           Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Validate that both flags aren't set
if [ "$BACKEND_ONLY" = true ] && [ "$FRONTEND_ONLY" = true ]; then
    print_error "Cannot use --backend-only and --frontend-only together"
    exit 1
fi

print_status "Starting Resume Generation Development Environment"
echo ""

# Check if required directories exist
if [ ! -d "api" ]; then
    print_error "Backend directory 'api' not found!"
    exit 1
fi

if [ ! -d "v0-resume-creation-framework" ]; then
    print_error "Frontend directory 'v0-resume-creation-framework' not found!"
    exit 1
fi

# Start backend server
if [ "$FRONTEND_ONLY" != true ]; then
    print_status "Checking backend port $BACKEND_PORT..."
    if ! check_port $BACKEND_PORT; then
        print_error "Port $BACKEND_PORT is already in use!"
        print_warning "Please stop the service using port $BACKEND_PORT or use --backend-port to specify a different port."
        exit 1
    fi
    
    print_status "Starting FastAPI backend on port $BACKEND_PORT..."
    cd api
    
    # Check if virtual environment exists and activate it
    if [ -d "../.venv" ]; then
        print_status "Activating virtual environment..."
        source ../.venv/bin/activate
    else
        print_warning "No virtual environment found at .venv"
    fi
    
    # Check if uvicorn is available
    if ! command -v uvicorn &> /dev/null; then
        print_error "uvicorn not found! Please install it with: pip install uvicorn"
        exit 1
    fi
    
    # Start backend in background
    python -m uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment and check if backend started successfully
    sleep 3
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Failed to start backend server!"
        print_error "Check logs/backend.log for details."
        exit 1
    fi
    
    print_success "Backend server started (PID: $BACKEND_PID)"
    print_status "Backend URL: http://localhost:$BACKEND_PORT"
    print_status "API Documentation: http://localhost:$BACKEND_PORT/docs"
fi

# Start frontend server
if [ "$BACKEND_ONLY" != true ]; then
    print_status "Checking frontend port $FRONTEND_PORT..."
    if ! check_port $FRONTEND_PORT; then
        print_error "Port $FRONTEND_PORT is already in use!"
        print_warning "Please stop the service using port $FRONTEND_PORT or use --frontend-port to specify a different port."
        exit 1
    fi
    
    print_status "Starting Next.js frontend on port $FRONTEND_PORT..."
    cd v0-resume-creation-framework
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Installing dependencies..."
        if command -v npm &> /dev/null; then
            npm install
        else
            print_error "npm not found! Please install Node.js and npm."
            exit 1
        fi
    fi
    
    # Set the port for Next.js
    export PORT=$FRONTEND_PORT
    
    # Start frontend in background
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait a moment and check if frontend started successfully
    sleep 5
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Failed to start frontend server!"
        print_error "Check logs/frontend.log for details."
        exit 1
    fi
    
    print_success "Frontend server started (PID: $FRONTEND_PID)"
    print_status "Frontend URL: http://localhost:$FRONTEND_PORT"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
print_success "Development environment is running!"
echo ""
if [ "$FRONTEND_ONLY" != true ]; then
    echo -e "  ${GREEN}Backend:${NC}  http://localhost:$BACKEND_PORT"
    echo -e "  ${GREEN}API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
fi
if [ "$BACKEND_ONLY" != true ]; then
    echo -e "  ${GREEN}Frontend:${NC} http://localhost:$FRONTEND_PORT"
fi
echo ""
echo -e "  ${BLUE}Logs:${NC}"
if [ "$FRONTEND_ONLY" != true ]; then
    echo -e "    Backend:  logs/backend.log"
fi
if [ "$BACKEND_ONLY" != true ]; then
    echo -e "    Frontend: logs/frontend.log"
fi
echo ""
print_status "Press Ctrl+C to stop all servers"

# Wait for processes to finish
if [ "$FRONTEND_ONLY" != true ] && [ "$BACKEND_ONLY" != true ]; then
    wait $BACKEND_PID $FRONTEND_PID
elif [ "$BACKEND_ONLY" = true ]; then
    wait $BACKEND_PID
elif [ "$FRONTEND_ONLY" = true ]; then
    wait $FRONTEND_PID
fi 