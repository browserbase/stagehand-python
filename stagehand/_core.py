import os
import time
from typing import Any, Callable, Literal, Optional

from .config import StagehandConfig
from .metrics import StagehandFunctionName, StagehandMetrics
from .utils import StagehandLogger


class _StagehandCore:
    """
    Core functionality shared between sync and async implementations.
    No Playwright or HTTP calls here – only pure-Python utilities.
    """

    # Common JavaScript for browser stealth mode
    # TODO: remove this?
    STEALTH_JS = """
    (() => {
        // Override navigator.webdriver
        if (navigator.webdriver) {
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        }

        // Mock languages and plugins
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Avoid complex plugin mocking, just return a non-empty array like structure
        if (navigator.plugins instanceof PluginArray && navigator.plugins.length === 0) {
             Object.defineProperty(navigator, 'plugins', {
                get: () => Object.values({
                    'plugin1': { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                    'plugin2': { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
                    'plugin3': { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
                }),
            });
        }

        // Remove Playwright-specific properties from window
        try {
            delete window.__playwright_run; // Example property, check actual properties if needed
            delete window.navigator.__proto__.webdriver; // Another common place
        } catch (e) {}

        // Override permissions API (example for notifications)
        if (window.navigator && window.navigator.permissions) {
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters && parameters.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission });
                }
                // Call original for other permissions
                return originalQuery.apply(window.navigator.permissions, [parameters]);
            };
        }
    })();
    """

    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[Callable[[dict[str, Any]], Any]] = None,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        timeout_settings: Optional[Any] = None,
        model_client_options: Optional[dict[str, Any]] = None,
        stream_response: Optional[bool] = None,
        self_heal: Optional[bool] = None,
        wait_for_captcha_solves: Optional[bool] = None,
        system_prompt: Optional[str] = None,
        use_rich_logging: bool = True,
        env: Literal["BROWSERBASE", "LOCAL"] = None,
        local_browser_launch_options: Optional[dict[str, Any]] = None,
    ):
        """Common initialization for Stagehand clients."""
        self.server_url = server_url or os.getenv("STAGEHAND_SERVER_URL")

        # Process configuration parameters - from config object or individual args
        if config:
            self.browserbase_api_key = (
                config.api_key
                or browserbase_api_key
                or os.getenv("BROWSERBASE_API_KEY")
            )
            self.browserbase_project_id = (
                config.project_id
                or browserbase_project_id
                or os.getenv("BROWSERBASE_PROJECT_ID")
            )
            self.session_id = config.browserbase_session_id or session_id
            self.model_name = config.model_name or model_name
            self.dom_settle_timeout_ms = (
                config.dom_settle_timeout_ms or dom_settle_timeout_ms
            )
            self.self_heal = (
                config.self_heal if config.self_heal is not None else self_heal
            )
            self.wait_for_captcha_solves = (
                config.wait_for_captcha_solves
                if config.wait_for_captcha_solves is not None
                else wait_for_captcha_solves
            )
            self.system_prompt = config.system_prompt or system_prompt
        else:
            self.browserbase_api_key = browserbase_api_key or os.getenv(
                "BROWSERBASE_API_KEY"
            )
            self.browserbase_project_id = browserbase_project_id or os.getenv(
                "BROWSERBASE_PROJECT_ID"
            )
            self.session_id = session_id
            self.model_name = model_name
            self.dom_settle_timeout_ms = dom_settle_timeout_ms
            self.self_heal = self_heal
            self.wait_for_captcha_solves = wait_for_captcha_solves
            self.system_prompt = system_prompt

        # Handle model-related settings directly
        self.model_api_key = model_api_key or os.getenv("MODEL_API_KEY")
        self.model_client_options = model_client_options or {}
        if self.model_api_key and "apiKey" not in self.model_client_options:
            self.model_client_options["apiKey"] = self.model_api_key

        # Set up common state
        self.on_log = on_log
        self.timeout_settings = timeout_settings
        self.streamed_response = (
            stream_response if stream_response is not None else True
        )
        self.verbose = verbose
        self.env = env.upper() if env else "BROWSERBASE"
        self.local_browser_launch_options = local_browser_launch_options or {}

        # Initialize metrics tracking
        self.metrics = StagehandMetrics()
        self._inference_start_time = 0

        # Initialize the centralized logger with the specified verbosity
        self.logger = StagehandLogger(
            verbose=self.verbose, external_logger=on_log, use_rich=use_rich_logging
        )

        # Validate env
        if self.env not in ["BROWSERBASE", "LOCAL"]:
            raise ValueError("env must be either 'BROWSERBASE' or 'LOCAL'")

        # If using BROWSERBASE, session_id or creation params are needed
        if self.env == "BROWSERBASE":
            if not self.session_id:
                # Check if BROWSERBASE keys are present for session creation
                if not self.browserbase_api_key:
                    raise ValueError(
                        "browserbase_api_key is required for BROWSERBASE env when no session_id is provided (or set BROWSERBASE_API_KEY in env)."
                    )
                if not self.browserbase_project_id:
                    raise ValueError(
                        "browserbase_project_id is required for BROWSERBASE env when no session_id is provided (or set BROWSERBASE_PROJECT_ID in env)."
                    )
            elif self.session_id:
                # Validate essential fields if session_id was provided for BROWSERBASE
                if not self.browserbase_api_key:
                    raise ValueError(
                        "browserbase_api_key is required for BROWSERBASE env with existing session_id (or set BROWSERBASE_API_KEY in env)."
                    )
                if not self.browserbase_project_id:
                    raise ValueError(
                        "browserbase_project_id is required for BROWSERBASE env with existing session_id (or set BROWSERBASE_PROJECT_ID in env)."
                    )

        self._initialized = False
        self._closed = False

    # --- Metrics handling methods ---

    def start_inference_timer(self):
        """Start timer for tracking inference time."""
        self._inference_start_time = time.time()
        return self._inference_start_time

    def get_inference_time_ms(self) -> int:
        """Get elapsed inference time in milliseconds."""
        if self._inference_start_time == 0:
            return 0
        return int((time.time() - self._inference_start_time) * 1000)

    def update_metrics(
        self,
        function_name: StagehandFunctionName,
        prompt_tokens: int,
        completion_tokens: int,
        inference_time_ms: int,
    ):
        """
        Update metrics based on function name and token usage.

        Args:
            function_name: The function that generated the metrics
            prompt_tokens: Number of prompt tokens used
            completion_tokens: Number of completion tokens used
            inference_time_ms: Time taken for inference in milliseconds
        """
        if function_name == StagehandFunctionName.ACT:
            self.metrics.act_prompt_tokens += prompt_tokens
            self.metrics.act_completion_tokens += completion_tokens
            self.metrics.act_inference_time_ms += inference_time_ms
        elif function_name == StagehandFunctionName.EXTRACT:
            self.metrics.extract_prompt_tokens += prompt_tokens
            self.metrics.extract_completion_tokens += completion_tokens
            self.metrics.extract_inference_time_ms += inference_time_ms
        elif function_name == StagehandFunctionName.OBSERVE:
            self.metrics.observe_prompt_tokens += prompt_tokens
            self.metrics.observe_completion_tokens += completion_tokens
            self.metrics.observe_inference_time_ms += inference_time_ms
        elif function_name == StagehandFunctionName.AGENT:
            self.metrics.agent_prompt_tokens += prompt_tokens
            self.metrics.agent_completion_tokens += completion_tokens
            self.metrics.agent_inference_time_ms += inference_time_ms

        # Always update totals
        self.metrics.total_prompt_tokens += prompt_tokens
        self.metrics.total_completion_tokens += completion_tokens
        self.metrics.total_inference_time_ms += inference_time_ms

    def update_metrics_from_response(
        self,
        function_name: StagehandFunctionName,
        response: Any,
        inference_time_ms: Optional[int] = None,
    ):
        """
        Extract and update metrics from a litellm response.

        Args:
            function_name: The function that generated the response
            response: litellm response object
            inference_time_ms: Optional inference time if already calculated
        """
        try:
            # Check if response has usage information
            if hasattr(response, "usage") and response.usage:
                prompt_tokens = getattr(response.usage, "prompt_tokens", 0)
                completion_tokens = getattr(response.usage, "completion_tokens", 0)

                # Use provided inference time or calculate from timer
                time_ms = inference_time_ms or self.get_inference_time_ms()

                self.update_metrics(
                    function_name, prompt_tokens, completion_tokens, time_ms
                )

                # Log the usage at debug level
                self.logger.debug(
                    f"Updated metrics for {function_name}: {prompt_tokens} prompt tokens, "
                    f"{completion_tokens} completion tokens, {time_ms}ms"
                )
                self.logger.debug(
                    f"Total metrics: {self.metrics.total_prompt_tokens} prompt tokens, "
                    f"{self.metrics.total_completion_tokens} completion tokens, "
                    f"{self.metrics.total_inference_time_ms}ms"
                )
            else:
                # Try to extract from _hidden_params or other locations
                hidden_params = getattr(response, "_hidden_params", {})
                if hidden_params and "usage" in hidden_params:
                    usage = hidden_params["usage"]
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)

                    # Use provided inference time or calculate from timer
                    time_ms = inference_time_ms or self.get_inference_time_ms()

                    self.update_metrics(
                        function_name, prompt_tokens, completion_tokens, time_ms
                    )

                    # Log the usage at debug level
                    self.logger.debug(
                        f"Updated metrics from hidden_params for {function_name}: {prompt_tokens} prompt tokens, "
                        f"{completion_tokens} completion tokens, {time_ms}ms"
                    )
        except Exception as e:
            self.logger.debug(f"Failed to update metrics from response: {str(e)}")

    def _handle_llm_metrics(
        self, response: Any, inference_time_ms: int, function_name=None
    ):
        """
        Callback to handle metrics from LLM responses.

        Args:
            response: The litellm response object
            inference_time_ms: Time taken for inference in milliseconds
            function_name: The function that generated the metrics (name or enum value)
        """
        # Default to AGENT only if no function_name is provided
        if function_name is None:
            function_enum = StagehandFunctionName.AGENT
        # Convert string function_name to enum if needed
        elif isinstance(function_name, str):
            try:
                function_enum = getattr(StagehandFunctionName, function_name.upper())
            except (AttributeError, KeyError):
                # If conversion fails, default to AGENT
                function_enum = StagehandFunctionName.AGENT
        else:
            # Use the provided enum value
            function_enum = function_name

        self.update_metrics_from_response(function_enum, response, inference_time_ms)

    # --- API payload helpers ---

    def _build_headers(self, include_model_key: bool = True) -> dict:
        """
        Build HTTP headers for API requests.

        Args:
            include_model_key: Whether to include the model API key in headers

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "x-stream-response": str(self.streamed_response).lower(),
        }

        if include_model_key and self.model_api_key:
            headers["x-model-api-key"] = self.model_api_key

        return headers

    def _build_session_payload(self) -> dict:
        """
        Build the payload for creating a new session.

        Returns:
            Dictionary payload for session creation
        """
        payload = {
            "modelName": self.model_name,
            "domSettleTimeoutMs": self.dom_settle_timeout_ms,
            "verbose": self.verbose,
            "browserbaseSessionCreateParams": {
                "browserSettings": {
                    "blockAds": True,
                    "viewport": {
                        "width": 1024,
                        "height": 768,
                    },
                },
                "proxies": True,
            },
        }

        # Add optional parameters if they have values
        if hasattr(self, "self_heal") and self.self_heal is not None:
            payload["selfHeal"] = self.self_heal

        if (
            hasattr(self, "wait_for_captcha_solves")
            and self.wait_for_captcha_solves is not None
        ):
            payload["waitForCaptchaSolves"] = self.wait_for_captcha_solves

        if hasattr(self, "system_prompt") and self.system_prompt:
            payload["systemPrompt"] = self.system_prompt

        if hasattr(self, "model_client_options") and self.model_client_options:
            payload["modelClientOptions"] = self.model_client_options

        return payload

    def _log(
        self, message: str, level: int = 1, category: str = None, auxiliary: dict = None
    ):
        """
        Enhanced logging method that uses the StagehandLogger.

        Args:
            message: The message to log
            level: Verbosity level (0=error, 1=info, 2=detailed, 3=debug)
            category: Optional category for the message
            auxiliary: Optional auxiliary data to include
        """
        # Use the structured logger
        self.logger.log(message, level=level, category=category, auxiliary=auxiliary)

    async def _handle_log(self, msg: dict[str, Any]):
        """
        Handle a log message from the server.
        First attempts to use the on_log callback, then falls back to formatting the log locally.
        """
        try:
            log_data = msg.get("data", {})

            # Call user-provided callback with original data if available
            if self.on_log:
                if hasattr(self.on_log, "__await__"):  # Check if it's awaitable
                    await self.on_log(log_data)
                else:
                    self.on_log(log_data)  # Synchronous call
                return  # Early return after on_log to prevent double logging

            # Extract message, category, and level info
            message = log_data.get("message", "")
            category = log_data.get("category", "")
            level_str = log_data.get("level", "info")
            auxiliary = log_data.get("auxiliary", {})

            # Map level strings to internal levels
            level_map = {
                "debug": 3,
                "info": 1,
                "warning": 2,
                "error": 0,
            }

            # Convert string level to int if needed
            if isinstance(level_str, str):
                internal_level = level_map.get(level_str.lower(), 1)
            else:
                internal_level = min(level_str, 3)  # Ensure level is between 0-3

            # Handle the case where message itself might be a JSON-like object
            if isinstance(message, dict):
                # If message is a dict, just pass it directly to the logger
                formatted_message = message
            elif isinstance(message, str) and (
                message.startswith("{") and ":" in message
            ):
                # If message looks like JSON but isn't a dict yet, it will be handled by _format_fastify_log
                formatted_message = message
            else:
                # Regular message
                formatted_message = message

            # Log using the structured logger
            self.logger.log(
                formatted_message,
                level=internal_level,
                category=category,
                auxiliary=auxiliary,
            )

        except Exception as e:
            self.logger.error(f"Error processing log message: {str(e)}")
