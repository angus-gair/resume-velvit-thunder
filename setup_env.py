#!/usr/bin/env python3
"""
Interactive script to set up environment variables for the Resume Velvit Thunder project.
This script helps users configure their .env file with the required API keys.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

def get_input(prompt: str, default: str = "", is_password: bool = False) -> str:
    """Get user input with a default value and optional password masking."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if is_password:
        import getpass
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value.strip() else default

def setup_environment() -> Dict[str, str]:
    """Interactively collect environment variables from the user."""
    print("\n=== Resume Velvit Thunder - Environment Setup ===\n")
    print("Please enter your API keys and configuration. Press Enter to use default values.\n")
    
    # Core API Keys
    print("\n=== API Keys ===")
    env_vars = {
        'ANTHROPIC_API_KEY': get_input("Anthropic API Key", is_password=True),
        'OPENAI_API_KEY': get_input("OpenAI API Key", is_password=True),
        'PERPLEXITY_API_KEY': get_input("Perplexity API Key (optional)", is_password=True),
        'GOOGLE_API_KEY': get_input("Google API Key (optional)", is_password=True),
        'MISTRAL_API_KEY': get_input("Mistral API Key (optional)", is_password=True),
    }
    
    # Optional Configuration
    print("\n=== Optional Configuration ===")
    env_vars.update({
        'JOB_ANALYSIS_OUTPUT_DIR': get_input("Job analysis output directory", "./applications"),
        'CLAUDE_MODEL': get_input("Default Claude model", "claude-3-5-sonnet-20241022"),
        'MEMORY_FILE_PATH': get_input("Memory file path", "./mcp-data/memory.json"),
        'MEMORY_BANK_PATH': get_input("Memory bank path", "./mcp-data/memory-bank"),
        'DEFAULT_PROVIDER': get_input("Default provider", "openai"),
        'DEFAULT_MODEL': get_input("Default model", "gpt-4-turbo-preview"),
        'API_TIMEOUT': get_input("API timeout (seconds)", "60"),
        'MAX_RETRIES': get_input("Max retries", "3"),
        'RETRY_DELAY': get_input("Retry delay (seconds)", "1.0"),
        'DEBUG_MODE': get_input("Enable debug mode (true/false)", "false"),
        'LOG_LEVEL': get_input("Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", "INFO"),
    })
    
    return env_vars

def write_env_file(env_vars: Dict[str, str], env_path: Path) -> None:
    """Write environment variables to a .env file."""
    with open(env_path, 'w') as f:
        f.write("# Core API Keys for Job Analysis\n")
        f.write(f"ANTHROPIC_API_KEY={env_vars['ANTHROPIC_API_KEY']}\n\n")
        
        f.write("# Optional: Job Analysis Configuration\n")
        f.write(f"JOB_ANALYSIS_OUTPUT_DIR={env_vars['JOB_ANALYSIS_OUTPUT_DIR']}\n")
        f.write(f"CLAUDE_MODEL={env_vars['CLAUDE_MODEL']}\n\n")
        
        f.write("# MCP Server API Keys\n")
        f.write(f"OPENAI_API_KEY={env_vars['OPENAI_API_KEY']}\n")
        f.write(f"PERPLEXITY_API_KEY={env_vars['PERPLEXITY_API_KEY']}\n")
        f.write(f"GOOGLE_API_KEY={env_vars['GOOGLE_API_KEY']}\n")
        f.write(f"MISTRAL_API_KEY={env_vars['MISTRAL_API_KEY']}\n\n")
        
        f.write("# MCP Data Paths\n")
        f.write(f"MEMORY_FILE_PATH={env_vars['MEMORY_FILE_PATH']}\n")
        f.write(f"MEMORY_BANK_PATH={env_vars['MEMORY_BANK_PATH']}\n\n")
        
        f.write("# Application Settings\n")
        f.write(f"DEFAULT_PROVIDER={env_vars['DEFAULT_PROVIDER']}\n")
        f.write(f"DEFAULT_MODEL={env_vars['DEFAULT_MODEL']}\n")
        f.write(f"API_TIMEOUT={env_vars['API_TIMEOUT']}\n")
        f.write(f"MAX_RETRIES={env_vars['MAX_RETRIES']}\n")
        f.write(f"RETRY_DELAY={env_vars['RETRY_DELAY']}\n")
        f.write(f"DEBUG_MODE={env_vars['DEBUG_MODE']}\n")
        f.write(f"LOG_LEVEL={env_vars['LOG_LEVEL']}\n")

def main():
    """Main function to run the environment setup."""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent
        env_path = project_root / '.env'
        
        # Check if .env already exists
        if env_path.exists():
            print(f"\n⚠️  WARNING: {env_path} already exists.")
            overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Setup cancelled. No changes were made.")
                return
        
        # Collect environment variables
        env_vars = setup_environment()
        
        # Write to .env file
        write_env_file(env_vars, env_path)
        print(f"\n✅ Successfully created/updated {env_path}")
        print("\nSetup complete! You can now run the application.")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
