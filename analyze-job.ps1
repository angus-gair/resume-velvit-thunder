#!/usr/bin/env pwsh
# PowerShell script to run job analysis

param(
    [Parameter(Position=0, Mandatory=$false)]
    [string]$JobFile = "paste.txt",
    
    [string]$OutputDir,
    [string]$ApiKey,
    [string]$Model,
    [switch]$Verbose
)

# Check if job file exists
if (-not (Test-Path $JobFile)) {
    Write-Host "Error: Job file '$JobFile' not found!" -ForegroundColor Red
    Write-Host "Usage: .\analyze-job.ps1 [job_file] [-OutputDir path] [-ApiKey key] [-Verbose]"
    exit 1
}

# Build command arguments
$args = @($JobFile)

if ($OutputDir) {
    $args += "-o", $OutputDir
}

if ($ApiKey) {
    $args += "-k", $ApiKey
}

if ($Model) {
    $args += "-m", $Model
}

if ($Verbose) {
    $args += "-v"
}

# Run the analysis
Write-Host "🚀 Starting job analysis for: $JobFile" -ForegroundColor Cyan
python 01-job-description-analysis.py @args

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Analysis completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Analysis failed with exit code: $LASTEXITCODE" -ForegroundColor Red
} 