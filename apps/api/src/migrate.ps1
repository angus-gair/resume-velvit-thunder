# Run database migrations

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

# Check if alembic is installed
$alembicVersion = alembic --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Alembic is not installed. Please install it with 'pip install alembic'"
    exit 1
}

Write-Host "🚀 Running database migrations..." -ForegroundColor Green

# Run migrations
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database migrations completed successfully" -ForegroundColor Green
} else {
    Write-Error "❌ Database migrations failed"
    exit 1
}
