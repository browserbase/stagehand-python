import asyncio
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Optional

import nest_asyncio
from dotenv import load_dotenv
from playwright.async_api import (
    BrowserContext,
    Playwright,
    async_playwright,
)
from playwright.async_api import Page as PlaywrightPage

from .agent import Agent
from .browser import (
    cleanup_browser_resources,
    connect_browser,
)
from .config import StagehandConfig, StagehandConfigError, default_config, validate_stagehand_config, create_helpful_error_message
from .context import StagehandContext
from .llm import LLMClient
from .logging import StagehandLogger, default_log_handler
from .metrics import StagehandFunctionName, StagehandMetrics
from .page import StagehandPage
from .utils import get_download_path

load_dotenv()


class LivePageProxy:
    """
    A proxy object that dynamically delegates all operations to the current active page.
    This mimics the behavior of the JavaScript Proxy in the original implementation.
    """

    def __init__(self, stagehand_instance):
        # Use object.__setattr__ to avoid infinite recursion
        object.__setattr__(self, "_stagehand", stagehand_instance)

    async def _ensure_page_stability(self):
        """Wait for any pending page switches to complete"""
        if hasattr(self._stagehand, "_page_switch_lock"):
            try:
                # Use wait_for for Python 3.10 compatibility (timeout prevents indefinite blocking)
                async def acquire_lock():
                    async with self._stagehand._page_switch_lock:
                        pass  # Just wait for any ongoing switches

                await asyncio.wait_for(acquire_lock(), timeout=30)
            except asyncio.TimeoutError:
                # Log the timeout and raise to let caller handle it
                if hasattr(self._stagehand, "logger"):
                    self._stagehand.logger.error(
                        "Timeout waiting for page stability lock", category="live_proxy"
                    )
                raise RuntimeError from asyncio.TimeoutError(
                    "Page stability lock timeout - possible deadlock detected"
                )

    def __getattr__(self, name):
        """Delegate all attribute access to the current active page."""
        stagehand = object.__getattribute__(self, "_stagehand")

        # Get the current page
        if hasattr(stagehand, "_page") and stagehand._page:
            page = stagehand._page
        else:
            raise RuntimeError("No active page available")

        # For async operations, make them wait for stability
        attr = getattr(page, name)
        if callable(attr) and asyncio.iscoroutinefunction(attr):
            # Don't wait for stability on navigation methods
            if name in ["goto", "reload", "go_back", "go_forward"]:
                return attr

            async def wrapped(*args, **kwargs):
                await self._ensure_page_stability()
                return await attr(*args, **kwargs)

            return wrapped
        return attr

    def __setattr__(self, name, value):
        """Delegate all attribute setting to the current active page."""
        if name.startswith("_"):
            # Internal attributes are set on the proxy itself
            object.__setattr__(self, name, value)
        else:
            stagehand = object.__getattribute__(self, "_stagehand")

            # Get the current page
            if hasattr(stagehand, "_page") and stagehand._page:
                page = stagehand._page
            else:
                raise RuntimeError("No active page available")

            # Set the attribute on the page
            setattr(page, name, value)

    def __dir__(self):
        """Return attributes of the current active page."""
        stagehand = object.__getattribute__(self, "_stagehand")

        if hasattr(stagehand, "_page") and stagehand._page:
            page = stagehand._page
        else:
            return []

        return dir(page)

    def __repr__(self):
        """Return representation of the current active page."""
        stagehand = object.__getattribute__(self, "_stagehand")

        if hasattr(stagehand, "_page") and stagehand._page:
            return f"<LivePageProxy -> {repr(stagehand._page)}>"
        else:
            return "<LivePageProxy -> No active page>"


