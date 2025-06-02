#!/usr/bin/env pwsh
# PowerShell script to set up MCP servers and data directories

param(
    [switch]$SkipInstall,
    [switch]$Verbose
)

Write-Host "🚀 Setting up MCP servers for Resume Velvit Thunder..." -ForegroundColor Cyan

# Create MCP data directories
Write-Host "`n📁 Creating MCP data directories..." -ForegroundColor Yellow
$mcpDataDir = "./mcp-data"
$memoryBankDir = "./mcp-data/memory-bank"

if (-not (Test-Path $mcpDataDir)) {
    New-Item -ItemType Directory -Path $mcpDataDir -Force | Out-Null
    Write-Host "✅ Created: $mcpDataDir" -ForegroundColor Green
} else {
    Write-Host "✅ Already exists: $mcpDataDir" -ForegroundColor Green
}

if (-not (Test-Path $memoryBankDir)) {
    New-Item -ItemType Directory -Path $memoryBankDir -Force | Out-Null
    Write-Host "✅ Created: $memoryBankDir" -ForegroundColor Green
} else {
    Write-Host "✅ Already exists: $memoryBankDir" -ForegroundColor Green
}

# Initialize memory file if it doesn't exist
$memoryFile = "./mcp-data/memory.json"
if (-not (Test-Path $memoryFile)) {
    '{}' | Out-File -FilePath $memoryFile -Encoding UTF8
    Write-Host "✅ Created: $memoryFile" -ForegroundColor Green
} else {
    Write-Host "✅ Already exists: $memoryFile" -ForegroundColor Green
}

# Check if Node.js is installed
Write-Host "`n🔍 Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if npx is available
try {
    $npxVersion = npx --version
    Write-Host "✅ npx found: $npxVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npx not found. Please ensure Node.js is properly installed." -ForegroundColor Red
    exit 1
}

if (-not $SkipInstall) {
    Write-Host "`n📦 Pre-installing MCP servers (this may take a few minutes)..." -ForegroundColor Yellow
    
    $servers = @(
        "@modelcontextprotocol/server-memory",
        "@modelcontextprotocol/server-sequential-thinking", 
        "task-master-ai",
        "@allpepper/mcp-perplexity-ask",
        "@allpepper/mcp-memory-bank",
        "@context7/mcp-server",
        "@modelcontextprotocol/server-puppeteer",
        "@executeautomation/playwright-mcp-server"
    )
    
    foreach ($server in $servers) {
        Write-Host "Installing $server..." -ForegroundColor Cyan
        try {
            if ($Verbose) {
                npx -y $server --help 2>$null | Out-Null
            } else {
                npx -y $server --help 2>$null | Out-Null
            }
            Write-Host "✅ $server installed successfully" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Warning: Could not pre-install $server (will install on first use)" -ForegroundColor Yellow
        }
    }
}

# Check environment file
Write-Host "`n🔧 Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Copy env.example to .env and configure your API keys:" -ForegroundColor Yellow
    Write-Host "   cp env.example .env" -ForegroundColor Cyan
}

# Display configuration instructions
Write-Host "`n📋 MCP Configuration Complete!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy env.example to .env: " -NoNewline -ForegroundColor White
Write-Host "cp env.example .env" -ForegroundColor Yellow
Write-Host "2. Edit .env with your API keys" -ForegroundColor White
Write-Host "3. Use mcp-config.json in your Claude Desktop settings" -ForegroundColor White
Write-Host ""
Write-Host "MCP Config file location: " -NoNewline -ForegroundColor White
Write-Host "$(Resolve-Path './mcp-config.json')" -ForegroundColor Yellow
Write-Host ""
Write-Host "Available MCP servers:" -ForegroundColor Cyan
Write-Host "• memory - Persistent memory storage" -ForegroundColor White
Write-Host "• sequential-thinking - Advanced reasoning" -ForegroundColor White  
Write-Host "• taskmaster-ai - Project task management" -ForegroundColor White
Write-Host "• perplexity-ask - Web search and research" -ForegroundColor White
Write-Host "• memory-bank - Project memory management" -ForegroundColor White
Write-Host "• context7 - Library documentation" -ForegroundColor White
Write-Host "• puppeteer - Web automation" -ForegroundColor White
Write-Host "• playwright - Advanced web automation" -ForegroundColor White
Write-Host "=" * 60 