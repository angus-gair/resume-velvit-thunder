#!/usr/bin/env python3
"""
Tests for MCP server configuration in the Resume Velvit Thunder project.
"""

import os
import sys
import json
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import (
    ConfigManager, 
    ResumeConfig, 
    ProviderConfig,
    MCPServerConfig
)

class TestMCPServerConfig(unittest.TestCase):
    """Test MCP server configuration."""
    
    def test_mcp_server_config_creation(self):
        """Test creating an MCP server config."""
        config = MCPServerConfig(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-memory"],
            env={"MEMORY_FILE_PATH": "./mcp-data/memory.json"},
            enabled=True,
            port=8000
        )
        
        self.assertEqual(config.command, "npx")
        self.assertEqual(config.args, ["-y", "@modelcontextprotocol/server-memory"])
        self.assertEqual(config.env, {"MEMORY_FILE_PATH": "./mcp-data/memory.json"})
        self.assertTrue(config.enabled)
        self.assertEqual(config.port, 8000)
    
    def test_mcp_server_validation(self):
        """Test MCP server config validation."""
        # Valid config
        valid_config = MCPServerConfig(
            command="npx",
            args=["-y", "test-server"]
        )
        self.assertEqual(valid_config.validate(), [])
        
        # Invalid config - missing command
        invalid_config = MCPServerConfig(
            command="",
            args=["-y", "test-server"]
        )
        self.assertIn("MCP server command is required", invalid_config.validate())
        
        # Invalid config - missing args
        invalid_config = MCPServerConfig(
            command="npx",
            args=[]
        )
        self.assertIn("MCP server args cannot be empty", invalid_config.validate())


class TestMCPIntegration(unittest.TestCase):
    """Test MCP server integration with ConfigManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigManager()
        self.test_config = {
            "mcp_servers": {
                "test-server": {
                    "command": "npx",
                    "args": ["-y", "test-server"],
                    "env": {"TEST": "value"},
                    "enabled": True,
                    "port": 8000
                }
            },
            "providers": {
                "test-provider": {
                    "models": ["model1", "model2"],
                    "default_model": "model1",
                    "mcp_server": "test-server"
                }
            }
        }
    
    def test_load_mcp_servers_from_dict(self):
        """Test loading MCP servers from a dictionary."""
        config = self.config_manager._dict_to_config(self.test_config)
        
        # Check MCP servers
        self.assertIn("test-server", config.mcp_servers)
        server = config.mcp_servers["test-server"]
        self.assertIsInstance(server, MCPServerConfig)
        self.assertEqual(server.command, "npx")
        self.assertEqual(server.args, ["-y", "test-server"])
        self.assertEqual(server.env, {"TEST": "value"})
        self.assertTrue(server.enabled)
        self.assertEqual(server.port, 8000)
        
        # Check provider MCP server reference
        self.assertIn("test-provider", config.providers)
        provider = config.providers["test-provider"]
        self.assertEqual(provider.mcp_server, "test-server")
    
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_load_mcp_servers_from_file(self, mock_open, mock_exists):
        """Test loading MCP servers from a config file."""
        # Mock file operations
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = json.dumps({
            "mcpServers": {
                "memory": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-memory"],
                    "env": {"MEMORY_FILE_PATH": "./mcp-data/memory.json"}
                }
            }
        })
        mock_open.return_value = mock_file
        
        # Test loading
        config = self.config_manager._load_mcp_servers("mcp-config.json")
        
        # Verify
        mock_open.assert_called_once()
        self.assertIn("memory", config)
        self.assertEqual(config["memory"].command, "npx")
        self.assertEqual(config["memory"].args, ["-y", "@modelcontextprotocol/server-memory"])
        self.assertEqual(config["memory"].env, {"MEMORY_FILE_PATH": "./mcp-data/memory.json"})
    
    @patch('os.path.exists')
    def test_load_mcp_servers_file_not_found(self, mock_exists):
        """Test handling of missing MCP config file."""
        mock_exists.return_value = False
        
        # Should not raise an exception
        config = self.config_manager._load_mcp_servers("nonexistent.json")
        self.assertEqual(config, {})


class TestEnvironmentVariableExpansion(unittest.TestCase):
    """Test environment variable expansion in MCP config."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_manager = ConfigManager()
        os.environ["TEST_VAR"] = "test_value"
        os.environ["TEST_PORT"] = "8080"
    
    def test_expand_environment_variables(self):
        """Test expanding environment variables in MCP config."""
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "npx",
                    "args": ["-y", "test-server", "--port", "${TEST_PORT}"],
                    "env": {"TEST": "${TEST_VAR}"},
                    "port": "${TEST_PORT}"
                }
            }
        }
        
        # Mock file operations
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            mock_file.return_value.read.return_value = json.dumps(test_config)
            
            # Test loading
            config = self.config_manager._load_mcp_servers("mcp-config.json")
            
            # Verify environment variables are expanded
            self.assertIn("test-server", config)
            server = config["test-server"]
            self.assertEqual(server.args, ["-y", "test-server", "--port", "8080"])
            self.assertEqual(server.env, {"TEST": "test_value"})
            self.assertEqual(server.port, 8080)  # Should be converted to int
    
    def test_nested_environment_variables(self):
        """Test expanding nested environment variables."""
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "npx",
                    "args": ["-y", "test-server"],
                    "env": {
                        "NESTED": {
                            "KEY1": "${TEST_VAR}",
                            "KEY2": "value_${TEST_VAR}"
                        }
                    }
                }
            }
        }
        
        # Mock file operations
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            mock_file.return_value.read.return_value = json.dumps(test_config)
            
            # Test loading
            config = self.config_manager._load_mcp_servers("mcp-config.json")
            
            # Verify nested environment variables are expanded
            self.assertEqual(
                config["test-server"].env,
                {"NESTED": {"KEY1": "test_value", "KEY2": "value_test_value"}}
            )


if __name__ == "__main__":
    unittest.main()
