#!/usr/bin/env python3
"""
Initialize allpepper-memory-bank MCP Server
This script initializes the memory bank server and creates a test project structure.
"""

import json
import os
from pathlib import Path

def check_memory_bank_setup():
    """Check if memory bank is properly configured."""
    print("🔍 Checking allpepper-memory-bank setup...")
    
    # Check if mcp-config.json exists and has memory-bank configured
    config_path = Path("mcp-config.json")
    if not config_path.exists():
        print("❌ mcp-config.json not found!")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if "memory-bank" not in config.get("mcpServers", {}):
        print("❌ memory-bank server not found in mcp-config.json!")
        return False
    
    memory_bank_config = config["mcpServers"]["memory-bank"]
    print("✅ memory-bank server found in configuration:")
    print(f"   Command: {memory_bank_config.get('command', 'N/A')}")
    print(f"   Package: {' '.join(memory_bank_config.get('args', []))}")
    print(f"   Path: {memory_bank_config.get('env', {}).get('MEMORY_BANK_PATH', 'N/A')}")
    
    return True

def create_memory_bank_structure():
    """Create the memory bank directory structure."""
    print("\n📁 Setting up memory bank directory structure...")
    
    memory_bank_path = Path("mcp-data/memory-bank")
    memory_bank_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created/verified directory: {memory_bank_path}")
    
    # Create a sample project structure
    sample_project = memory_bank_path / "resume-project"
    sample_project.mkdir(exist_ok=True)
    print(f"✅ Created sample project directory: {sample_project}")
    
    # Create a sample memory file
    sample_memory = sample_project / "project-overview.md"
    sample_content = """# Resume Project Memory Bank

## Project Overview
This is a memory bank for the resume analysis project.

## Key Information
- Project Type: Resume Analysis Tool
- Language: Python
- Purpose: Analyze job descriptions and match with resumes

## Notes
- Add your project-specific notes here
- This file will be accessible through the MCP memory bank server
"""
    
    with open(sample_memory, 'w') as f:
        f.write(sample_content)
    print(f"✅ Created sample memory file: {sample_memory}")
    
    # Create a .gitkeep file to ensure the directory is tracked
    gitkeep = memory_bank_path / ".gitkeep"
    gitkeep.touch()
    print(f"✅ Created .gitkeep file")

def display_usage_instructions():
    """Display instructions for using the memory bank."""
    print("\n📚 How to use allpepper-memory-bank:")
    print("=" * 50)
    print("\n1. The memory bank is now initialized at: ./mcp-data/memory-bank")
    print("\n2. Available MCP tools for memory bank:")
    print("   - mcp_allpepper-memory-bank_list_projects")
    print("   - mcp_allpepper-memory-bank_list_project_files")
    print("   - mcp_allpepper-memory-bank_memory_bank_read")
    print("   - mcp_allpepper-memory-bank_memory_bank_write")
    print("   - mcp_allpepper-memory-bank_memory_bank_update")
    print("\n3. Project structure:")
    print("   mcp-data/memory-bank/")
    print("   └── [project-name]/")
    print("       └── [memory-files.md/.txt/.json]")
    print("\n4. Example usage in your AI assistant:")
    print("   - Create a new project: Create folder in mcp-data/memory-bank/")
    print("   - Write memory: Use memory_bank_write tool")
    print("   - Read memory: Use memory_bank_read tool")
    print("   - List projects: Use list_projects tool")

def main():
    """Main initialization function."""
    print("🚀 Initializing allpepper-memory-bank MCP Server")
    print("=" * 50)
    
    # Check configuration
    if not check_memory_bank_setup():
        print("\n❌ Setup failed! Please check your mcp-config.json")
        return
    
    # Create directory structure
    create_memory_bank_structure()
    
    # Display usage instructions
    display_usage_instructions()
    
    print("\n" + "=" * 50)
    print("✅ Memory bank initialization complete!")
    print("\n💡 Tip: Restart your MCP client (Cursor/Cline) to load the memory bank server.")

if __name__ == "__main__":
    main() 