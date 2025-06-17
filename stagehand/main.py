import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from playwright.async_api import (
    BrowserContext,
    Playwright,
    async_playwright,
)
from playwright.async_api import Page as PlaywrightPage

from .agent import Agent
from .api import _create_session, _execute
from .browser import (
    cleanup_browser_resources,
    connect_browserbase_browser,
    connect_local_browser,
)
from .config import StagehandConfig, default_config
from .context import StagehandContext
from .llm import LLMClient
from .logging import StagehandLogger, default_log_handler
from .metrics import StagehandFunctionName, StagehandMetrics
from .page import StagehandPage
from .utils import make_serializable

load_dotenv()


class Stagehand:
    """
    Main Stagehand class.
    """

    _session_locks = {}
    _cleanup_called = False

    def __init__(
        self,
        config: StagehandConfig = default_config,
        **config_overrides,
    ):
        """
        Initialize the Stagehand client.

        Args:
            config (Optional[StagehandConfig]): Configuration object. If not provided, uses default_config.
            **config_overrides: Additional configuration overrides to apply to the config.
        """

        # Apply any overrides
        overrides = {}

        # Add any additional config overrides
        overrides.update(config_overrides)

        # Create final config with overrides
        if overrides:
            self.config = config.with_overrides(**overrides)
        else:
            self.config = config

        # Handle non-config parameters
        self.api_url = self.config.api_url or os.getenv("STAGEHAND_API_URL")
        self.model_api_key = self.config.model_api_key or os.getenv("MODEL_API_KEY")
        self.model_name = self.config.model_name

        # Extract frequently used values from config for convenience
        self.browserbase_api_key = self.config.api_key or os.getenv(
            "BROWSERBASE_API_KEY"
        )
        self.browserbase_project_id = self.config.project_id or os.getenv(
            "BROWSERBASE_PROJECT_ID"
        )
        self.session_id = self.config.browserbase_session_id
        self.dom_settle_timeout_ms = self.config.dom_settle_timeout_ms
        self.self_heal = self.config.self_heal
        self.wait_for_captcha_solves = self.config.wait_for_captcha_solves
        self.system_prompt = self.config.system_prompt
        self.verbose = self.config.verbose
        self.env = self.config.env.upper() if self.config.env else "BROWSERBASE"
        self.local_browser_launch_options = (
            self.config.local_browser_launch_options or {}
        )

        # Handle model-related settings
        self.model_client_options = {}
        if self.model_api_key and "apiKey" not in self.model_client_options:
            self.model_client_options["apiKey"] = self.model_api_key

        # Handle browserbase session create params
        self.browserbase_session_create_params = make_serializable(
            self.config.browserbase_session_create_params
        )

        # Handle streaming response setting
        self.streamed_response = True

        self.timeout_settings = httpx.Timeout(
            connect=180.0,
            read=180.0,
            write=180.0,
            pool=180.0,
        )

        self._local_user_data_dir_temp: Optional[Path] = (
            None  # To store path if created temporarily
        )

        # Initialize metrics tracking
        self.metrics = StagehandMetrics()
        self._inference_start_time = 0  # To track inference time

        # Validate env
        if self.env not in ["BROWSERBASE", "LOCAL"]:
            raise ValueError("env must be either 'BROWSERBASE' or 'LOCAL'")

        # Initialize the centralized logger with the specified verbosity
        self.on_log = self.config.logger or default_log_handler
        self.logger = StagehandLogger(
            verbose=self.verbose,
            external_logger=self.on_log,
            use_rich=self.config.use_rich_logging,
        )

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
                if not self.model_api_key:
                    # Model API key needed if Stagehand server creates the session
                    self.logger.info(
                        "model_api_key is recommended when creating a new BROWSERBASE session to configure the Stagehand server's LLM."
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

        # Register signal handlers for graceful shutdown
        self._register_signal_handlers()

        self._client = httpx.AsyncClient(timeout=self.timeout_settings)

        self._playwright: Optional[Playwright] = None
        self._browser = None
        self._context: Optional[BrowserContext] = None
        self._playwright_page: Optional[PlaywrightPage] = None
        self.page: Optional[StagehandPage] = None
        self.context: Optional[StagehandContext] = None
        self.use_api = self.config.use_api
        self.experimental = self.config.experimental
        if self.experimental:
            self.use_api = False
        if (
            self.browserbase_session_create_params
            and self.browserbase_session_create_params.get("region")
            and self.browserbase_session_create_params.get("region") != "us-west-2"
        ):
            self.use_api = False

        self._initialized = False  # Flag to track if init() has run
        self._closed = False  # Flag to track if resources have been closed

        # Setup LLM client if LOCAL mode
        self.llm = None
        if not self.use_api:
            self.llm = LLMClient(
                stagehand_logger=self.logger,
                api_key=self.model_api_key,
                default_model=self.model_name,
                metrics_callback=self._handle_llm_metrics,
                **self.model_client_options,
            )

    def _register_signal_handlers(self):
        """Register signal handlers for SIGINT and SIGTERM to ensure proper cleanup."""

        def cleanup_handler(sig, frame):
            # Prevent multiple cleanup calls
            if self.__class__._cleanup_called:
                return

            self.__class__._cleanup_called = True
            print(
                f"\n[{signal.Signals(sig).name}] received. Ending Browserbase session..."
            )

            try:
                # Try to get the current event loop
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    # No event loop running - create one to run cleanup
                    print("No event loop running, creating one for cleanup...")
                    try:
                        asyncio.run(self._async_cleanup())
                    except Exception as e:
                        print(f"Error during cleanup: {str(e)}")
                    finally:
                        sys.exit(0)
                    return

                # Schedule cleanup in the existing event loop
                # Use call_soon_threadsafe since signal handlers run in a different thread context
                def schedule_cleanup():
                    task = asyncio.create_task(self._async_cleanup())
                    # Shield the task to prevent it from being cancelled
                    asyncio.shield(task)
                    # We don't need to await here since we're in call_soon_threadsafe

                loop.call_soon_threadsafe(schedule_cleanup)

            except Exception as e:
                print(f"Error during signal cleanup: {str(e)}")
                sys.exit(1)

        # Register signal handlers
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)

    async def _async_cleanup(self):
        """Async cleanup method called from signal handler."""
        try:
            await self.close()
            print(f"Session {self.session_id} ended successfully")
        except Exception as e:
            print(f"Error ending Browserbase session: {str(e)}")
        finally:
            # Force exit after cleanup completes (or fails)
            # Use os._exit to avoid any further Python cleanup that might hang
            os._exit(0)

    def start_inference_timer(self):
        """Start timer for tracking inference time."""
        self._inference_start_time = time.time()

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

    def _get_lock_for_session(self) -> asyncio.Lock:
        """
        Return an asyncio.Lock for this session. If one doesn't exist yet, create it.
        """
        if self.session_id not in self._session_locks:
            self._session_locks[self.session_id] = asyncio.Lock()
        return self._session_locks[self.session_id]

    async def __aenter__(self):
        self.logger.debug("Entering Stagehand context manager (__aenter__)...")
        # Just call init() if not already done
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Exiting Stagehand context manager (__aexit__)...")
        await self.close()

    async def init(self):
        """
        Public init() method.
        For BROWSERBASE: Creates or resumes the server session, starts Playwright, connects to remote browser.
        For LOCAL: Starts Playwright, launches a local persistent context or connects via CDP.
        Sets up self.page in both cases.
        """
        if self._initialized:
            self.logger.debug("Stagehand is already initialized; skipping init()")
            return

        self.logger.debug("Initializing Stagehand...")
        self.logger.debug(f"Environment: {self.env}")

        self._playwright = await async_playwright().start()

        if self.env == "BROWSERBASE":
            # Create session if we don't have one
            if self.use_api:
                if not self.session_id:
                    await self._create_session()  # Uses self._client and api_url
                    self.logger.debug(
                        f"Created new Browserbase session via Stagehand server: {self.session_id}"
                    )
                else:
                    self.logger.debug(
                        f"Using existing Browserbase session: {self.session_id}"
                    )

            # Connect to remote browser
            try:
                (
                    self._browser,
                    self._context,
                    self.context,
                    self.page,
                ) = await connect_browserbase_browser(
                    self._playwright,
                    self.session_id,
                    self.browserbase_api_key,
                    self,
                    self.logger,
                )
                self._playwright_page = self.page._page
            except Exception:
                await self.close()
                raise

        elif self.env == "LOCAL":
            # Connect to local browser
            try:
                (
                    self._browser,
                    self._context,
                    self.context,
                    self.page,
                    self._local_user_data_dir_temp,
                ) = await connect_local_browser(
                    self._playwright,
                    self.local_browser_launch_options,
                    self,
                    self.logger,
                )
                self._playwright_page = self.page._page
            except Exception:
                await self.close()
                raise
        else:
            # Should not happen due to __init__ validation
            raise RuntimeError(f"Invalid env value: {self.env}")

        self._initialized = True

    def agent(self, **kwargs) -> Agent:
        """
        Create an agent instance configured with the provided options.

        Args:
            agent_config (AgentConfig): Configuration for the agent instance.
                                          Provider must be specified or inferrable from the model.

        Returns:
            Agent: A configured Agent instance ready to execute tasks.
        """
        if not self._initialized:
            raise RuntimeError(
                "Stagehand must be initialized with await init() before creating an agent."
            )

        self.logger.debug(f"Creating Agent instance with config: {kwargs}")
        # Pass the required config directly to the Agent constructor
        return Agent(self, **kwargs)

    async def close(self):
        """
        Clean up resources.
        For BROWSERBASE: Ends the session on the server and stops Playwright.
        For LOCAL: Closes the local context, stops Playwright, and removes temporary directories.
        """
        if self._closed:
            return

        self.logger.debug("Closing resources...")

        if self.use_api:
            # --- BROWSERBASE Cleanup (API) ---
            # End the session on the server if we have a session ID
            if self.session_id and self._client:  # Check if client was initialized
                try:
                    self.logger.debug(
                        f"Attempting to end server session {self.session_id}..."
                    )
                    # Don't use async with here as it might close the client prematurely
                    # The _execute method will handle the request properly
                    result = await self._execute("end", {"sessionId": self.session_id})
                    self.logger.debug(
                        f"Server session {self.session_id} ended successfully with result: {result}"
                    )
                except Exception as e:
                    # Log error but continue cleanup
                    self.logger.error(
                        f"Error ending server session {self.session_id}: {str(e)}"
                    )
            elif self.session_id:
                self.logger.warning(
                    "Cannot end server session: HTTP client not available."
                )

            if self._client:
                self.logger.debug("Closing the internal HTTPX client...")
                await self._client.aclose()
                self._client = None

        # Use the centralized cleanup function for browser resources
        await cleanup_browser_resources(
            self._browser,
            self._context,
            self._playwright,
            self._local_user_data_dir_temp,
            self.logger,
        )

        self._closed = True

    async def _handle_log(self, msg: dict[str, Any]):
        """
        Handle a log message from the server.
        First attempts to use the on_log callback, then falls back to formatting the log locally.
        """
        try:
            log_data = msg.get("data", {})

            # Call user-provided callback with original data if available
            if self.on_log:
                await self.on_log(log_data)
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


# Bind the imported API methods to the Stagehand class
Stagehand._create_session = _create_session
Stagehand._execute = _execute