class Stagehand:
    """
    Main Stagehand class for local browser automation.
    """

    _cleanup_called = False

    def __init__(
        self,
        config: StagehandConfig = default_config,
        **config_overrides,
    ):
        """
        Initialize the Stagehand client for local browser automation.

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

        # Handle model-related settings
        self.model_client_options = self.config.model_client_options or {}
        self.model_api_key = self.config.model_api_key or os.getenv("MODEL_API_KEY")

        self.model_name = self.config.model_name

        # Extract frequently used values from config for convenience
        self.dom_settle_timeout_ms = self.config.dom_settle_timeout_ms
        self.self_heal = self.config.self_heal
        self.wait_for_captcha_solves = self.config.wait_for_captcha_solves
        self.system_prompt = self.config.system_prompt
        self.verbose = self.config.verbose
        self.local_browser_launch_options = (
            self.config.local_browser_launch_options or {}
        )
        
        # Handle API key configuration with better validation
        if self.model_api_key:
            # If api_key is provided directly, use it
            pass
        else:
            # Try to extract API key from model_client_options
            if "apiKey" in self.model_client_options:
                self.model_api_key = self.model_client_options["apiKey"]
            elif "api_key" in self.model_client_options:
                self.model_api_key = self.model_client_options["api_key"]
            else:
                # Try to get from environment based on model type
                self.model_api_key = self._get_api_key_from_environment()

        self._local_user_data_dir_temp: Optional[Path] = (
            None  # To store path if created temporarily
        )

        # Initialize metrics tracking
        self._local_metrics = StagehandMetrics()  # Internal storage for local metrics
        self._inference_start_time = 0  # To track inference time

        # Initialize the centralized logger with the specified verbosity
        self.on_log = self.config.logger or default_log_handler
        self.logger = StagehandLogger(
            verbose=self.verbose,
            external_logger=self.on_log,
            use_rich=self.config.use_rich_logging,
        )
        
        # Validate configuration after logger is initialized
        self._validate_configuration()

        # Register signal handlers for graceful shutdown
        self._register_signal_handlers()

        # Initialize browser-related instance variables
        self._playwright: Optional[Playwright] = None
        self._browser = None
        self._context: Optional[BrowserContext] = None
        self._playwright_page: Optional[PlaywrightPage] = None
        self._page: Optional[StagehandPage] = None
        self.context: Optional[StagehandContext] = None
        self.experimental = self.config.experimental

        self._initialized = False  # Flag to track if init() has run
        self._closed = False  # Flag to track if resources have been closed
        self._live_page_proxy = None  # Live page proxy
        self._page_switch_lock = asyncio.Lock()  # Lock for page stability

        # Setup enhanced LLM client with custom endpoint support
        llm_options = self.model_client_options.copy()
        
        # Remove API key variants from options to avoid conflicts
        llm_options.pop("api_key", None)
        llm_options.pop("apiKey", None)
        
        try:
            self.llm = LLMClient(
                stagehand_logger=self.logger,
                api_key=self.model_api_key,
                default_model=self.model_name,
                metrics_callback=self._handle_llm_metrics,
                **llm_options,
            )
            
            # Validate the LLM configuration
            validation_result = self.llm.validate_configuration()
            if not validation_result["valid"]:
                for error in validation_result["errors"]:
                    self.logger.error(f"LLM configuration error: {error}", category="llm")
            
            for warning in validation_result["warnings"]:
                self.logger.info(f"LLM configuration warning: {warning}", category="llm")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM client: {e}", category="llm")
            raise RuntimeError(f"Failed to initialize LLM client: {e}") from e

    def _get_api_key_from_environment(self) -> Optional[str]:
        """
        Try to get API key from environment variables based on the model type.
        
        Returns:
            API key from environment or None if not found
        """
        if not self.model_name:
            return None
            
        model_lower = self.model_name.lower()
        
        # Try to infer provider and get corresponding environment variable
        if model_lower.startswith("gpt-") or "openai" in model_lower:
            return os.getenv("OPENAI_API_KEY")
        elif model_lower.startswith("claude-") or "anthropic" in model_lower:
            return os.getenv("ANTHROPIC_API_KEY")
        elif "together" in model_lower:
            return os.getenv("TOGETHER_API_KEY")
        elif "groq" in model_lower:
            return os.getenv("GROQ_API_KEY")
        elif model_lower.startswith("gemini") or "google" in model_lower:
            return os.getenv("GOOGLE_API_KEY")
        
        # Fallback to generic environment variables
        return os.getenv("MODEL_API_KEY") or os.getenv("LLM_API_KEY")

    def _validate_configuration(self):
        """
        Validate the Stagehand configuration and raise helpful errors if invalid.
        
        Raises:
            StagehandConfigError: If configuration is invalid
        """
        try:
            validation_result = validate_stagehand_config(self.config)
            
            if not validation_result["valid"]:
                error_message = create_helpful_error_message(
                    validation_result, 
                    "Stagehand initialization"
                )
                raise StagehandConfigError(error_message)
            
            # Log warnings and recommendations
            for warning in validation_result["warnings"]:
                self.logger.info(f"Configuration warning: {warning}", category="config")
            
            for recommendation in validation_result["recommendations"]:
                self.logger.info(f"Configuration recommendation: {recommendation}", category="config")
                
        except Exception as e:
            if isinstance(e, StagehandConfigError):
                raise
            else:
                # Wrap other validation errors
                raise StagehandConfigError(f"Configuration validation failed: {e}") from e

    def _register_signal_handlers(self):
        """Register signal handlers for SIGINT and SIGTERM to ensure proper cleanup."""

        def cleanup_handler(sig, frame):
            # Prevent multiple cleanup calls
            if self.__class__._cleanup_called:
                return

            self.__class__._cleanup_called = True
            print(
                f"\n[{signal.Signals(sig).name}] received. Cleaning up browser resources..."
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
            print("Browser resources cleaned up successfully")
        except Exception as e:
            print(f"Error cleaning up browser resources: {str(e)}")
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
            self._local_metrics.act_prompt_tokens += prompt_tokens
            self._local_metrics.act_completion_tokens += completion_tokens
            self._local_metrics.act_inference_time_ms += inference_time_ms
        elif function_name == StagehandFunctionName.EXTRACT:
            self._local_metrics.extract_prompt_tokens += prompt_tokens
            self._local_metrics.extract_completion_tokens += completion_tokens
            self._local_metrics.extract_inference_time_ms += inference_time_ms
        elif function_name == StagehandFunctionName.OBSERVE:
            self._local_metrics.observe_prompt_tokens += prompt_tokens
            self._local_metrics.observe_completion_tokens += completion_tokens
            self._local_metrics.observe_inference_time_ms += inference_time_ms
        elif function_name == StagehandFunctionName.AGENT:
            self._local_metrics.agent_prompt_tokens += prompt_tokens
            self._local_metrics.agent_completion_tokens += completion_tokens
            self._local_metrics.agent_inference_time_ms += inference_time_ms

        # Always update totals
        self._local_metrics.total_prompt_tokens += prompt_tokens
        self._local_metrics.total_completion_tokens += completion_tokens
        self._local_metrics.total_inference_time_ms += inference_time_ms

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
                    f"Total metrics: {self._local_metrics.total_prompt_tokens} prompt tokens, "
                    f"{self._local_metrics.total_completion_tokens} completion tokens, "
                    f"{self._local_metrics.total_inference_time_ms}ms"
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
        Initialize Stagehand for local browser automation.
        
        This method starts Playwright, launches a local browser instance, and sets up the page.
        Only local browser mode is supported - no remote browser connections are available.
        
        Raises:
            RuntimeError: If local browser initialization fails
            asyncio.TimeoutError: If Playwright startup times out
        """
        if self._initialized:
            self.logger.debug("Stagehand is already initialized; skipping init()")
            return

        self.logger.debug("Initializing Stagehand for local browser automation...")

        # Initialize Playwright with timeout
        try:
            self._playwright = await asyncio.wait_for(
                async_playwright().start(), timeout=30.0  # 30 second timeout
            )
            self.logger.debug("Playwright initialized successfully")
        except asyncio.TimeoutError as e:
            self.logger.error("Playwright initialization timed out after 30 seconds")
            raise RuntimeError("Failed to initialize Playwright: timeout after 30 seconds") from e
        except Exception as e:
            self.logger.error(f"Failed to initialize Playwright: {str(e)}")
            raise RuntimeError(f"Failed to initialize Playwright: {str(e)}") from e

        # Connect to local browser
        try:
            (
                self._browser,
                self._context,
                self.context,
                self._page,
                self._local_user_data_dir_temp,
            ) = await connect_browser(
                self._playwright,
                self.local_browser_launch_options,
                self,
                self.logger,
            )
            self._playwright_page = self._page._page

        except Exception as e:
            self.logger.error(f"Failed to initialize local browser: {str(e)}")
            await self.close()
            raise RuntimeError(f"Failed to initialize Stagehand with local browser: {str(e)}") from e

        # Set up download behavior via CDP
        try:
            # Create CDP session for the page
            cdp_session = await self._context.new_cdp_session(self._playwright_page)
            # Enable download behavior
            await cdp_session.send(
                "Browser.setDownloadBehavior",
                {
                    "behavior": "allow",
                    "downloadPath": get_download_path(self),
                    "eventsEnabled": True,
                },
            )
            self.logger.debug("Set up CDP download behavior")
        except Exception as e:
            self.logger.info(f"Failed to set up CDP download behavior: {str(e)}")

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
        Clean up local browser resources.
        Closes the local browser context, stops Playwright, and removes temporary directories.
        """
        if self._closed:
            return

        self.logger.debug("Closing local browser resources...")

        # Use the centralized cleanup function for browser resources
        await cleanup_browser_resources(
            self._browser,
            self._context,
            self._playwright,
            self._local_user_data_dir_temp,
            self.logger,
        )

        self._closed = True



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

    def _set_active_page(self, stagehand_page: StagehandPage):
        """
        Internal method called by StagehandContext to update the active page.

        Args:
            stagehand_page: The StagehandPage to set as active
        """
        self._page = stagehand_page

    @property
    def page(self) -> Optional[StagehandPage]:
        """
        Get the current active page. This property returns a live proxy that
        always points to the currently focused page when multiple tabs are open.

        Returns:
            A LivePageProxy that delegates to the active StagehandPage or None if not initialized
        """
        if not self._initialized:
            return None

        # Create the live page proxy if it doesn't exist
        if not self._live_page_proxy:
            self._live_page_proxy = LivePageProxy(self)

        return self._live_page_proxy

    @property
    def metrics(self) -> StagehandMetrics:
        """
        Get the current metrics for local browser automation.
        
        Returns:
            StagehandMetrics: Current metrics tracking token usage and inference times
        """
        return self._local_metrics
