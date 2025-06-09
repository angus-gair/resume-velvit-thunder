# Run the Resume Builder API

# Check if virtual environment exists
$venvDir = ".\venv"
$activateScript = "$venvDir\Scripts\Activate.ps1"

if (-not (Test-Path -Path $activateScript)) {
    Write-Error "Virtual environment not found. Please run .\setup_dev_env.ps1 first."
    exit 1
}

# Activate virtual environment
. $activateScript

# Check if .env file exists
if (-not (Test-Path -Path ".env")) {
    Write-Error ".env file not found. Please create it from .env.example"
    exit 1
}

# Load environment variables
Get-Content .env | ForEach-Object {
    $name, $value = $_.split('=', 2)
    if ($name -and $value) {
        [System.Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim())
    }
}

# Run the application
Write-Host "🚀 Starting Resume Builder API..." -ForegroundColor Green
Write-Host "   API will be available at http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn api.main:app --host $env:HOST --port $env:PORT --reload
