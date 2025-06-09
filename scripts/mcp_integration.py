#!/usr/bin/env python3
"""
MCP Server Integration for Project Audit

This module provides integration with MCP (Model Context Protocol) servers
for enhanced project analysis.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """Class to interact with MCP servers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize MCP server with configuration."""
        self.name = config.get('name', 'unknown')
        self.url = config.get('url', '').rstrip('/')
        self.api_key = config.get('api_key', '')
        self.enabled = config.get('enabled', True)
        self.timeout = config.get('timeout', 30)
        
        # Validate configuration
        if not self.url:
            logger.warning(f"MCP server '{self.name}' has no URL configured and will be disabled.")
            self.enabled = False
    
    def is_available(self) -> bool:
        """Check if the MCP server is available."""
        if not self.enabled:
            return False
            
        try:
            response = requests.get(
                f"{self.url}/health",
                timeout=5,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"MCP server '{self.name}' health check failed: {e}")
            return False
    
    def analyze_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code quality using MCP server."""
        return self._make_request("/analyze/code-quality", {
            'code': code,
            'language': language
        })
    
    def detect_duplicates(self, file_hashes: Dict[str, str]) -> Dict[str, List[str]]:
        """Detect duplicate files using MCP server."""
        return self._make_request("/analyze/duplicates", {
            'file_hashes': file_hashes
        })
    
    def analyze_dependencies(self, dependencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze project dependencies using MCP server."""
        return self._make_request("/analyze/dependencies", {
            'dependencies': dependencies
        })
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the MCP server."""
        if not self.enabled:
            return {'error': 'MCP server is disabled'}
            
        url = f"{self.url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP server request failed: {e}")
            return {'error': str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP server response: {e}")
            return {'error': 'Invalid JSON response from MCP server'}

class MCPService:
    """Service class for MCP server integration."""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """Initialize MCP service with configuration."""
        self.servers: Dict[str, MCPServer] = {}
        self._load_config(config_file)
    
    def _load_config(self, config_file: Optional[Union[str, Path]] = None) -> None:
        """Load MCP server configuration from file or environment."""
        # Default config file path
        if config_file is None:
            config_file = Path(os.environ.get(
                'MCP_CONFIG_FILE',
                Path(__file__).parent.parent / 'mcp-config.json'
            ))
        
        # Load from file if exists
        config = {}
        if isinstance(config_file, (str, Path)) and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded MCP configuration from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load MCP config from {config_file}: {e}")
        else:
            # Try to load from environment
            config = self._load_config_from_env()
        
        # Initialize servers
        for name, server_config in config.get('servers', {}).items():
            self.servers[name] = MCPServer({
                'name': name,
                **server_config
            })
    
    def _load_config_from_env(self) -> Dict[str, Any]:
        """Load MCP server configuration from environment variables."""
        config = {'servers': {}}
        
        # Example: MCP_SERVERS=server1,server2
        server_names = os.environ.get('MCP_SERVERS', '').split(',')
        
        for server_name in server_names:
            server_name = server_name.strip()
            if not server_name:
                continue
                
            # Example: MCP_SERVER_SERVER1_URL, MCP_SERVER_SERVER1_API_KEY
            prefix = f"MCP_SERVER_{server_name.upper()}"
            url = os.environ.get(f"{prefix}_URL")
            api_key = os.environ.get(f"{prefix}_API_KEY")
            
            if url:
                config['servers'][server_name] = {
                    'url': url,
                    'api_key': api_key,
                    'enabled': os.environ.get(f"{prefix}_ENABLED", "true").lower() == 'true'
                }
        
        return config
    
    def get_available_servers(self) -> Dict[str, MCPServer]:
        """Get all available MCP servers."""
        return {name: server for name, server in self.servers.items() 
                if server.enabled and server.is_available()}
    
    def analyze_project(self, project_path: Union[str, Path]) -> Dict[str, Any]:
        """Analyze a project using available MCP servers."""
        results = {}
        
        for name, server in self.get_available_servers().items():
            try:
                logger.info(f"Analyzing project with {name}...")
                
                # Example analysis - can be expanded based on server capabilities
                if 'code-quality' in server.url:
                    results[name] = {
                        'code_quality': self._analyze_code_quality(server, project_path)
                    }
                elif 'duplicates' in server.url:
                    results[name] = {
                        'duplicates': self._analyze_duplicates(server, project_path)
                    }
                else:
                    logger.warning(f"Unknown MCP server type: {name}")
                    
            except Exception as e:
                logger.error(f"Error analyzing with {name}: {e}")
                results[name] = {'error': str(e)}
        
        return results
    
    def _analyze_code_quality(self, server: MCPServer, project_path: Path) -> Dict[str, Any]:
        """Analyze code quality using MCP server."""
        # This is a simplified example - in a real implementation, you would
        # scan the project for source files and send them for analysis
        source_files = list(project_path.rglob('*.py'))  # Example: Python files
        
        results = {}
        for file_path in source_files[:10]:  # Limit number of files for demo
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                    
                analysis = server.analyze_code_quality(
                    code=code,
                    language='python'  # Should be detected from file extension
                )
                results[str(file_path.relative_to(project_path))] = analysis
                
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        return results
    
    def _analyze_duplicates(self, server: MCPServer, project_path: Path) -> Dict[str, Any]:
        """Analyze file duplicates using MCP server."""
        # This is a simplified example - in a real implementation, you would
        # calculate file hashes and send them for analysis
        file_hashes = {}
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and file_path.stat().st_size < 10 * 1024 * 1024:  # Skip large files
                file_hashes[str(file_path.relative_to(project_path))] = self._calculate_file_hash(file_path)
        
        return server.detect_duplicates(file_hashes)
    
    @staticmethod
    def _calculate_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of a file."""
        import hashlib
        
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, PermissionError) as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return ""

def analyze_with_mcp(project_path: Union[str, Path], 
                    config_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Convenience function to analyze a project with MCP servers."""
    service = MCPService(config_file)
    return service.analyze_project(Path(project_path))

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze project with MCP servers')
    parser.add_argument('project_path', help='Path to the project directory')
    parser.add_argument('--config', '-c', help='Path to MCP config file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Analyze project
    results = analyze_with_mcp(args.project_path, args.config)
    
    # Print results
    print("\n=== MCP Analysis Results ===\n")
    for server_name, analysis in results.items():
        print(f"{server_name}:")
        print(json.dumps(analysis, indent=2))
        print("\n" + "-"*50 + "\n")
