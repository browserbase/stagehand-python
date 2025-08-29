"""LLM client for model interactions."""

import os
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

import litellm

from stagehand.metrics import get_inference_time_ms, start_inference_timer

if TYPE_CHECKING:
    from ..logging import StagehandLogger


class LLMProviderError(Exception):
    """Exception raised for LLM provider configuration errors."""
    pass


class LLMClient:
    """
    Enhanced client for making LLM calls using the litellm library.
    Supports custom API endpoints and multiple providers with proper error handling.
    """

    # Default API endpoints for different providers
    DEFAULT_ENDPOINTS = {
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com",
        "together": "https://api.together.xyz/v1",
        "groq": "https://api.groq.com/openai/v1",
    }

    def __init__(
        self,
        stagehand_logger: "StagehandLogger",
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        metrics_callback: Optional[Callable[[Any, int, Optional[str]], None]] = None,
        **kwargs: Any,
    ):
        """
        Initialize the enhanced LLM client with support for custom API endpoints.

        Args:
            stagehand_logger: StagehandLogger instance for centralized logging
            api_key: API key for the model provider
            default_model: Default model to use (e.g., "gpt-4o", "claude-3-opus-20240229")
            metrics_callback: Optional callback to track metrics from responses
            **kwargs: Additional configuration options including:
                - api_base: Custom API base URL
                - baseURL: Alias for api_base
                - timeout: Request timeout in seconds
                - max_retries: Maximum number of retries
                - Other litellm global settings
        """
        self.logger = stagehand_logger
        self.default_model = default_model
        self.metrics_callback = metrics_callback
        
        # Store original configuration for validation and fallback
        self.config = kwargs.copy()
        self.api_key = api_key
        
        # Validate and configure API settings
        self._configure_api_settings(api_key, **kwargs)
        
        # Perform initial validation
        self._validate_initial_configuration()

    def _configure_api_settings(self, api_key: Optional[str], **kwargs: Any) -> None:
        """
        Configure API settings with validation and error handling.
        
        Args:
            api_key: API key for the model provider
            **kwargs: Additional configuration options
        """
        try:
            # Handle API key configuration
            if api_key:
                litellm.api_key = api_key
                self.logger.debug("Set API key for LLM client", category="llm")
            
            # Handle API base URL configuration
            api_base = kwargs.get("api_base") or kwargs.get("baseURL")
            if api_base:
                self._validate_api_base(api_base)
                litellm.api_base = api_base
                self.logger.debug(f"Set custom API base: {api_base}", category="llm")
            else:
                # Try to infer provider and set default endpoint
                provider = self._infer_provider_from_model(self.default_model)
                if provider and provider in self.DEFAULT_ENDPOINTS:
                    default_endpoint = self.DEFAULT_ENDPOINTS[provider]
                    litellm.api_base = default_endpoint
                    self.logger.debug(f"Set default API base for {provider}: {default_endpoint}", category="llm")

            # Apply other global settings
            for key, value in kwargs.items():
                if key in ["api_base", "baseURL"]:
                    continue  # Already handled above
                    
                if hasattr(litellm, key):
                    setattr(litellm, key, value)
                    self.logger.debug(f"Set global litellm.{key} = {value}", category="llm")
                elif key in ["timeout", "max_retries"]:
                    # Store these for per-request use
                    setattr(self, f"_{key}", value)
                    self.logger.debug(f"Set client {key} = {value}", category="llm")

        except Exception as e:
            self.logger.error(f"Error configuring LLM client: {e}", category="llm")
            raise LLMProviderError(f"Failed to configure LLM client: {e}") from e

    def _validate_api_base(self, api_base: str) -> None:
        """
        Validate the API base URL format.
        
        Args:
            api_base: The API base URL to validate
            
        Raises:
            LLMProviderError: If the API base URL is invalid
        """
        if not isinstance(api_base, str):
            raise LLMProviderError("api_base must be a string")
        
        if not (api_base.startswith("http://") or api_base.startswith("https://")):
            raise LLMProviderError("api_base must be a valid HTTP/HTTPS URL")
        
        # Remove trailing slash for consistency
        if api_base.endswith("/"):
            api_base = api_base.rstrip("/")

    def _infer_provider_from_model(self, model: Optional[str]) -> Optional[str]:
        """
        Infer the provider from the model name.
        
        Args:
            model: The model name
            
        Returns:
            The inferred provider name or None if cannot be determined
        """
        if not model:
            return None
            
        model_lower = model.lower()
        
        if model_lower.startswith("gpt-") or "openai" in model_lower:
            return "openai"
        elif model_lower.startswith("claude-") or "anthropic" in model_lower:
            return "anthropic"
        elif "together" in model_lower:
            return "together"
        elif "groq" in model_lower:
            return "groq"
        elif model_lower.startswith("gemini/") or model_lower.startswith("google/"):
            return "google"
        
        return None

    def _get_provider_specific_config(self, model: str) -> Dict[str, Any]:
        """
        Get provider-specific configuration for the model.
        
        Args:
            model: The model name
            
        Returns:
            Dictionary of provider-specific configuration
        """
        provider = self._infer_provider_from_model(model)
        config = {}
        
        # Add provider-specific configurations
        if provider == "anthropic":
            # Anthropic models may need specific headers or parameters
            config.update({
                "anthropic_version": "2023-06-01",
            })
        elif provider == "together":
            # Together AI specific configurations
            config.update({
                "stream": False,  # Ensure streaming is handled properly
            })
        elif provider == "groq":
            # Groq specific configurations
            config.update({
                "stream": False,
            })
        
        return config

    def create_response(
        self,
        *,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        function_name: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a chat completion response with enhanced error handling and provider support.

        Args:
            messages: List of message dictionaries
            model: Specific model to use (overrides default_model)
            function_name: Function name for metrics tracking
            **kwargs: Additional parameters for litellm.completion

        Returns:
            Dictionary containing the completion response

        Raises:
            ValueError: If no model is specified
            LLMProviderError: If there's a provider configuration error
            Exception: Other errors from litellm.completion
        """
        completion_model = model or self.default_model
        if not completion_model:
            raise ValueError(
                "No model specified for chat completion. Please provide a model name "
                "either in the constructor (default_model) or in this method call."
            )

        # Standardize model names
        completion_model = self._standardize_model_name(completion_model)
        
        # Get provider-specific configuration
        provider_config = self._get_provider_specific_config(completion_model)
        
        # Prepare parameters
        params = {
            "model": completion_model,
            "messages": messages,
            **provider_config,
            **kwargs,
        }
        
        # Add client-level settings if available
        if hasattr(self, "_timeout"):
            params["timeout"] = self._timeout
        if hasattr(self, "_max_retries"):
            params["max_retries"] = self._max_retries
        
        # Filter out None values
        filtered_params = {
            k: v for k, v in params.items() if v is not None or k in kwargs
        }
        
        # Apply model-specific fixes
        if "gpt-5" in completion_model:
            filtered_params["temperature"] = 1

        self.logger.debug(
            f"Calling litellm.completion with model={completion_model}",
            category="llm",
            auxiliary={"params": {k: v for k, v in filtered_params.items() if k != "messages"}}
        )

        try:
            # Start tracking inference time
            start_time = start_inference_timer()

            # Make the API call with retry logic
            response = self._make_api_call_with_retry(filtered_params)

            # Calculate inference time
            inference_time_ms = get_inference_time_ms(start_time)

            # Update metrics if callback is provided
            if self.metrics_callback:
                self.metrics_callback(response, inference_time_ms, function_name)

            self.logger.debug(
                f"Successfully received response from {completion_model}",
                category="llm",
                auxiliary={
                    "inference_time_ms": inference_time_ms,
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0) if hasattr(response, "usage") else 0,
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0) if hasattr(response, "usage") else 0,
                }
            )

            return response

        except Exception as e:
            error_msg = f"Error calling litellm.completion with model {completion_model}: {e}"
            self.logger.error(error_msg, category="llm")
            
            # Provide helpful error messages based on common issues
            if "api_key" in str(e).lower():
                raise LLMProviderError(
                    f"API key error for model {completion_model}. "
                    f"Please check your API key configuration in model_client_options. "
                    f"Original error: {e}"
                ) from e
            elif "not found" in str(e).lower() or "404" in str(e):
                raise LLMProviderError(
                    f"Model {completion_model} not found. "
                    f"Please check the model name and your API endpoint configuration. "
                    f"Original error: {e}"
                ) from e
            elif "unauthorized" in str(e).lower() or "401" in str(e):
                raise LLMProviderError(
                    f"Unauthorized access for model {completion_model}. "
                    f"Please check your API key and permissions. "
                    f"Original error: {e}"
                ) from e
            elif "rate limit" in str(e).lower() or "429" in str(e):
                raise LLMProviderError(
                    f"Rate limit exceeded for model {completion_model}. "
                    f"Please try again later or check your usage limits. "
                    f"Original error: {e}"
                ) from e
            else:
                raise LLMProviderError(f"LLM API error: {e}") from e

    def _standardize_model_name(self, model: str) -> str:
        """
        Standardize model names for different providers.
        
        Args:
            model: Original model name
            
        Returns:
            Standardized model name
        """
        # Standardize gemini provider to google
        if model.startswith("google/"):
            return model.replace("google/", "gemini/")
        
        return model

    def _make_api_call_with_retry(self, params: Dict[str, Any]) -> Any:
        """
        Make API call with built-in retry logic.
        
        Args:
            params: Parameters for the API call
            
        Returns:
            Response from litellm.completion
        """
        max_retries = getattr(self, "_max_retries", 3)
        
        for attempt in range(max_retries + 1):
            try:
                return litellm.completion(**params)
            except Exception as e:
                if attempt == max_retries:
                    raise
                
                # Only retry on certain types of errors
                if any(error_type in str(e).lower() for error_type in ["timeout", "connection", "rate limit"]):
                    self.logger.debug(
                        f"Retrying API call (attempt {attempt + 1}/{max_retries + 1}) after error: {e}",
                        category="llm"
                    )
                    continue
                else:
                    # Don't retry on authentication, not found, or other permanent errors
                    raise

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current LLM client configuration.
        
        Returns:
            Dictionary containing validation results and configuration info
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "configuration": {
                "default_model": self.default_model,
                "api_key_configured": bool(self.api_key),
                "api_base": getattr(litellm, "api_base", None),
                "provider": self._infer_provider_from_model(self.default_model),
            }
        }
        
        # Check if model is specified
        if not self.default_model:
            validation_result["errors"].append("No default model specified")
            validation_result["valid"] = False
        
        # Check if API key is available (either directly or via environment)
        provider = self._infer_provider_from_model(self.default_model)
        if provider:
            env_key_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "together": "TOGETHER_API_KEY",
                "groq": "GROQ_API_KEY",
            }
            
            env_key = env_key_map.get(provider)
            if not self.api_key and not (env_key and os.getenv(env_key)):
                validation_result["warnings"].append(
                    f"No API key found for {provider}. "
                    f"Consider setting {env_key} environment variable or providing api_key in model_client_options."
                )
        
        return validation_result

    def _validate_initial_configuration(self) -> None:
        """
        Validate the initial LLM client configuration and log any issues.
        
        Raises:
            LLMProviderError: If critical configuration issues are found
        """
        validation_result = self.validate_configuration()
        
        # Log warnings
        for warning in validation_result["warnings"]:
            self.logger.warn(f"LLM configuration: {warning}", category="llm")
        
        # Handle errors - for now we log them but don't fail initialization
        # This allows the client to work with environment variables that might be set later
        for error in validation_result["errors"]:
            self.logger.warn(f"LLM configuration issue: {error}", category="llm")
        
        # Log configuration info
        config_info = validation_result["configuration"]
        self.logger.debug(
            f"LLM client initialized - Provider: {config_info.get('provider', 'unknown')}, "
            f"Model: {config_info.get('default_model', 'none')}, "
            f"API Key: {'configured' if config_info.get('api_key_configured') else 'not configured'}",
            category="llm"
        )
