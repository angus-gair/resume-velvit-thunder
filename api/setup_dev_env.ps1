# Setup development environment for Resume Builder API

# Check if Python is installed
$pythonVersion = python --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or higher and try again."
    exit 1
}

Write-Host "🐍 Found $pythonVersion" -ForegroundColor Green

# Create and activate virtual environment
Write-Host "🔧 Setting up virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path -Path "./venv")) {
    python -m venv venv
}

# Activate virtual environment
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Error "Failed to activate virtual environment. Script not found: $activateScript"
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-test.txt

# Create .env file if it doesn't exist
if (-not (Test-Path -Path ".env")) {
    Write-Host "⚙️  Creating .env file from .env.example" -ForegroundColor Cyan
    Copy-Item ".env.example" -Destination ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
}

# Create data directory if it doesn't exist
$dataDir = ".\data"
if (-not (Test-Path -Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
    Write-Host "📁 Created data directory" -ForegroundColor Green
}

# Initialize the database
Write-Host "💾 Initializing database..." -ForegroundColor Cyan
python -m scripts.init_db

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database initialized successfully" -ForegroundColor Green
} else {
    Write-Error "❌ Failed to initialize database"
    exit 1
}

Write-Host ""
Write-Host "🚀 Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the development server, run:" -ForegroundColor Cyan
Write-Host "  .\run.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "To run tests:" -ForegroundColor Cyan
Write-Host "  pytest" -ForegroundColor Yellow
Write-Host ""
Write-Host "To activate the virtual environment in a new terminal:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
