# 00-MCP Server Setup Script (PowerShell)
# This script initializes three new MCP servers with blank configurations.
# You can modify the server details below and run this script to add them to your mcp-config.json.

param(
    [switch]$DryRun = $false
)

function Load-MCPConfig {
    """Load the existing MCP configuration."""
    $configPath = "mcp-config.json"
    if (Test-Path $configPath) {
        $content = Get-Content $configPath -Raw | ConvertFrom-Json
        return $content
    } else {
        return @{
            mcpServers = @{}
        }
    }
}

function Save-MCPConfig {
    param($Config)
    """Save the MCP configuration to file."""
    $Config | ConvertTo-Json -Depth 10 | Set-Content "mcp-config.json"
}

function Add-NewServers {
    """Add three new MCP servers with blank configurations."""
    
    # Define three new MCP servers with blank configurations
    # TODO: Fill in the actual server details you want to add
    $newServers = @{
        "server-1" = @{
            command = ""  # TODO: Add command (e.g., "npx", "python", etc.)
            args = @(
                # TODO: Add arguments for the server
                # Example: "-y", "@package/server-name"
            )
            env = @{
                # TODO: Add environment variables if needed
                # Example: "API_KEY" = "`${API_KEY}"
            }
        }
        "server-2" = @{
            command = ""  # TODO: Add command
            args = @(
                # TODO: Add arguments for the server
            )
            env = @{
                # TODO: Add environment variables if needed
            }
        }
        "server-3" = @{
            command = ""  # TODO: Add command
            args = @(
                # TODO: Add arguments for the server
            )
            env = @{
                # TODO: Add environment variables if needed
            }
        }
    }
    
    # Load existing configuration
    $config = Load-MCPConfig
    
    if ($DryRun) {
        Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
        Write-Host ""
    }
    
    # Add new servers to the configuration
    foreach ($serverName in $newServers.Keys) {
        if (-not $config.mcpServers.PSObject.Properties.Name -contains $serverName) {
            if (-not $DryRun) {
                $config.mcpServers | Add-Member -MemberType NoteProperty -Name $serverName -Value $newServers[$serverName]
            }
            Write-Host "✓ Added $serverName to MCP configuration" -ForegroundColor Green
        } else {
            Write-Host "⚠ $serverName already exists in configuration, skipping..." -ForegroundColor Yellow
        }
    }
    
    # Save the updated configuration
    if (-not $DryRun) {
        Save-MCPConfig $config
        Write-Host ""
        Write-Host "✓ MCP configuration updated successfully!" -ForegroundColor Green
        Write-Host "📝 Please edit the server configurations in mcp-config.json to add the actual server details." -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "🔍 DRY RUN: Configuration would be updated (use without -DryRun to apply changes)" -ForegroundColor Yellow
    }
}

function Create-DataDirectories {
    """Create necessary data directories for MCP servers."""
    $directories = @(
        "mcp-data",
        "mcp-data/memory-bank",
        "mcp-data/logs"
    )
    
    foreach ($directory in $directories) {
        if (-not (Test-Path $directory)) {
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path $directory -Force | Out-Null
            }
            Write-Host "✓ Created directory: $directory" -ForegroundColor Green
        } else {
            Write-Host "✓ Directory already exists: $directory" -ForegroundColor Gray
        }
    }
}

function Main {
    """Main setup function."""
    Write-Host "🚀 MCP Server Setup Script" -ForegroundColor Cyan
    Write-Host "=" * 40 -ForegroundColor Cyan
    
    if ($DryRun) {
        Write-Host "🔍 Running in DRY RUN mode - no changes will be made" -ForegroundColor Yellow
        Write-Host ""
    }
    
    # Create necessary directories
    Write-Host ""
    Write-Host "📁 Creating data directories..." -ForegroundColor Cyan
    Create-DataDirectories
    
    # Add new servers
    Write-Host ""
    Write-Host "🔧 Adding new MCP servers..." -ForegroundColor Cyan
    Add-NewServers
    
    Write-Host ""
    Write-Host "=" * 40 -ForegroundColor Cyan
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Edit mcp-config.json to fill in the server details"
    Write-Host "2. Update your .env file with any required API keys"
    Write-Host "3. Test the servers by running your application"
    Write-Host ""
    Write-Host "Example server configuration:" -ForegroundColor Cyan
    Write-Host @"
    "my-server": {
        "command": "npx",
        "args": ["-y", "@package/my-server"],
        "env": {
            "API_KEY": "`${MY_API_KEY}"
        }
    }
"@ -ForegroundColor Gray
    
    if ($DryRun) {
        Write-Host ""
        Write-Host "To apply these changes, run the script without the -DryRun parameter:" -ForegroundColor Yellow
        Write-Host ".\00-MCP-Server-Setup.ps1" -ForegroundColor White
    }
}

# Run the main function
Main 