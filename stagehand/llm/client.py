"""LLM client for model interactions."""

import logging
from typing import Any, Optional

import litellm

# Configure logger for the module
logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for making LLM calls using the litellm library.
    Provides a simplified interface for chat completions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        **kwargs: Any,  # To catch other potential litellm global settings
    ):
        """
        Initializes the LiteLLMClient.

        Args:
            api_key: An API key for the default provider, if required.
                     It's often better to set provider-specific environment variables
                     (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY) which litellm reads automatically.
                     Passing api_key here might set litellm.api_key globally, which may
                     not be desired if using multiple providers.
            default_model: The default model to use if none is specified in chat_completion
                           (e.g., "gpt-4o", "claude-3-opus-20240229").
            **kwargs: Additional global settings for litellm (e.g., api_base).
                      See litellm documentation for available settings.
        """
        self.default_model = default_model

        # Warning:Prefer environment variables for specific providers.
        if api_key:
            litellm.api_key = api_key
            logger.warning(
                "Set global litellm.api_key. Prefer provider-specific environment variables."
            )

        # Apply other global settings if provided
        for key, value in kwargs.items():
            if hasattr(litellm, key):
                setattr(litellm, key, value)
                logger.debug(f"Set global litellm.{key}")
            # Handle common aliases or expected config names if necessary
            elif key == "api_base":  # Example: map api_base if needed
                litellm.api_base = value
                logger.debug(f"Set global litellm.api_base to {value}")

    def create_response(
        self,
        *,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a chat completion response using litellm.

        Args:
            messages: A list of message dictionaries, e.g., [{"role": "user", "content": "Hello"}].
            model: The specific model to use (e.g., "gpt-4o", "claude-3-opus-20240229").
                   Overrides the default_model if provided.
            **kwargs: Additional parameters to pass directly to litellm.completion
                      (e.g., temperature, max_tokens, stream=True, specific provider arguments).

        Returns:
            A dictionary containing the completion response from litellm, typically
            including choices, usage statistics, etc. Structure depends on the model
            provider and whether streaming is used.

        Raises:
            ValueError: If no model is specified (neither default nor in the call).
            Exception: Propagates exceptions from litellm.completion.
        """
        completion_model = model or self.default_model
        if not completion_model:
            raise ValueError(
                "No model specified for chat completion (neither default_model nor model argument)."
            )

        # Prepare arguments directly from kwargs
        params = {
            "model": completion_model,
            "messages": messages,
            **kwargs,  # Pass through any extra arguments
        }
        # Filter out None values only for keys explicitly present in kwargs to avoid sending nulls
        # unless they were intentionally provided as None.
        filtered_params = {
            k: v for k, v in params.items() if v is not None or k in kwargs
        }

        logger.debug(
            f"Calling litellm.completion with model={completion_model} and params: {filtered_params}"
        )
        try:
            # Use litellm's completion function
            response = litellm.completion(**filtered_params)
            return response

        except Exception as e:
            logger.error(f"Error calling litellm.completion: {e}", exc_info=True)
            # Consider more specific exception handling based on litellm errors
            raise

