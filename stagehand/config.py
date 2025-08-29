import os
from typing import Any, Callable, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, ValidationError

from stagehand.schemas import AvailableModel


class StagehandConfigError(Exception):
    """Exception raised for Stagehand configuration errors."""
    pass


class StagehandConfig(BaseModel):
    """
    Configuration for the Stagehand client.

    This configuration is designed for local browser automation using Playwright.
    All browser operations run locally without external service dependencies.

    Attributes:
        model_name (Optional[str]): Name of the language model to use for AI operations.
        model_api_key (Optional[str]): API key for the language model provider.
        model_client_options (Optional[dict[str, Any]]): Configuration options for the language model client.
            Supports custom API endpoints via 'api_base' parameter for OpenAI/Anthropic compatible providers.
            Examples:
            - OpenAI: {"api_base": "https://api.openai.com/v1", "api_key": "your-key"}
            - Anthropic: {"api_base": "https://api.anthropic.com", "api_key": "your-key"}
            - Together AI: {"api_base": "https://api.together.xyz/v1", "api_key": "your-key"}
            - Local OpenAI server: {"api_base": "http://localhost:8000/v1", "api_key": "local-key"}
        verbose (Optional[int]): Verbosity level for logs (0=ERROR, 1=INFO, 2=DEBUG).
        logger (Optional[Callable[[Any], None]]): Custom logging function.
        use_rich_logging (Optional[bool]): Whether to use Rich for colorized logging.
        dom_settle_timeout_ms (Optional[int]): Timeout for DOM to settle after actions (in milliseconds).
        enable_caching (Optional[bool]): Enable caching functionality for improved performance.
        self_heal (Optional[bool]): Enable self-healing functionality to recover from failures.
        wait_for_captcha_solves (Optional[bool]): Whether to wait for CAPTCHA to be solved manually.
        system_prompt (Optional[str]): Custom system prompt to use for LLM interactions.
        local_browser_launch_options (Optional[dict[str, Any]]): Options for launching the local browser.
            Supports all Playwright browser launch options such as:
            - headless: bool - Run browser in headless mode
            - viewport: dict - Set viewport size
            - user_data_dir: str - Browser profile directory
            - args: list - Additional browser arguments
        experimental (Optional[bool]): Enable experimental features (use with caution).
    """

    model_name: Optional[str] = Field(
        AvailableModel.GPT_4O, 
        alias="modelName", 
        description="Name of the language model to use for AI operations"
    )
    model_api_key: Optional[str] = Field(
        None, 
        alias="modelApiKey", 
        description="API key for the language model provider"
    )
    model_client_options: Optional[dict[str, Any]] = Field(
        None,
        alias="modelClientOptions",
        description="Configuration options for the language model client. "
                   "Use 'api_base' to specify custom API endpoints for OpenAI/Anthropic compatible providers. "
                   "Example: {'api_base': 'https://api.together.xyz/v1', 'api_key': 'your-key'}",
    )
    verbose: Optional[int] = Field(
        1,
        description="Verbosity level for logs: 0=ERROR only, 1=INFO and above, 2=DEBUG and above",
    )
    logger: Optional[Callable[[Any], None]] = Field(
        None, 
        description="Custom logging function to override default logging behavior"
    )
    use_rich_logging: Optional[bool] = Field(
        True, 
        description="Whether to use Rich library for colorized and formatted logging output"
    )
    dom_settle_timeout_ms: Optional[int] = Field(
        3000,
        alias="domSettleTimeoutMs",
        description="Timeout in milliseconds to wait for DOM to settle after actions",
    )
    enable_caching: Optional[bool] = Field(
        False, 
        alias="enableCaching", 
        description="Enable caching functionality to improve performance by reusing results"
    )
    self_heal: Optional[bool] = Field(
        True, 
        alias="selfHeal", 
        description="Enable self-healing functionality to automatically recover from failures"
    )
    wait_for_captcha_solves: Optional[bool] = Field(
        False,
        alias="waitForCaptchaSolves",
        description="Whether to pause execution and wait for manual CAPTCHA solving",
    )
    system_prompt: Optional[str] = Field(
        None,
        alias="systemPrompt",
        description="Custom system prompt to use for LLM interactions, overrides default prompts",
    )
    local_browser_launch_options: Optional[dict[str, Any]] = Field(
        {},
        alias="localBrowserLaunchOptions",
        description="Options for launching the local Playwright browser instance. "
                   "Supports all Playwright launch options like headless, viewport, user_data_dir, args, etc.",
    )
    experimental: Optional[bool] = Field(
        False,
        description="Enable experimental features that may be unstable or change in future versions",
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("model_client_options")
    @classmethod
    def validate_model_client_options(cls, v):
        """Validate model_client_options configuration with enhanced validation."""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError("model_client_options must be a dictionary")
        
        # Validate api_base if provided
        api_base = v.get("api_base") or v.get("baseURL")
        if api_base:
            validation_result = validate_api_base_url(api_base)
            if not validation_result["valid"]:
                raise ValueError(validation_result["error"])
            
            # Normalize the URL (remove trailing slash)
            normalized_url = validation_result["normalized_url"]
            if "api_base" in v:
                v["api_base"] = normalized_url
            if "baseURL" in v:
                v["baseURL"] = normalized_url
        
        # Validate timeout if provided
        if "timeout" in v:
            timeout = v["timeout"]
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise ValueError("timeout must be a positive number")
        
        # Validate max_retries if provided
        if "max_retries" in v:
            max_retries = v["max_retries"]
            if not isinstance(max_retries, int) or max_retries < 0:
                raise ValueError("max_retries must be a non-negative integer")
        
        # Validate API key variants
        api_key_fields = ["api_key", "apiKey"]
        api_keys_found = [field for field in api_key_fields if field in v]
        if len(api_keys_found) > 1:
            raise ValueError(f"Only one API key field should be specified, found: {api_keys_found}")
        
        return v

    @field_validator("verbose")
    @classmethod
    def validate_verbose(cls, v):
        """Validate verbose level is within acceptable range."""
        if v is not None and not (0 <= v <= 2):
            raise ValueError("verbose must be 0 (ERROR), 1 (INFO), or 2 (DEBUG)")
        return v

    @field_validator("dom_settle_timeout_ms")
    @classmethod
    def validate_dom_settle_timeout(cls, v):
        """Validate DOM settle timeout is positive."""
        if v is not None and v < 0:
            raise ValueError("dom_settle_timeout_ms must be non-negative")
        return v

    def with_overrides(self, **overrides) -> "StagehandConfig":
        """
        Create a new config instance with the specified overrides.

        Args:
            **overrides: Key-value pairs to override in the config

        Returns:
            StagehandConfig: New config instance with overrides applied
        """
        config_dict = self.model_dump()
        config_dict.update(overrides)
        return StagehandConfig(**config_dict)


# Configuration validation utility functions

def validate_api_base_url(api_base: str) -> dict[str, Any]:
    """
    Validate an API base URL with comprehensive checks.
    
    Args:
        api_base: The API base URL to validate
        
    Returns:
        Dictionary with validation results:
        - valid: bool - Whether the URL is valid
        - error: str - Error message if invalid
        - normalized_url: str - Normalized URL if valid
        - warnings: list - List of warning messages
    """
    result = {
        "valid": False,
        "error": "",
        "normalized_url": "",
        "warnings": []
    }
    
    if not isinstance(api_base, str):
        result["error"] = "api_base must be a string"
        return result
    
    if not api_base.strip():
        result["error"] = "api_base cannot be empty"
        return result
    
    # Check for valid URL scheme
    if not (api_base.startswith("http://") or api_base.startswith("https://")):
        result["error"] = "api_base must be a valid HTTP/HTTPS URL"
        return result
    
    try:
        parsed = urlparse(api_base)
        
        # Check for valid hostname
        if not parsed.netloc:
            result["error"] = "api_base must have a valid hostname"
            return result
        
        # Warn about localhost/local IPs for production use
        if parsed.hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
            result["warnings"].append("Using localhost/local IP - ensure this is intended for development")
        
        # Warn about HTTP (non-HTTPS) for production APIs
        if parsed.scheme == "http" and parsed.hostname not in ["localhost", "127.0.0.1", "0.0.0.0"]:
            result["warnings"].append("Using HTTP instead of HTTPS - consider using HTTPS for security")
        
        # Normalize URL (remove trailing slash)
        normalized = api_base.rstrip("/")
        
        result["valid"] = True
        result["normalized_url"] = normalized
        
    except Exception as e:
        result["error"] = f"Invalid URL format: {e}"
    
    return result


def validate_api_key_configuration(model_name: Optional[str], model_api_key: Optional[str], 
                                 model_client_options: Optional[dict[str, Any]]) -> dict[str, Any]:
    """
    Validate API key configuration for different LLM providers.
    
    Args:
        model_name: The model name to infer provider
        model_api_key: Direct API key
        model_client_options: Client options that may contain API key
        
    Returns:
        Dictionary with validation results:
        - valid: bool - Whether API key configuration is valid
        - errors: list - List of error messages
        - warnings: list - List of warning messages
        - provider: str - Detected provider
        - api_key_source: str - Where the API key was found
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "provider": None,
        "api_key_source": None
    }
    
    # Infer provider from model name
    provider = infer_provider_from_model_name(model_name)
    result["provider"] = provider
    
    if not provider:
        result["warnings"].append("Could not infer provider from model name - API key validation may be incomplete")
        return result
    
    # Check for API key in various locations
    api_key_found = False
    
    # Check direct API key
    if model_api_key:
        api_key_found = True
        result["api_key_source"] = "model_api_key"
    
    # Check API key in model_client_options
    if model_client_options:
        client_api_key = model_client_options.get("api_key") or model_client_options.get("apiKey")
        if client_api_key:
            if api_key_found:
                result["warnings"].append("API key found in multiple locations - model_client_options will take precedence")
            api_key_found = True
            result["api_key_source"] = "model_client_options"
    
    # Check environment variables
    env_key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY", 
        "together": "TOGETHER_API_KEY",
        "groq": "GROQ_API_KEY",
        "google": "GOOGLE_API_KEY",
        "cohere": "COHERE_API_KEY",
    }
    
    env_key = env_key_map.get(provider)
    env_api_key = None
    if env_key:
        env_api_key = os.getenv(env_key)
        if env_api_key:
            if not api_key_found:
                api_key_found = True
                result["api_key_source"] = f"environment ({env_key})"
            elif result["api_key_source"] != "model_client_options":
                result["warnings"].append(f"API key found in both configuration and environment variable {env_key}")
    
    # Validate API key presence
    if not api_key_found:
        result["valid"] = False
        if env_key:
            result["errors"].append(
                f"No API key found for {provider} provider. "
                f"Please provide an API key via model_api_key, model_client_options['api_key'], "
                f"or set the {env_key} environment variable."
            )
        else:
            result["errors"].append(
                f"No API key found for {provider} provider. "
                f"Please provide an API key via model_api_key or model_client_options['api_key']."
            )
    
    return result


def infer_provider_from_model_name(model_name: Optional[str]) -> Optional[str]:
    """
    Infer the LLM provider from the model name.
    
    Args:
        model_name: The model name
        
    Returns:
        The inferred provider name or None if cannot be determined
    """
    if not model_name:
        return None
        
    model_lower = model_name.lower()
    
    # OpenAI models
    if model_lower.startswith("gpt-") or "openai" in model_lower:
        return "openai"
    
    # Anthropic models
    if model_lower.startswith("claude-") or "anthropic" in model_lower:
        return "anthropic"
    
    # Together AI models
    if "together" in model_lower or model_lower.startswith("meta-llama/") or model_lower.startswith("mistralai/"):
        return "together"
    
    # Groq models
    if "groq" in model_lower or model_lower.startswith("llama") or model_lower.startswith("mixtral"):
        return "groq"
    
    # Google models
    if model_lower.startswith("gemini") or model_lower.startswith("google/") or "palm" in model_lower:
        return "google"
    
    # Cohere models
    if model_lower.startswith("command") or "cohere" in model_lower:
        return "cohere"
    
    return None


def validate_stagehand_config(config: StagehandConfig) -> dict[str, Any]:
    """
    Perform comprehensive validation of a StagehandConfig instance.
    
    Args:
        config: The StagehandConfig instance to validate
        
    Returns:
        Dictionary with validation results:
        - valid: bool - Whether the configuration is valid
        - errors: list - List of error messages
        - warnings: list - List of warning messages
        - recommendations: list - List of recommendations for improvement
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Validate model configuration
    if not config.model_name:
        result["errors"].append("model_name is required")
        result["valid"] = False
    
    # Validate API key configuration
    api_key_validation = validate_api_key_configuration(
        config.model_name, 
        config.model_api_key, 
        config.model_client_options
    )
    
    if not api_key_validation["valid"]:
        result["errors"].extend(api_key_validation["errors"])
        result["valid"] = False
    
    result["warnings"].extend(api_key_validation["warnings"])
    
    # Validate model_client_options if present
    if config.model_client_options:
        api_base = config.model_client_options.get("api_base") or config.model_client_options.get("baseURL")
        if api_base:
            url_validation = validate_api_base_url(api_base)
            if not url_validation["valid"]:
                result["errors"].append(f"Invalid api_base URL: {url_validation['error']}")
                result["valid"] = False
            else:
                result["warnings"].extend(url_validation["warnings"])
    
    # Validate verbose level
    if config.verbose is not None and not (0 <= config.verbose <= 2):
        result["errors"].append("verbose must be 0 (ERROR), 1 (INFO), or 2 (DEBUG)")
        result["valid"] = False
    
    # Validate timeout settings
    if config.dom_settle_timeout_ms is not None and config.dom_settle_timeout_ms < 0:
        result["errors"].append("dom_settle_timeout_ms must be non-negative")
        result["valid"] = False
    
    # Validate browser launch options
    if config.local_browser_launch_options:
        browser_validation = validate_browser_launch_options(config.local_browser_launch_options)
        result["warnings"].extend(browser_validation["warnings"])
        if browser_validation["errors"]:
            result["errors"].extend(browser_validation["errors"])
            result["valid"] = False
    
    # Add recommendations
    if config.verbose == 2:
        result["recommendations"].append("Debug logging (verbose=2) may impact performance in production")
    
    if not config.enable_caching:
        result["recommendations"].append("Consider enabling caching for better performance")
    
    if config.experimental:
        result["warnings"].append("Experimental features are enabled - use with caution in production")
    
    return result


def validate_browser_launch_options(options: dict[str, Any]) -> dict[str, Any]:
    """
    Validate browser launch options.
    
    Args:
        options: Browser launch options dictionary
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "errors": [],
        "warnings": []
    }
    
    if not isinstance(options, dict):
        result["errors"].append("local_browser_launch_options must be a dictionary")
        return result
    
    # Validate headless option
    if "headless" in options and not isinstance(options["headless"], bool):
        result["errors"].append("headless option must be a boolean")
    
    # Validate viewport
    if "viewport" in options:
        viewport = options["viewport"]
        if not isinstance(viewport, dict):
            result["errors"].append("viewport must be a dictionary")
        else:
            if "width" in viewport and (not isinstance(viewport["width"], int) or viewport["width"] <= 0):
                result["errors"].append("viewport width must be a positive integer")
            if "height" in viewport and (not isinstance(viewport["height"], int) or viewport["height"] <= 0):
                result["errors"].append("viewport height must be a positive integer")
    
    # Validate args
    if "args" in options:
        args = options["args"]
        if not isinstance(args, list):
            result["errors"].append("args must be a list")
        elif not all(isinstance(arg, str) for arg in args):
            result["errors"].append("all args must be strings")
    
    # Validate user_data_dir
    if "user_data_dir" in options:
        user_data_dir = options["user_data_dir"]
        if not isinstance(user_data_dir, str):
            result["errors"].append("user_data_dir must be a string")
    
    # Validate downloads_path
    if "downloads_path" in options:
        downloads_path = options["downloads_path"]
        if not isinstance(downloads_path, str):
            result["errors"].append("downloads_path must be a string")
    
    return result


def create_helpful_error_message(validation_result: dict[str, Any], config_context: str = "") -> str:
    """
    Create a helpful error message from validation results.
    
    Args:
        validation_result: Result from validation functions
        config_context: Additional context about where the error occurred
        
    Returns:
        Formatted error message with suggestions
    """
    if validation_result.get("valid", True):
        return ""
    
    errors = validation_result.get("errors", [])
    warnings = validation_result.get("warnings", [])
    recommendations = validation_result.get("recommendations", [])
    
    message_parts = []
    
    if config_context:
        message_parts.append(f"Configuration Error in {config_context}:")
    else:
        message_parts.append("Configuration Error:")
    
    # Add errors
    if errors:
        message_parts.append("\nErrors:")
        for error in errors:
            message_parts.append(f"  • {error}")
    
    # Add warnings
    if warnings:
        message_parts.append("\nWarnings:")
        for warning in warnings:
            message_parts.append(f"  • {warning}")
    
    # Add recommendations
    if recommendations:
        message_parts.append("\nRecommendations:")
        for rec in recommendations:
            message_parts.append(f"  • {rec}")
    
    # Add helpful examples
    if any("API key" in error for error in errors):
        message_parts.append("\nExample API key configuration:")
        message_parts.append("  config = StagehandConfig(")
        message_parts.append("      model_name='gpt-4o',")
        message_parts.append("      model_client_options={")
        message_parts.append("          'api_key': 'your-api-key-here'")
        message_parts.append("      }")
        message_parts.append("  )")
        message_parts.append("\nOr set environment variable: export OPENAI_API_KEY=your-api-key-here")
    
    if any("api_base" in error for error in errors):
        message_parts.append("\nExample custom API endpoint configuration:")
        message_parts.append("  config = StagehandConfig(")
        message_parts.append("      model_name='gpt-4o',")
        message_parts.append("      model_client_options={")
        message_parts.append("          'api_base': 'https://api.together.xyz/v1',")
        message_parts.append("          'api_key': 'your-together-api-key'")
        message_parts.append("      }")
        message_parts.append("  )")
    
    return "\n".join(message_parts)


# Default configuration instance for local browser automation
default_config = StagehandConfig()
