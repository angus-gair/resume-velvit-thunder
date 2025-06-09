#!/usr/bin/env python3
"""
Configuration Manager for Resume Generation System
=================================================

This module provides a robust configuration management system that handles:
- Loading from multiple sources (files, environment variables)
- Validation of required parameters
- Provider-specific configurations
- Runtime configuration reloading
- Default value management

Author: AI Resume Builder
Version: 1.0.0
Date: December 2024
"""

import os
import json
import dataclasses
from dotenv import load_dotenv
try:
    import yaml
except ImportError:
    yaml = None
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict, fields, is_dataclass
from enum import Enum
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, TypeVar, Type, cast

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class ConfigSource(Enum):
    """Configuration source types."""
    FILE = "file"
    ENVIRONMENT = "environment"
    DEFAULT = "default"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    port: Optional[int] = None
    
    def validate(self) -> List[str]:
        """Validate MCP server configuration."""
        errors = []
        if not self.command:
            errors.append("MCP server command is required")
        if not self.args:
            errors.append("MCP server args cannot be empty")
        return errors
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'command': self.command,
            'args': self.args,
            'env': self.env,
            'enabled': self.enabled,
            'port': self.port
        }


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    models: List[str]
    default_model: str
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    api_key_env_var: str = ""
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    mcp_server: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate provider configuration."""
        errors = []
        
        if not self.models:
            errors.append("models list cannot be empty")
        
        if self.default_model not in self.models:
            errors.append(f"default_model '{self.default_model}' not in models list")
            
        if not 0 <= self.temperature <= 2:
            errors.append("temperature must be between 0 and 2")
            
        if self.max_tokens <= 0:
            errors.append("max_tokens must be positive")
            
        if self.timeout <= 0:
            errors.append("timeout must be positive")
            
        if self.max_retries < 0:
            errors.append("max_retries cannot be negative")
            
        if self.retry_delay < 0:
            errors.append("retry_delay cannot be negative")
            
        return errors


@dataclass
class ATSOptimizationConfig:
    """Configuration for ATS optimization."""
    keyword_density_min: float = 0.02
    keyword_density_max: float = 0.05
    min_match_score: float = 70.0
    min_ats_score: float = 80.0
    
    def validate(self) -> List[str]:
        """Validate ATS optimization configuration."""
        errors = []
        
        if not 0 <= self.keyword_density_min <= 1:
            errors.append("keyword_density_min must be between 0 and 1")
            
        if not 0 <= self.keyword_density_max <= 1:
            errors.append("keyword_density_max must be between 0 and 1")
            
        if self.keyword_density_min > self.keyword_density_max:
            errors.append("keyword_density_min cannot be greater than keyword_density_max")
            
        if not 0 <= self.min_match_score <= 100:
            errors.append("min_match_score must be between 0 and 100")
            
        if not 0 <= self.min_ats_score <= 100:
            errors.append("min_ats_score must be between 0 and 100")
            
        return errors


@dataclass
class GenerationLimitsConfig:
    """Configuration for generation limits."""
    max_api_calls_per_resume: int = 10
    max_generation_time: int = 120
    max_word_count: int = 1000
    min_word_count: int = 300
    
    def validate(self) -> List[str]:
        """Validate generation limits configuration."""
        errors = []
        
        if self.max_api_calls_per_resume <= 0:
            errors.append("max_api_calls_per_resume must be positive")
            
        if self.max_generation_time <= 0:
            errors.append("max_generation_time must be positive")
            
        if self.max_word_count <= 0:
            errors.append("max_word_count must be positive")
            
        if self.min_word_count <= 0:
            errors.append("min_word_count must be positive")
            
        if self.min_word_count > self.max_word_count:
            errors.append("min_word_count cannot be greater than max_word_count")
            
        return errors


@dataclass
class TemplateDefaultsConfig:
    """Configuration for template defaults."""
    font_family: str = "Arial, sans-serif"
    font_size: str = "11pt"
    line_height: str = "1.5"
    margin: str = "0.75in"
    
    def validate(self) -> List[str]:
        """Validate template defaults configuration."""
        errors = []
        
        if not self.font_family:
            errors.append("font_family cannot be empty")
            
        if not self.font_size:
            errors.append("font_size cannot be empty")
            
        if not self.line_height:
            errors.append("line_height cannot be empty")
            
        if not self.margin:
            errors.append("margin cannot be empty")
            
        return errors


@dataclass
class ResumeConfig:
    """Main configuration class for the resume generation system."""
    # Core settings
    database_path: str = "resume_builder.db"
    template_dir: str = "data/sample_docs"
    output_dir: str = "generated_resumes"
    default_provider: str = "openai"
    default_model: str = "gpt-4-turbo-preview"
    
    # API settings
    max_retries: int = 3
    retry_delay: float = 1.0
    request_timeout: int = 60
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Logging settings
    api_usage_tracking: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    preserve_logs: int = 30
    
    # Sub-configurations
    template_defaults: TemplateDefaultsConfig = field(default_factory=TemplateDefaultsConfig)
    ats_optimization: ATSOptimizationConfig = field(default_factory=ATSOptimizationConfig)
    generation_limits: GenerationLimitsConfig = field(default_factory=GenerationLimitsConfig)
    mcp_servers: Dict[str, MCPServerConfig] = field(default_factory=dict)
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default providers if not provided."""
        if not self.providers:
            self.providers = self._get_default_providers()
    
    def _get_default_providers(self) -> Dict[str, ProviderConfig]:
        """Get default provider configurations."""
        return {
            "openai": ProviderConfig(
                models=["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
                default_model="gpt-4-turbo-preview",
                api_key_env_var="OPENAI_API_KEY"
            ),
            "anthropic": ProviderConfig(
                models=["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                default_model="claude-3-sonnet-20240229",
                api_key_env_var="ANTHROPIC_API_KEY"
            ),
            "perplexity": ProviderConfig(
                models=["pplx-7b-online", "pplx-70b-online", "pplx-7b-chat", "pplx-70b-chat"],
                default_model="pplx-70b-online",
                api_key_env_var="PERPLEXITY_API_KEY"
            ),
            "google": ProviderConfig(
                models=["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
                default_model="gemini-1.5-pro",
                api_key_env_var="GOOGLE_API_KEY"
            ),
            "mistral": ProviderConfig(
                models=["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large-latest"],
                default_model="mistral-medium",
                api_key_env_var="MISTRAL_API_KEY"
            ),
            "opensource": ProviderConfig(
                models=["llama2", "codellama", "mistral"],
                default_model="llama2",
                endpoint="http://localhost:11434/api/generate"
            )
        }
    
    def validate(self) -> List[str]:
        """Validate the entire configuration."""
        errors = []
        
        # Validate core settings
        if not self.database_path:
            errors.append("database_path cannot be empty")
            
        if not self.template_dir:
            errors.append("template_dir cannot be empty")
            
        if not self.output_dir:
            errors.append("output_dir cannot be empty")
            
        if self.default_provider not in self.providers:
            errors.append(f"default_provider '{self.default_provider}' not found in providers")
            
        if not 0 <= self.temperature <= 2:
            errors.append("temperature must be between 0 and 2")
            
        if self.max_tokens <= 0:
            errors.append("max_tokens must be positive")
            
        if self.request_timeout <= 0:
            errors.append("request_timeout must be positive")
            
        if self.max_retries < 0:
            errors.append("max_retries cannot be negative")
            
        if self.retry_delay < 0:
            errors.append("retry_delay cannot be negative")
            
        if self.preserve_logs < 0:
            errors.append("preserve_logs cannot be negative")
            
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            errors.append("log_level must be a valid logging level")
        
        # Validate sub-configurations
        errors.extend(self.template_defaults.validate())
        errors.extend(self.ats_optimization.validate())
        errors.extend(self.generation_limits.validate())
        
        # Validate providers
        for provider_name, provider_config in self.providers.items():
            provider_errors = provider_config.validate()
            errors.extend([f"Provider '{provider_name}': {error}" for error in provider_errors])
        
        return errors
    
    def get_provider_config(self, provider_name: Optional[str] = None) -> ProviderConfig:
        """Get configuration for a specific provider."""
        provider_name = provider_name or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found in configuration")
            
        return self.providers[provider_name]
    
    def get_api_key(self, provider_name: Optional[str] = None) -> Optional[str]:
        """Get API key for a provider from environment variables."""
        provider_config = self.get_provider_config(provider_name)
        
        if provider_config.api_key_env_var:
            return os.getenv(provider_config.api_key_env_var)
        
        return None


class ConfigManager:
    """Manages configuration loading, validation, and reloading."""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        self.config_file = Path(config_file) if config_file else None
        self.config: Optional[ResumeConfig] = None
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, validate: bool = True) -> ResumeConfig:
        """
        Load configuration from all sources.
        
        Args:
            validate: Whether to validate the configuration
            
        Returns:
            Loaded and validated configuration
            
        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If config file doesn't exist
        """
        # Start with default configuration
        config_dict = asdict(ResumeConfig())
        
        # Load from file if specified
        if self.config_file and self.config_file.exists():
            file_config = self._load_from_file(self.config_file)
            config_dict = self._merge_configs(config_dict, file_config)
            self.logger.info(f"Loaded configuration from {self.config_file}")
        elif self.config_file:
            self.logger.warning(f"Configuration file {self.config_file} not found, using defaults")
        
        # Override with environment variables
        env_config = self._load_from_environment()
        config_dict = self._merge_configs(config_dict, env_config)
        
        # Convert to ResumeConfig object
        self.config = self._dict_to_config(config_dict)
        
        # Validate if requested
        if validate:
            errors = self.config.validate()
            if errors:
                error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
                raise ValueError(error_msg)
        
        self.logger.info("Configuration loaded and validated successfully")
        return self.config
    
    def reload_config(self) -> ResumeConfig:
        """Reload configuration from all sources."""
        self.logger.info("Reloading configuration")
        return self.load_config()
    
    def save_config(self, config: ResumeConfig, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            file_path: Path to save to (defaults to current config file)
        """
        save_path = Path(file_path) if file_path else self.config_file
        
        if not save_path:
            raise ValueError("No file path specified for saving configuration")
        
        config_dict = asdict(config)
        
        if save_path.suffix.lower() in ['.yaml', '.yml']:
            if yaml is None:
                raise ValueError("YAML support not available. Install PyYAML to save YAML config files.")
            with open(save_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        else:
            with open(save_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        
        self.logger.info(f"Configuration saved to {save_path}")
    
    def _load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from a file."""
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    if yaml is None:
                        raise ValueError("YAML support not available. Install PyYAML to use YAML config files.")
                    return yaml.safe_load(f) or {}
                else:
                    return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {file_path}: {e}")
    
    def _expand_environment_variables(self, value: Any, context: Optional[Dict[str, str]] = None) -> Any:
        """
        Recursively expand environment variables in a value.
        
        Args:
            value: The value to process (can be any type)
            context: Optional dictionary of additional variables to use for expansion
            
        Returns:
            The value with environment variables expanded
            
        Environment variables can be referenced in the format ${VARIABLE} or $VARIABLE.
        The ${VARIABLE:-default} syntax is also supported for providing default values.
        """
        if value is None:
            return None
            
        # Handle string values
        if isinstance(value, str):
            # First expand any environment variables in the string
            def replace_var(match):
                var_name = match.group(1) or match.group(2)
                
                # Handle default value syntax: ${VAR:-default}
                if ':-' in var_name:
                    var_name, default = var_name.split(':-', 1)
                    return os.getenv(var_name, default)
                    
                # Check context first, then environment
                if context and var_name in context:
                    return context[var_name]
                return os.getenv(var_name, '')
                
            # Replace ${VAR} or $VAR patterns
            value = re.sub(r'\${([^}]+)}|\$([A-Za-z_][A-Za-z0-9_]*)', replace_var, value)
            
            # Convert string booleans to actual booleans
            if value.lower() in ('true', 'yes', 'on'):
                return True
            elif value.lower() in ('false', 'no', 'off'):
                return False
                
            # Convert string numbers to appropriate numeric types
            if value.isdigit():
                return int(value)
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
                
            return value
            
        # Handle dictionaries
        elif isinstance(value, dict):
            return {k: self._expand_environment_variables(v, context) for k, v in value.items()}
            
        # Handle lists, tuples, and other iterables
        elif isinstance(value, (list, tuple, set)):
            return type(value)(self._expand_environment_variables(v, context) for v in value)
            
        return value

    def _load_mcp_servers(self, config_path: str) -> Dict[str, MCPServerConfig]:
        """
        Load MCP server configurations from the specified file or environment variables.
        
        This method loads MCP server configurations from a JSON or YAML file and optionally
        overrides them with environment variables. Environment variables should be prefixed
        with 'MCP_SERVER_<NAME>_' where <NAME> is the uppercase server name.
        
        Args:
            config_path: Path to the MCP config file (JSON or YAML)
            
        Returns:
            Dictionary of MCP server configurations with environment variables expanded
            
        Example environment variables:
            MCP_SERVER_MY_SERVER_COMMAND="python -m my_server"
            MCP_SERVER_MY_SERVER_PORT=8000
            MCP_SERVER_MY_SERVER_ENABLED=true
            MCP_SERVER_MY_SERVER_ENV_KEY=value
        """
        mcp_servers = {}
        
        try:
            # Try to load from file if it exists
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    if config_file.suffix.lower() in ['.yaml', '.yml']:
                        if yaml is None:
                            self.logger.warning("YAML support not available. Install PyYAML to use YAML config files.")
                        else:
                            config = yaml.safe_load(f) or {}
                    else:
                        config = json.load(f) or {}
                
                servers = config.get('mcpServers', {})
                
                for name, server_config in servers.items():
                    if not isinstance(server_config, dict):
                        self.logger.warning(f"Invalid MCP server config for {name}: expected dict, got {type(server_config)}")
                        continue
                        
                    # Expand environment variables in the server config
                    expanded_config = self._expand_environment_variables(server_config)
                    
                    # Create MCPServerConfig object
                    port = expanded_config.get('port')
                    if port is not None and isinstance(port, str):
                        if port.isdigit():
                            port = int(port)
                        else:
                            self.logger.warning(f"Invalid port value for MCP server {name}: {port}")
                            port = None
                    
                    mcp_servers[name] = MCPServerConfig(
                        command=expanded_config.get('command', '').strip(),
                        args=[str(arg) for arg in expanded_config.get('args', [])],
                        env=dict(expanded_config.get('env', {})),
                        enabled=bool(expanded_config.get('enabled', True)),
                        port=port
                    )
            
            # Apply environment variable overrides
            for env_key, env_value in os.environ.items():
                if not env_key.startswith('MCP_SERVER_'):
                    continue
                    
                # Parse the environment variable name
                parts = env_key.split('_', 3)  # Split into ['MCP', 'SERVER', 'NAME', 'FIELD']
                if len(parts) < 4:
                    continue
                    
                server_name = parts[2].lower()
                field_name = parts[3].lower()
                
                # Get or create the server config
                if server_name not in mcp_servers:
                    mcp_servers[server_name] = MCPServerConfig(command='')
                
                server = mcp_servers[server_name]
                
                # Apply the environment variable value
                try:
                    if field_name == 'command':
                        server.command = env_value.strip()
                    elif field_name == 'port':
                        if env_value.isdigit():
                            server.port = int(env_value)
                    elif field_name == 'enabled':
                        server.enabled = env_value.lower() in ('true', '1', 'yes', 'y')
                    elif field_name == 'args':
                        # Split command-line arguments respecting quotes
                        import shlex
                        server.args = shlex.split(env_value)
                    elif field_name.startswith('env_'):
                        # Handle environment variables for the server process
                        env_var_name = field_name[4:]  # Remove 'env_' prefix
                        if not hasattr(server, 'env'):
                            server.env = {}
                        server.env[env_var_name] = env_value
                except Exception as e:
                    self.logger.warning(f"Failed to set {env_key}: {e}")
            
            # Validate all server configurations
            valid_servers = {}
            for name, server in mcp_servers.items():
                try:
                    errors = server.validate()
                    if errors:
                        self.logger.warning(f"Invalid MCP server config for {name}: {', '.join(errors)}")
                        continue
                    valid_servers[name] = server
                except Exception as e:
                    self.logger.error(f"Error validating MCP server {name}: {e}")
            
            return valid_servers
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in MCP config file {config_path}: {e}")
        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML in MCP config file {config_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error loading MCP server config from {config_path}: {e}", exc_info=True)
            
        return mcp_servers
            
    def _load_from_environment(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.
        
        Returns:
            Dict containing configuration loaded from environment variables with all
            environment variables expanded.
            
        Environment variables take precedence over config file values and can be used
        to override any configuration setting. The following formats are supported:
        
        - General settings: SETTING_NAME=value
        - Provider settings: PROVIDER_NAME_SETTING=value (e.g., OPENAI_API_KEY=sk-...)
        - MCP server settings: MCP_SERVER_NAME_SETTING=value (e.g., MCP_SERVER_MY_SERVER_PORT=8000)
        
        Boolean values can be 'true'/'false', 'yes'/'no', '1'/'0' (case-insensitive).
        List values should be comma-separated.
        """
        env_config = {}
        
        # Get default provider configurations
        default_providers = ResumeConfig()._get_default_providers()
        
        # Initialize providers with default values
        env_config['providers'] = {}
        for provider_name, provider_config in default_providers.items():
            env_config['providers'][provider_name] = {
                'models': provider_config.models,
                'default_model': provider_config.default_model,
                'max_tokens': provider_config.max_tokens,
                'temperature': provider_config.temperature,
                'timeout': provider_config.timeout,
                'max_retries': provider_config.max_retries,
                'retry_delay': provider_config.retry_delay,
                'api_key_env_var': provider_config.api_key_env_var,
                'api_key': None,  # Will be set from environment if available
                'endpoint': provider_config.endpoint,
                'mcp_server': provider_config.mcp_server
            }
            
        # Load MCP server configurations from both file and environment variables
        mcp_config_file = os.getenv('MCP_CONFIG_FILE', 'mcp-config.json')
        env_config['mcp_servers'] = self._load_mcp_servers(mcp_config_file)
        env_config['mcp_config_file'] = mcp_config_file
        
        # Log MCP server status
        if env_config['mcp_servers']:
            self.logger.info(f"Loaded {len(env_config['mcp_servers'])} MCP server(s) from {mcp_config_file}")
            for name, server in env_config['mcp_servers'].items():
                status = "enabled" if server.enabled else "disabled"
                port_info = f"on port {server.port}" if server.port else "(no port specified)"
                self.logger.debug(f"MCP Server: {name} - {status} {port_info}")
        else:
            self.logger.info("No MCP servers configured")
        
        # Map environment variables to config structure with type information
        env_mapping = {
            # API Keys
            'ANTHROPIC_API_KEY': (['providers', 'anthropic', 'api_key'], str),
            'OPENAI_API_KEY': (['providers', 'openai', 'api_key'], str),
            'PERPLEXITY_API_KEY': (['providers', 'perplexity', 'api_key'], str),
            'GOOGLE_API_KEY': (['providers', 'google', 'api_key'], str),
            'MISTRAL_API_KEY': (['providers', 'mistral', 'api_key'], str),
            
            # Model names - update default model and ensure it's in the models list
            'CLAUDE_MODEL': (['providers', 'anthropic', 'default_model'], str),
            'OPENAI_MODEL': (['providers', 'openai', 'default_model'], str),
            
            # Core settings
            'DEFAULT_PROVIDER': (['default_provider'], str),
            'DEFAULT_MODEL': (['default_model'], str),
            
            # Timeout and retry settings
            'API_TIMEOUT': (['request_timeout'], int),
            'MAX_RETRIES': (['max_retries'], int),
            'RETRY_DELAY': (['retry_delay'], float),
            
            # Debug and logging
            'DEBUG_MODE': (['debug_mode'], lambda x: str(x).lower() in ['true', '1', 'yes']),
            'LOG_LEVEL': (['log_level'], str)
        }
        
        # Process environment variables
        for env_var, (config_path, converter) in env_mapping.items():
            if value := os.getenv(env_var):
                try:
                    # Convert value to the appropriate type
                    converted_value = converter(value)
                    
                    # Navigate the config structure and set the value
                    current = env_config
                    for key in config_path[:-1]:
                        if key not in current:
                            current[key] = {}
                        current = current[key]
                    
                    # Special handling for default_model to ensure it's in the models list
                    if config_path[-1] == 'default_model' and 'providers' in config_path:
                        provider_name = config_path[1]  # Get provider name from path
                        if provider_name in env_config['providers']:
                            # Ensure the model is in the models list
                            models = env_config['providers'][provider_name].get('models', [])
                            if converted_value not in models:
                                # Add the model to the models list if it's not already there
                                models.append(converted_value)
                                env_config['providers'][provider_name]['models'] = models
                    
                    current[config_path[-1]] = converted_value
                    
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid value for {env_var}: {value} ({e})")
        
        return env_config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> ResumeConfig:
        """Convert dictionary to ResumeConfig object."""
        # Create a copy to avoid modifying the original
        config_dict = config_dict.copy()
        
        # Handle nested configurations
        if 'template_defaults' in config_dict:
            template_defaults = config_dict.get('template_defaults', {})
            config_dict['template_defaults'] = TemplateDefaultsConfig(
                **{k: v for k, v in template_defaults.items() 
                   if k in TemplateDefaultsConfig.__annotations__}
            )
        
        if 'ats_optimization' in config_dict:
            ats_optimization = config_dict.get('ats_optimization', {})
            config_dict['ats_optimization'] = ATSOptimizationConfig(
                **{k: v for k, v in ats_optimization.items() 
                   if k in ATSOptimizationConfig.__annotations__}
            )
        
        if 'generation_limits' in config_dict:
            generation_limits = config_dict.get('generation_limits', {})
            config_dict['generation_limits'] = GenerationLimitsConfig(
                **{k: v for k, v in generation_limits.items() 
                   if k in GenerationLimitsConfig.__annotations__}
            )
            
        # Handle MCP servers
        if 'mcp_servers' in config_dict:
            mcp_servers = {}
            for name, server_data in config_dict['mcp_servers'].items():
                if isinstance(server_data, dict):
                    mcp_servers[name] = MCPServerConfig(
                        command=server_data.get('command', ''),
                        args=server_data.get('args', []),
                        env=server_data.get('env', {}),
                        enabled=server_data.get('enabled', True),
                        port=server_data.get('port')
                    )
                elif isinstance(server_data, MCPServerConfig):
                    mcp_servers[name] = server_data
            config_dict['mcp_servers'] = mcp_servers
            
        # Handle MCP servers
        if 'mcp_servers' in config_dict:
            mcp_servers = {}
            for name, server_data in config_dict['mcp_servers'].items():
                if isinstance(server_data, dict):
                    mcp_servers[name] = MCPServerConfig(
                        command=server_data.get('command', ''),
                        args=server_data.get('args', []),
                        env=server_data.get('env', {}),
                        enabled=server_data.get('enabled', True),
                        port=server_data.get('port')
                    )
                elif isinstance(server_data, MCPServerConfig):
                    mcp_servers[name] = server_data
            config_dict['mcp_servers'] = mcp_servers
        
        # Handle providers
        if 'providers' in config_dict:
            providers = {}
            default_provider = config_dict.get('default_provider', 'openai')
            
            # Get default providers to use as fallback
            default_providers = ResumeConfig()._get_default_providers()
            
            for name, provider_data in config_dict['providers'].items():
                # Skip if provider_data is not a dictionary
                if not isinstance(provider_data, dict):
                    continue
                    
                # Get default values for this provider if available
                default_provider_config = default_providers.get(name, {})
                
                # Merge with default values
                merged_provider = {
                    'models': provider_data.get('models', getattr(default_provider_config, 'models', [])),
                    'default_model': provider_data.get('default_model', 
                                                     getattr(default_provider_config, 'default_model', '')),
                    'max_tokens': provider_data.get('max_tokens', 
                                                  getattr(default_provider_config, 'max_tokens', 2000)),
                    'temperature': provider_data.get('temperature', 
                                                   getattr(default_provider_config, 'temperature', 0.7)),
                    'timeout': provider_data.get('timeout', 
                                              getattr(default_provider_config, 'timeout', 60)),
                    'max_retries': provider_data.get('max_retries', 
                                                  getattr(default_provider_config, 'max_retries', 3)),
                    'retry_delay': provider_data.get('retry_delay', 
                                                  getattr(default_provider_config, 'retry_delay', 1.0)),
                    'api_key_env_var': provider_data.get('api_key_env_var', 
                                                      getattr(default_provider_config, 'api_key_env_var', None)),
                    'api_key': provider_data.get('api_key', 
                                               getattr(default_provider_config, 'api_key', None)),
                    'endpoint': provider_data.get('endpoint', 
                                               getattr(default_provider_config, 'endpoint', None)),
                    'mcp_server': provider_data.get('mcp_server',
                                                 getattr(default_provider_config, 'mcp_server', None))
                }
                
                # Create the provider config
                providers[name] = ProviderConfig(**merged_provider)
            
            config_dict['providers'] = providers
        
        # Filter out any keys not in ResumeConfig
        valid_keys = {f.name for f in dataclasses.fields(ResumeConfig) if f.init}
        filtered_config = {k: v for k, v in config_dict.items() if k in valid_keys}
        
        return ResumeConfig(**filtered_config)


# Convenience functions
def load_config(config_file: Optional[Union[str, Path]] = None) -> ResumeConfig:
    """Load configuration using the default config manager."""
    return ConfigManager(config_file).load_config()


def get_default_config() -> ResumeConfig:
    """Get the default configuration."""
    return ResumeConfig()


# Export all configuration classes
__all__ = [
    'ConfigManager',
    'ResumeConfig',
    'ProviderConfig',
    'MCPServerConfig',
    'TemplateDefaultsConfig',
    'ATSOptimizationConfig',
    'GenerationLimitsConfig',
    'ConfigSource',
    'load_config',
    'get_default_config'
]


if __name__ == "__main__":
    # Test the configuration manager
    print("🧪 Testing Configuration Manager")
    print("=" * 50)
    
    # Test default configuration
    default_config = get_default_config()
    print("✅ Default configuration created")
    
    # Test validation
    errors = default_config.validate()
    if errors:
        print(f"❌ Validation errors: {errors}")
    else:
        print("✅ Default configuration is valid")
    
    # Test loading from file
    try:
        config_manager = ConfigManager("config.json")
        loaded_config = config_manager.load_config()
        print("✅ Configuration loaded from file")
        
        # Test provider access
        openai_config = loaded_config.get_provider_config("openai")
        print(f"✅ OpenAI provider config: {openai_config.default_model}")
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
    
    print("\n✅ Configuration manager test completed!") 