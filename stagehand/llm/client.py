"""LLM client for model interactions using the OpenAI SDK."""

from typing import TYPE_CHECKING, Any, Callable, Optional

from openai import AsyncOpenAI

from stagehand.metrics import get_inference_time_ms, start_inference_timer

if TYPE_CHECKING:
    from ..logging import StagehandLogger


class LLMClient:
    """
    Client for making LLM calls using the OpenAI SDK.
    Provides a simplified interface for chat completions.
    """

    def __init__(
        self,
        stagehand_logger: "StagehandLogger",
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        metrics_callback: Optional[Callable[[Any, int, Optional[str]], None]] = None,
        **kwargs: Any,
    ):
        """
        Initializes the LLMClient.

        Args:
            stagehand_logger: StagehandLogger instance for centralized logging
            api_key: An API key for the OpenAI API or compatible provider.
            default_model: The default model to use if none is specified in chat_completion
                           (e.g., "gpt-4o", "gpt-4o-mini").
            metrics_callback: Optional callback to track metrics from responses
            **kwargs: Additional settings for the OpenAI client (e.g., base_url, timeout).
        """
        self.logger = stagehand_logger
        self.default_model = default_model
        self.metrics_callback = metrics_callback

        # Build client configuration
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key

        # Handle base URL configuration (support multiple naming conventions)
        base_url = kwargs.get("base_url") or kwargs.get("baseURL") or kwargs.get("api_base")
        if base_url:
            client_kwargs["base_url"] = base_url
            self.logger.debug(f"Set OpenAI client base_url to {base_url}", category="llm")

        # Handle timeout if provided
        if "timeout" in kwargs:
            client_kwargs["timeout"] = kwargs["timeout"]

        # Handle max_retries if provided
        if "max_retries" in kwargs:
            client_kwargs["max_retries"] = kwargs["max_retries"]

        # Handle default headers if provided
        if "default_headers" in kwargs:
            client_kwargs["default_headers"] = kwargs["default_headers"]

        # Initialize the async OpenAI client
        self.client = AsyncOpenAI(**client_kwargs)

    async def create_response(
        self,
        *,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        function_name: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a chat completion response using the OpenAI SDK.

        Args:
            messages: A list of message dictionaries, e.g., [{"role": "user", "content": "Hello"}].
            model: The specific model to use (e.g., "gpt-4o", "gpt-4o-mini").
                   Overrides the default_model if provided.
            function_name: The name of the Stagehand function calling this method (ACT, OBSERVE, etc.)
                   Used for metrics tracking.
            **kwargs: Additional parameters to pass directly to the OpenAI completions API
                      (e.g., temperature, max_tokens, response_format).

        Returns:
            The completion response from the OpenAI SDK.

        Raises:
            ValueError: If no model is specified (neither default nor in the call).
            Exception: Propagates exceptions from the OpenAI client.
        """
        completion_model = model or self.default_model
        if not completion_model:
            raise ValueError(
                "No model specified for chat completion (neither default_model nor model argument)."
            )

        # Handle provider prefixes - strip them for OpenAI SDK
        # Some configurations use prefixes like "openai/", etc.
        # For OpenAI SDK, we just use the model name directly
        if "/" in completion_model:
            # Extract just the model name after the provider prefix
            completion_model = completion_model.split("/", 1)[1]

        # Prepare arguments
        params = {
            "model": completion_model,
            "messages": messages,
        }

        # Handle response_format - convert Pydantic model to OpenAI format if needed
        response_format = kwargs.pop("response_format", None)
        if response_format is not None:
            if isinstance(response_format, type):
                # It's a Pydantic model class, use structured outputs
                params["response_format"] = response_format
            elif isinstance(response_format, dict):
                params["response_format"] = response_format
            else:
                params["response_format"] = response_format

        # Add remaining kwargs
        params.update(kwargs)

        # Filter out None values
        filtered_params = {k: v for k, v in params.items() if v is not None}

        # Fixes parameters for GPT-5 family of models
        if "gpt-5" in completion_model:
            filtered_params["temperature"] = 1

        self.logger.debug(
            f"Calling OpenAI client with model={completion_model}",
            category="llm",
        )

        try:
            # Start tracking inference time
            start_time = start_inference_timer()

            # Check if we're using structured output with a Pydantic model
            if "response_format" in filtered_params and isinstance(
                filtered_params["response_format"], type
            ):
                # Use beta.chat.completions.parse for structured outputs
                response = await self.client.beta.chat.completions.parse(
                    **filtered_params
                )
            else:
                # Use standard chat completions
                response = await self.client.chat.completions.create(**filtered_params)

            # Calculate inference time
            inference_time_ms = get_inference_time_ms(start_time)

            # Update metrics if callback is provided
            if self.metrics_callback:
                self.metrics_callback(response, inference_time_ms, function_name)

            return response

        except Exception as e:
            self.logger.error(f"Error calling OpenAI client: {e}", category="llm")
            raise
