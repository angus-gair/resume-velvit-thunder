# Run tests for the Resume Builder API

# Check if virtual environment exists
$venvDir = ".\venv"
$activateScript = "$venvDir\Scripts\Activate.ps1"

if (-not (Test-Path -Path $activateScript)) {
    Write-Error "Virtual environment not found. Please run .\setup_dev_env.ps1 first."
    exit 1
}

# Activate virtual environment
. $activateScript

# Install test dependencies if not already installed
pip install -q -r requirements-test.txt

# Set environment variables for testing
$env:TESTING = "true"
$env:DATABASE_URL = "sqlite:///:memory:"

# Run pytest with coverage
Write-Host "🚀 Running tests..." -ForegroundColor Green
pytest -v --cov=api --cov-report=term-missing

# Capture the exit code
$testExitCode = $LASTEXITCODE

# Reset environment variables
Remove-Item Env:\TESTING
Remove-Item Env:\DATABASE_URL

# Exit with the test status code
exit $testExitCode
