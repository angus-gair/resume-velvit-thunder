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
try:
    import yaml
except ImportError:
    yaml = None
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging


class ConfigSource(Enum):
    """Configuration source types."""
    FILE = "file"
    ENVIRONMENT = "environment"
    DEFAULT = "default"


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
    api_key_env_var: Optional[str] = None
    endpoint: Optional[str] = None
    
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
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # Map environment variables to config keys
        env_mappings = {
            'RESUME_DB_PATH': 'database_path',
            'RESUME_TEMPLATE_DIR': 'template_dir',
            'RESUME_OUTPUT_DIR': 'output_dir',
            'RESUME_DEFAULT_PROVIDER': 'default_provider',
            'RESUME_DEFAULT_MODEL': 'default_model',
            'RESUME_MAX_RETRIES': ('max_retries', int),
            'RESUME_RETRY_DELAY': ('retry_delay', float),
            'RESUME_REQUEST_TIMEOUT': ('request_timeout', int),
            'RESUME_MAX_TOKENS': ('max_tokens', int),
            'RESUME_TEMPERATURE': ('temperature', float),
            'RESUME_DEBUG_MODE': ('debug_mode', lambda x: x.lower() in ['true', '1', 'yes']),
            'RESUME_LOG_LEVEL': 'log_level',
            'RESUME_PRESERVE_LOGS': ('preserve_logs', int),
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(config_key, tuple):
                    key, converter = config_key
                    try:
                        env_config[key] = converter(value)
                    except (ValueError, TypeError) as e:
                        self.logger.warning(f"Invalid value for {env_var}: {value} ({e})")
                else:
                    env_config[config_key] = value
        
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
        # Handle nested configurations
        if 'template_defaults' in config_dict:
            config_dict['template_defaults'] = TemplateDefaultsConfig(**config_dict['template_defaults'])
        
        if 'ats_optimization' in config_dict:
            config_dict['ats_optimization'] = ATSOptimizationConfig(**config_dict['ats_optimization'])
        
        if 'generation_limits' in config_dict:
            config_dict['generation_limits'] = GenerationLimitsConfig(**config_dict['generation_limits'])
        
        if 'providers' in config_dict:
            providers = {}
            for name, provider_dict in config_dict['providers'].items():
                providers[name] = ProviderConfig(**provider_dict)
            config_dict['providers'] = providers
        
        return ResumeConfig(**config_dict)


# Convenience functions
def load_config(config_file: Optional[Union[str, Path]] = None) -> ResumeConfig:
    """Load configuration using the default config manager."""
    manager = ConfigManager(config_file)
    return manager.load_config()


def get_default_config() -> ResumeConfig:
    """Get the default configuration."""
    return ResumeConfig()


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