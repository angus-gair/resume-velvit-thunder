#!/usr/bin/env python3
"""
AI Provider Integration Module
=============================

This module provides a unified interface for different AI providers including:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Open Source models (via Ollama or similar)

The module includes:
- Provider-specific client wrappers
- Unified API interface
- Error handling and retry logic
- Token usage tracking
- Response parsing utilities

Author: AI Resume Builder
Version: 1.0.0
Date: December 2024
"""

import os
import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from functools import wraps

# Third-party imports with fallbacks
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None
    Anthropic = None

try:
    import requests
except ImportError:
    requests = None

from config_manager import ProviderConfig, ResumeConfig


class AIProviderType(Enum):
    """Supported AI provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENSOURCE = "opensource"


class ResponseFormat(Enum):
    """Response format types."""
    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"


@dataclass
class AIResponse:
    """Standardized AI response format."""
    content: str
    model: str
    provider: AIProviderType
    tokens_used: int
    cost_estimate: float
    response_time: float
    metadata: Dict[str, Any]
    raw_response: Any = None


@dataclass
class AIRequest:
    """Standardized AI request format."""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    response_format: ResponseFormat = ResponseFormat.TEXT
    model: Optional[str] = None
    metadata: Dict[str, Any] = None


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass


class APIKeyError(AIProviderError):
    """Exception for API key related errors."""
    pass


class RateLimitError(AIProviderError):
    """Exception for rate limit errors."""
    pass


class ModelNotFoundError(AIProviderError):
    """Exception for model not found errors."""
    pass


class TokenLimitError(AIProviderError):
    """Exception for token limit errors."""
    pass


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for retrying failed API calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay on each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (RateLimitError, ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    continue
                except Exception as e:
                    # Don't retry on other types of errors
                    raise e
            
            # If we get here, all retries failed
            raise last_exception
        return wrapper
    return decorator


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: ProviderConfig, logger: logging.Logger):
        """
        Initialize the AI provider.
        
        Args:
            config: Provider configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client."""
        pass
    
    @abstractmethod
    def _make_request(self, request: AIRequest) -> AIResponse:
        """Make a request to the AI provider."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key for this provider."""
        pass
    
    @retry_on_failure()
    def generate_response(self, request: AIRequest) -> AIResponse:
        """
        Generate a response from the AI provider with retry logic.
        
        Args:
            request: Standardized AI request
            
        Returns:
            Standardized AI response
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Making AI request to {self.__class__.__name__}")
            response = self._make_request(request)
            response.response_time = time.time() - start_time
            
            self.logger.info(f"AI request completed in {response.response_time:.2f}s, "
                           f"tokens: {response.tokens_used}")
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"AI request failed after {duration:.2f}s: {str(e)}")
            raise
    
    def estimate_cost(self, tokens: int, model: str) -> float:
        """
        Estimate the cost for a given number of tokens.
        
        Args:
            tokens: Number of tokens
            model: Model name
            
        Returns:
            Estimated cost in USD
        """
        # Default implementation - should be overridden by providers
        return 0.0


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, config: ProviderConfig, logger: logging.Logger):
        """Initialize OpenAI provider."""
        if not openai:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        super().__init__(config, logger)
    
    def _initialize_client(self):
        """Initialize OpenAI client."""
        api_key = os.getenv(self.config.api_key_env_var) if self.config.api_key_env_var else None
        
        if not api_key:
            raise APIKeyError(f"OpenAI API key not found in environment variable: {self.config.api_key_env_var}")
        
        try:
            self.client = OpenAI(
                api_key=api_key,
                timeout=self.config.timeout,
                max_retries=0  # We handle retries ourselves
            )
            self.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def _make_request(self, request: AIRequest) -> AIResponse:
        """Make request to OpenAI API."""
        if not self.client:
            raise AIProviderError("OpenAI client not initialized")
        
        # Prepare messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        
        # Prepare parameters
        params = {
            "model": request.model or self.config.default_model,
            "messages": messages,
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "temperature": request.temperature if request.temperature is not None else self.config.temperature,
        }
        
        # Handle response format
        if request.response_format == ResponseFormat.JSON:
            params["response_format"] = {"type": "json_object"}
        
        try:
            response = self.client.chat.completions.create(**params)
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            model_used = response.model
            
            return AIResponse(
                content=content,
                model=model_used,
                provider=AIProviderType.OPENAI,
                tokens_used=tokens_used,
                cost_estimate=self.estimate_cost(tokens_used, model_used),
                response_time=0.0,  # Will be set by caller
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                },
                raw_response=response
            )
            
        except openai.RateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.AuthenticationError as e:
            raise APIKeyError(f"OpenAI authentication failed: {str(e)}")
        except openai.NotFoundError as e:
            raise ModelNotFoundError(f"OpenAI model not found: {str(e)}")
        except Exception as e:
            raise AIProviderError(f"OpenAI API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return self.config.models.copy()
    
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key."""
        try:
            # Make a minimal request to test the API key
            response = self.client.chat.completions.create(
                model=self.config.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception:
            return False
    
    def estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost for OpenAI models."""
        # Simplified cost estimation (rates as of 2024)
        cost_per_1k_tokens = {
            "gpt-4-turbo-preview": 0.01,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
        }
        
        rate = cost_per_1k_tokens.get(model, 0.01)  # Default rate
        return (tokens / 1000) * rate


class AnthropicProvider(BaseAIProvider):
    """Anthropic provider implementation."""
    
    def __init__(self, config: ProviderConfig, logger: logging.Logger):
        """Initialize Anthropic provider."""
        if not anthropic:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
        
        super().__init__(config, logger)
    
    def _initialize_client(self):
        """Initialize Anthropic client."""
        api_key = os.getenv(self.config.api_key_env_var) if self.config.api_key_env_var else None
        
        if not api_key:
            raise APIKeyError(f"Anthropic API key not found in environment variable: {self.config.api_key_env_var}")
        
        try:
            self.client = Anthropic(
                api_key=api_key,
                timeout=self.config.timeout,
                max_retries=0  # We handle retries ourselves
            )
            self.logger.info("Anthropic client initialized successfully")
        except Exception as e:
            raise AIProviderError(f"Failed to initialize Anthropic client: {str(e)}")
    
    def _make_request(self, request: AIRequest) -> AIResponse:
        """Make request to Anthropic API."""
        if not self.client:
            raise AIProviderError("Anthropic client not initialized")
        
        # Prepare parameters
        params = {
            "model": request.model or self.config.default_model,
            "max_tokens": request.max_tokens or self.config.max_tokens,
            "temperature": request.temperature if request.temperature is not None else self.config.temperature,
            "messages": [{"role": "user", "content": request.prompt}]
        }
        
        # Add system prompt if provided
        if request.system_prompt:
            params["system"] = request.system_prompt
        
        try:
            response = self.client.messages.create(**params)
            
            # Extract response data
            content = response.content[0].text if response.content else ""
            tokens_used = response.usage.input_tokens + response.usage.output_tokens if response.usage else 0
            model_used = response.model
            
            return AIResponse(
                content=content,
                model=model_used,
                provider=AIProviderType.ANTHROPIC,
                tokens_used=tokens_used,
                cost_estimate=self.estimate_cost(tokens_used, model_used),
                response_time=0.0,  # Will be set by caller
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens if response.usage else 0,
                    "output_tokens": response.usage.output_tokens if response.usage else 0,
                },
                raw_response=response
            )
            
        except anthropic.RateLimitError as e:
            raise RateLimitError(f"Anthropic rate limit exceeded: {str(e)}")
        except anthropic.AuthenticationError as e:
            raise APIKeyError(f"Anthropic authentication failed: {str(e)}")
        except anthropic.NotFoundError as e:
            raise ModelNotFoundError(f"Anthropic model not found: {str(e)}")
        except Exception as e:
            raise AIProviderError(f"Anthropic API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        return self.config.models.copy()
    
    def validate_api_key(self) -> bool:
        """Validate Anthropic API key."""
        try:
            # Make a minimal request to test the API key
            response = self.client.messages.create(
                model=self.config.default_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
    
    def estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost for Anthropic models."""
        # Simplified cost estimation (rates as of 2024)
        cost_per_1k_tokens = {
            "claude-3-opus-20240229": 0.015,
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.00025,
        }
        
        rate = cost_per_1k_tokens.get(model, 0.003)  # Default rate
        return (tokens / 1000) * rate


class OpenSourceProvider(BaseAIProvider):
    """Open source provider implementation (via Ollama or similar)."""
    
    def __init__(self, config: ProviderConfig, logger: logging.Logger):
        """Initialize open source provider."""
        if not requests:
            raise ImportError("Requests library not installed. Run: pip install requests")
        
        super().__init__(config, logger)
    
    def _initialize_client(self):
        """Initialize open source client."""
        if not self.config.endpoint:
            raise AIProviderError("Endpoint not configured for open source provider")
        
        # Test connection to endpoint
        try:
            response = requests.get(f"{self.config.endpoint.rstrip('/')}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info("Open source provider endpoint is accessible")
            else:
                self.logger.warning(f"Open source endpoint returned status {response.status_code}")
        except Exception as e:
            self.logger.warning(f"Could not connect to open source endpoint: {str(e)}")
    
    def _make_request(self, request: AIRequest) -> AIResponse:
        """Make request to open source API."""
        if not self.config.endpoint:
            raise AIProviderError("Open source provider not properly configured")
        
        # Prepare prompt
        full_prompt = request.prompt
        if request.system_prompt:
            full_prompt = f"System: {request.system_prompt}\n\nUser: {request.prompt}"
        
        # Prepare parameters
        params = {
            "model": request.model or self.config.default_model,
            "prompt": full_prompt,
            "options": {
                "temperature": request.temperature if request.temperature is not None else self.config.temperature,
                "num_predict": request.max_tokens or self.config.max_tokens,
            },
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.config.endpoint.rstrip('/')}/api/generate",
                json=params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result.get("response", "")
            
            # Estimate tokens (rough approximation)
            tokens_used = len(content.split()) + len(full_prompt.split())
            
            return AIResponse(
                content=content,
                model=params["model"],
                provider=AIProviderType.OPENSOURCE,
                tokens_used=tokens_used,
                cost_estimate=0.0,  # Open source is typically free
                response_time=0.0,  # Will be set by caller
                metadata={
                    "done": result.get("done", False),
                    "context": result.get("context", []),
                },
                raw_response=result
            )
            
        except requests.exceptions.Timeout:
            raise TimeoutError("Open source API request timed out")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Could not connect to open source API")
        except Exception as e:
            raise AIProviderError(f"Open source API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available open source models."""
        return self.config.models.copy()
    
    def validate_api_key(self) -> bool:
        """Validate open source provider (no API key needed)."""
        try:
            # Test connection to endpoint
            response = requests.get(f"{self.config.endpoint.rstrip('/')}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class AIProviderManager:
    """Manages multiple AI providers and provides unified interface."""
    
    def __init__(self, config: ResumeConfig, logger: logging.Logger):
        """
        Initialize the AI provider manager.
        
        Args:
            config: Resume configuration containing provider settings
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.providers: Dict[AIProviderType, BaseAIProvider] = {}
        self.fallback_order: List[AIProviderType] = []
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers."""
        provider_classes = {
            AIProviderType.OPENAI: OpenAIProvider,
            AIProviderType.ANTHROPIC: AnthropicProvider,
            AIProviderType.OPENSOURCE: OpenSourceProvider,
        }
        
        for provider_name, provider_config in self.config.providers.items():
            try:
                provider_type = AIProviderType(provider_name)
                provider_class = provider_classes[provider_type]
                
                provider = provider_class(provider_config, self.logger)
                self.providers[provider_type] = provider
                self.fallback_order.append(provider_type)
                
                self.logger.info(f"Initialized {provider_name} provider")
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize {provider_name} provider: {str(e)}")
    
    def get_provider(self, provider_type: Optional[AIProviderType] = None) -> BaseAIProvider:
        """
        Get a specific provider or the default provider.
        
        Args:
            provider_type: Specific provider type to get
            
        Returns:
            AI provider instance
        """
        if provider_type is None:
            provider_type = AIProviderType(self.config.default_provider)
        
        if provider_type not in self.providers:
            raise AIProviderError(f"Provider {provider_type.value} not available")
        
        return self.providers[provider_type]
    
    def generate_response(self, request: AIRequest, 
                         provider_type: Optional[AIProviderType] = None,
                         use_fallback: bool = True) -> AIResponse:
        """
        Generate response with optional fallback to other providers.
        
        Args:
            request: AI request
            provider_type: Preferred provider type
            use_fallback: Whether to try fallback providers on failure
            
        Returns:
            AI response
        """
        # Determine provider order
        if provider_type:
            providers_to_try = [provider_type]
            if use_fallback:
                providers_to_try.extend([p for p in self.fallback_order if p != provider_type])
        else:
            providers_to_try = self.fallback_order.copy()
        
        last_error = None
        
        for provider_type in providers_to_try:
            if provider_type not in self.providers:
                continue
            
            try:
                provider = self.providers[provider_type]
                response = provider.generate_response(request)
                
                self.logger.info(f"Successfully generated response using {provider_type.value}")
                return response
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Provider {provider_type.value} failed: {str(e)}")
                continue
        
        # If we get here, all providers failed
        raise AIProviderError(f"All providers failed. Last error: {str(last_error)}")
    
    def get_available_models(self, provider_type: Optional[AIProviderType] = None) -> Dict[str, List[str]]:
        """
        Get available models for all or specific providers.
        
        Args:
            provider_type: Specific provider type
            
        Returns:
            Dictionary mapping provider names to model lists
        """
        if provider_type:
            if provider_type in self.providers:
                return {provider_type.value: self.providers[provider_type].get_available_models()}
            else:
                return {}
        
        return {
            provider_type.value: provider.get_available_models()
            for provider_type, provider in self.providers.items()
        }
    
    def validate_providers(self) -> Dict[str, bool]:
        """
        Validate all providers.
        
        Returns:
            Dictionary mapping provider names to validation status
        """
        results = {}
        
        for provider_type, provider in self.providers.items():
            try:
                results[provider_type.value] = provider.validate_api_key()
            except Exception as e:
                self.logger.error(f"Error validating {provider_type.value}: {str(e)}")
                results[provider_type.value] = False
        
        return results


# Convenience functions
def create_ai_request(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> AIRequest:
    """Create an AI request with default parameters."""
    return AIRequest(
        prompt=prompt,
        system_prompt=system_prompt,
        **kwargs
    )


def parse_json_response(response: AIResponse) -> Dict[str, Any]:
    """Parse JSON response from AI provider."""
    try:
        return json.loads(response.content)
    except json.JSONDecodeError as e:
        raise AIProviderError(f"Failed to parse JSON response: {str(e)}")


if __name__ == "__main__":
    # Test the AI providers
    print("🧪 Testing AI Provider Integration")
    print("=" * 50)
    
    # This would require actual API keys to test fully
    print("✅ AI provider module loaded successfully")
    print("📝 Note: Full testing requires valid API keys in environment variables")
    
    # Test provider types
    for provider_type in AIProviderType:
        print(f"✅ Provider type available: {provider_type.value}")
    
    print("\n✅ AI provider integration test completed!") 