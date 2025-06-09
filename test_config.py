#!/usr/bin/env python3
"""
Test script to verify the configuration manager loads environment variables correctly.
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from config_manager import ConfigManager, load_config

def test_environment_loading():
    """Test that environment variables are loaded from .env file."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Check that required environment variables are set
    assert 'ANTHROPIC_API_KEY' in os.environ, "ANTHROPIC_API_KEY not found in environment"
    assert 'OPENAI_API_KEY' in os.environ, "OPENAI_API_KEY not found in environment"
    
    print("[OK] Environment variables loaded successfully")

def test_config_manager_loading():
    """Test that the config manager loads configuration correctly."""
    # Initialize config manager
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Check that the config object is created
    assert config is not None, "Failed to load configuration"
    
    # Check that provider configurations are loaded
    assert hasattr(config, 'providers'), "Provider configurations not found"
    assert 'openai' in config.providers, "OpenAI provider not configured"
    assert 'anthropic' in config.providers, "Anthropic provider not configured"
    
    print("[OK] Config manager loaded successfully")

def test_api_key_loading():
    """Test that API keys can be retrieved from the config."""
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Get provider configs
    openai_config = config.get_provider_config('openai')
    anthropic_config = config.get_provider_config('anthropic')
    
    # Check that API keys are available
    assert openai_config.api_key, "OpenAI API key not found"
    assert anthropic_config.api_key, "Anthropic API key not found"
    
    print("[OK] API keys loaded successfully")

if __name__ == "__main__":
    print("=== Testing configuration ===")
    
    try:
        test_environment_loading()
        test_config_manager_loading()
        test_api_key_loading()
        print("\n[PASS] All configuration tests passed!")
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        exit(1)
