"""LLM client for model interactions."""

from typing import TYPE_CHECKING, Any, Callable, Optional

import litellm

from stagehand.metrics import get_inference_time_ms, start_inference_timer

if TYPE_CHECKING:
    from ..logging import StagehandLogger


class LLMClient:
    """
    Client for making LLM calls using the litellm library.
    Provides a simplified interface for chat completions.
    """

    def __init__(
        self,
        stagehand_logger: "StagehandLogger",
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        metrics_callback: Optional[Callable[[Any, int, Optional[str]], None]] = None,
        **kwargs: Any,  # To catch other potential litellm global settings
    ):
        """
        Initializes the LiteLLMClient.

        Args:
            stagehand_logger: StagehandLogger instance for centralized logging
            api_key: An API key for the default provider, if required.
                     It's often better to set provider-specific environment variables
                     (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY) which litellm reads automatically.
                     Passing api_key here might set litellm.api_key globally, which may
                     not be desired if using multiple providers.
            default_model: The default model to use if none is specified in chat_completion
                           (e.g., "gpt-4o", "claude-3-opus-20240229").
            metrics_callback: Optional callback to track metrics from responses
            **kwargs: Additional global settings for litellm (e.g., api_base).
                      See litellm documentation for available settings.
        """
        self.logger = stagehand_logger
        self.default_model = default_model
        self.metrics_callback = metrics_callback

        # Warning:Prefer environment variables for specific providers.
        if api_key:
            litellm.api_key = api_key

        # Apply other global settings if provided
        for key, value in kwargs.items():
            if hasattr(litellm, key):
                setattr(litellm, key, value)
                self.logger.debug(f"Set global litellm.{key}", category="llm")
            # Handle common aliases or expected config names if necessary
            elif key == "api_base":  # Example: map api_base if needed
                litellm.api_base = value
                self.logger.debug(
                    f"Set global litellm.api_base to {value}", category="llm"
                )

    def create_response(
        self,
        *,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        function_name: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a chat completion response using litellm.

        Args:
            messages: A list of message dictionaries, e.g., [{"role": "user", "content": "Hello"}].
            model: The specific model to use (e.g., "gpt-4o", "claude-3-opus-20240229").
                   Overrides the default_model if provided.
            function_name: The name of the Stagehand function calling this method (ACT, OBSERVE, etc.)
                   Used for metrics tracking.
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

        # Standardize gemini provider to google
        if completion_model.startswith("google/"):
            completion_model = completion_model.replace("google/", "gemini/")

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

        self.logger.debug(
            f"Calling litellm.completion with model={completion_model} and params: {filtered_params}",
            category="llm",
        )

        try:
            # Start tracking inference time
            start_time = start_inference_timer()

            # Use litellm's completion function
            response = litellm.completion(**filtered_params)

            # Calculate inference time
            inference_time_ms = get_inference_time_ms(start_time)

            # Update metrics if callback is provided
            if self.metrics_callback:
                self.metrics_callback(response, inference_time_ms, function_name)

            return response

        except Exception as e:
            self.logger.error(f"Error calling litellm.completion: {e}", category="llm")
            # Consider more specific exception handling based on litellm errors
            raise
