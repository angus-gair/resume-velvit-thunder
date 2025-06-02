#!/usr/bin/env python3
"""
00-MCP Server Setup Script
This script initializes three new MCP servers with blank configurations.
You can modify the server details below and run this script to add them to your mcp-config.json.
"""

import json
import os
from pathlib import Path

def load_mcp_config():
    """Load the existing MCP configuration."""
    config_path = Path("mcp-config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return {"mcpServers": {}}

def save_mcp_config(config):
    """Save the MCP configuration to file."""
    with open("mcp-config.json", 'w') as f:
        json.dump(config, f, indent=2)

def add_new_servers():
    """Add three new MCP servers with blank configurations."""
    
    # Define three new MCP servers with blank configurations
    # TODO: Fill in the actual server details you want to add
    new_servers = {
        "server-1": {
            "command": "",  # TODO: Add command (e.g., "npx", "python", etc.)
            "args": [
                # TODO: Add arguments for the server
                # Example: "-y", "@package/server-name"
            ],
            "env": {
                # TODO: Add environment variables if needed
                # Example: "API_KEY": "${API_KEY}"
            }
        },
        "server-2": {
            "command": "",  # TODO: Add command
            "args": [
                # TODO: Add arguments for the server
            ],
            "env": {
                # TODO: Add environment variables if needed
            }
        },
        "server-3": {
            "command": "",  # TODO: Add command
            "args": [
                # TODO: Add arguments for the server
            ],
            "env": {
                # TODO: Add environment variables if needed
            }
        }
    }
    
    # Load existing configuration
    config = load_mcp_config()
    
    # Add new servers to the configuration
    for server_name, server_config in new_servers.items():
        if server_name not in config["mcpServers"]:
            config["mcpServers"][server_name] = server_config
            print(f"✓ Added {server_name} to MCP configuration")
        else:
            print(f"⚠ {server_name} already exists in configuration, skipping...")
    
    # Save the updated configuration
    save_mcp_config(config)
    print("\n✓ MCP configuration updated successfully!")
    print("📝 Please edit the server configurations in mcp-config.json to add the actual server details.")

def create_data_directories():
    """Create necessary data directories for MCP servers."""
    directories = [
        "mcp-data",
        "mcp-data/memory-bank",
        "mcp-data/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def main():
    """Main setup function."""
    print("🚀 MCP Server Setup Script")
    print("=" * 40)
    
    # Create necessary directories
    print("\n📁 Creating data directories...")
    create_data_directories()
    
    # Add new servers
    print("\n🔧 Adding new MCP servers...")
    add_new_servers()
    
    print("\n" + "=" * 40)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit mcp-config.json to fill in the server details")
    print("2. Update your .env file with any required API keys")
    print("3. Test the servers by running your application")
    print("\nExample server configuration:")
    print("""
    "my-server": {
        "command": "npx",
        "args": ["-y", "@package/my-server"],
        "env": {
            "API_KEY": "${MY_API_KEY}"
        }
    }
    """)

if __name__ == "__main__":
    main() 