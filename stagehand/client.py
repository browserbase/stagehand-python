import asyncio
import json
import os
import shutil
import signal
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Literal, Optional

import httpx
from browserbase import Browserbase
from dotenv import load_dotenv
from playwright.async_api import (
    BrowserContext,
    Playwright,
    async_playwright,
)
from playwright.async_api import Page as PlaywrightPage

from .agent import Agent
from .config import StagehandConfig, default_config
from .context import StagehandContext
from .llm import LLMClient
from .logging import LogConfig, StagehandLogger, default_log_handler
from .metrics import StagehandFunctionName, StagehandMetrics
from .page import StagehandPage
from .schemas import AgentConfig
from .utils import (
    convert_dict_keys_to_camel_case,
    make_serializable,
)

load_dotenv()


class Stagehand:
    """
    Python client for interacting with a running Stagehand server and Browserbase remote headless browser.

    Now supports automatically creating a new session if no session_id is provided.
    You can provide a configuration via the 'config' parameter, or use individual parameters to override
    the default configuration values.
    """

    # Dictionary to store one lock per session_id
    _session_locks = {}

    # Flag to track if cleanup has been called
    _cleanup_called = False

    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        *,
        api_url: Optional[str] = None,
        model_api_key: Optional[str] = None,
        session_id: Optional[str] = None,
        env: Optional[Literal["BROWSERBASE", "LOCAL"]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        timeout_settings: Optional[httpx.Timeout] = None,
        use_rich_logging: bool = True,
        **config_overrides,
    ):
        """
        Initialize the Stagehand client.

        Args:
            config (Optional[StagehandConfig]): Configuration object. If not provided, uses default_config.
            api_url (Optional[str]): The running Stagehand server URL. Overrides config if provided.
            model_api_key (Optional[str]): Your model API key (e.g. OpenAI, Anthropic, etc.). Overrides config if provided.
            session_id (Optional[str]): Existing Browserbase session ID to connect to. Overrides config if provided.
            env (Optional[Literal["BROWSERBASE", "LOCAL"]]): Environment to run in. Overrides config if provided.
            httpx_client (Optional[httpx.AsyncClient]): Optional custom httpx.AsyncClient instance.
            timeout_settings (Optional[httpx.Timeout]): Optional custom timeout settings for httpx.
            use_rich_logging (bool): Whether to use Rich for colorized logging.
            **config_overrides: Additional configuration overrides to apply to the config.
        """
        # Start with provided config or default config
        if config is None:
            config = default_config

        # Apply any overrides
        overrides = {}
        if api_url is not None:
            # api_url isn't in config, handle separately
            pass
        if model_api_key is not None:
            # model_api_key isn't in config, handle separately
            pass
        if session_id is not None:
            overrides["browserbase_session_id"] = session_id
        if env is not None:
            overrides["env"] = env

        # Add any additional config overrides
        overrides.update(config_overrides)

        # Create final config with overrides
        if overrides:
            self.config = config.with_overrides(**overrides)
        else:
            self.config = config

        # Handle non-config parameters
        self.api_url = api_url or os.getenv("STAGEHAND_API_URL")
        self.model_api_key = model_api_key or os.getenv("MODEL_API_KEY")

        # Extract frequently used values from config for convenience
        self.browserbase_api_key = self.config.api_key or os.getenv(
            "BROWSERBASE_API_KEY"
        )
        self.browserbase_project_id = self.config.project_id or os.getenv(
            "BROWSERBASE_PROJECT_ID"
        )
        self.session_id = self.config.browserbase_session_id
        self.model_name = self.config.model_name
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

        self.httpx_client = httpx_client
        self.timeout_settings = timeout_settings or httpx.Timeout(
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

        # Create centralized log configuration
        self.log_config = LogConfig(
            verbose=self.verbose,
            use_rich=use_rich_logging,
            env=self.env,
            external_logger=self.config.logger or default_log_handler,
            quiet_dependencies=True,
        )

        # Initialize the centralized logger with the LogConfig
        self.on_log = self.log_config.external_logger
        self.logger = StagehandLogger(config=self.log_config)

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

        self._client: Optional[httpx.AsyncClient] = (
            None  # Used for server communication in BROWSERBASE
        )

        self._playwright: Optional[Playwright] = None
        self._browser = None
        self._context: Optional[BrowserContext] = None
        self._playwright_page: Optional[PlaywrightPage] = None
        self.page: Optional[StagehandPage] = None
        self.agent = None
        self.context: Optional[StagehandContext] = None

        self._initialized = False  # Flag to track if init() has run
        self._closed = False  # Flag to track if resources have been closed

        # Setup LLM client if LOCAL mode
        self.llm = None
        if self.env == "LOCAL":
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
        # Just call init() if not already done
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
            if not self._client:
                self._client = self.httpx_client or httpx.AsyncClient(
                    timeout=self.timeout_settings
                )

            # Create session if we don't have one
            if not self.session_id:
                await self._create_session()  # Uses self._client and api_url
                self.logger.debug(
                    f"Created new Browserbase session via Stagehand server: {self.session_id}"
                )
            else:
                self.logger.debug(
                    f"Using existing Browserbase session: {self.session_id}"
                )

            # Connect to remote browser via Browserbase SDK and CDP
            bb = Browserbase(api_key=self.browserbase_api_key)
            try:
                self.logger.debug(
                    f"Retrieving Browserbase session details for {self.session_id}..."
                )
                session = bb.sessions.retrieve(self.session_id)
                if session.status != "RUNNING":
                    raise RuntimeError(
                        f"Browserbase session {self.session_id} is not running (status: {session.status})"
                    )
                connect_url = session.connectUrl
            except Exception as e:
                self.logger.error(
                    f"Error retrieving or validating Browserbase session: {str(e)}"
                )
                await self.close()  # Clean up playwright if started
                raise

            self.logger.debug(f"Connecting to remote browser at: {connect_url}")
            try:
                self._browser = await self._playwright.chromium.connect_over_cdp(
                    connect_url
                )
            except Exception as e:
                self.logger.error(f"Failed to connect Playwright via CDP: {str(e)}")
                await self.close()
                raise

            existing_contexts = self._browser.contexts
            self.logger.debug(
                f"Existing contexts in remote browser: {len(existing_contexts)}"
            )
            if existing_contexts:
                self._context = existing_contexts[0]
            else:
                # This case might be less common with Browserbase but handle it
                self.logger.debug(
                    "No existing context found in remote browser, creating a new one."
                )
                self._context = (
                    await self._browser.new_context()
                )  # Should we pass options?

            self.context = await StagehandContext.init(self._context, self)

            # Access or create a page via StagehandContext
            existing_pages = self._context.pages
            self.logger.debug(f"Existing pages in context: {len(existing_pages)}")
            if existing_pages:
                self.logger.debug("Using existing page via StagehandContext")
                self.page = await self.context.get_stagehand_page(existing_pages[0])
                self._playwright_page = existing_pages[0]
            else:
                self.logger.debug("Creating a new page via StagehandContext")
                self.page = await self.context.new_page()
                self._playwright_page = self.page.page

        elif self.env == "LOCAL":
            cdp_url = self.local_browser_launch_options.get("cdp_url")

            if cdp_url:
                self.logger.info(f"Connecting to local browser via CDP URL: {cdp_url}")
                try:
                    self._browser = await self._playwright.chromium.connect_over_cdp(
                        cdp_url
                    )

                    if not self._browser.contexts:
                        raise RuntimeError(
                            f"No browser contexts found at CDP URL: {cdp_url}"
                        )
                    self._context = self._browser.contexts[0]
                    self.context = await StagehandContext.init(self._context, self)
                    self.logger.debug(
                        f"Connected via CDP. Using context: {self._context}"
                    )
                except Exception as e:
                    self.logger.error(
                        f"Failed to connect via CDP URL ({cdp_url}): {str(e)}"
                    )
                    await self.close()
                    raise
            else:
                self.logger.info("Launching new local browser context...")

                user_data_dir_option = self.local_browser_launch_options.get(
                    "user_data_dir"
                )
                if user_data_dir_option:
                    user_data_dir = Path(user_data_dir_option).resolve()
                else:
                    # Create temporary directory
                    temp_dir = tempfile.mkdtemp(prefix="stagehand_ctx_")
                    self._local_user_data_dir_temp = Path(temp_dir)
                    user_data_dir = self._local_user_data_dir_temp
                    # Create Default profile directory and Preferences file like in TS
                    default_profile_path = user_data_dir / "Default"
                    default_profile_path.mkdir(parents=True, exist_ok=True)
                    prefs_path = default_profile_path / "Preferences"
                    default_prefs = {"plugins": {"always_open_pdf_externally": True}}
                    try:
                        with open(prefs_path, "w") as f:
                            json.dump(default_prefs, f)
                        self.logger.debug(
                            f"Created temporary user_data_dir with default preferences: {user_data_dir}"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Failed to write default preferences to {prefs_path}: {e}"
                        )

                downloads_path_option = self.local_browser_launch_options.get(
                    "downloads_path"
                )
                if downloads_path_option:
                    downloads_path = str(Path(downloads_path_option).resolve())
                else:
                    downloads_path = str(Path.cwd() / "downloads")
                try:
                    os.makedirs(downloads_path, exist_ok=True)
                    self.logger.debug(f"Using downloads_path: {downloads_path}")
                except Exception as e:
                    self.logger.error(
                        f"Failed to create downloads_path {downloads_path}: {e}"
                    )

                # 3. Prepare Launch Options (translate keys if needed)
                launch_options = {
                    "headless": self.local_browser_launch_options.get(
                        "headless", False
                    ),
                    "accept_downloads": self.local_browser_launch_options.get(
                        "acceptDownloads", True
                    ),
                    "downloads_path": downloads_path,
                    "args": self.local_browser_launch_options.get(
                        "args",
                        [
                            # Common args from TS version
                            # "--enable-webgl",
                            # "--use-gl=swiftshader",
                            # "--enable-accelerated-2d-canvas",
                            "--disable-blink-features=AutomationControlled",
                            # "--disable-web-security",  # Use with caution
                        ],
                    ),
                    # Add more translations as needed based on local_browser_launch_options structure
                    "viewport": self.local_browser_launch_options.get(
                        "viewport", {"width": 1024, "height": 768}
                    ),
                    "locale": self.local_browser_launch_options.get("locale", "en-US"),
                    "timezone_id": self.local_browser_launch_options.get(
                        "timezoneId", "America/New_York"
                    ),
                    "bypass_csp": self.local_browser_launch_options.get(
                        "bypassCSP", True
                    ),
                    "proxy": self.local_browser_launch_options.get("proxy"),
                    "ignore_https_errors": self.local_browser_launch_options.get(
                        "ignoreHTTPSErrors", True
                    ),
                }
                launch_options = {
                    k: v for k, v in launch_options.items() if v is not None
                }

                # 4. Launch Context
                try:
                    self._context = (
                        await self._playwright.chromium.launch_persistent_context(
                            str(user_data_dir),  # Needs to be string path
                            **launch_options,
                        )
                    )
                    self.context = await StagehandContext.init(self._context, self)
                    self.logger.info("Local browser context launched successfully.")
                    self._browser = self._context.browser

                except Exception as e:
                    self.logger.error(
                        f"Failed to launch local browser context: {str(e)}"
                    )
                    await self.close()  # Clean up playwright and temp dir
                    raise

                cookies = self.local_browser_launch_options.get("cookies")
                if cookies:
                    try:
                        await self._context.add_cookies(cookies)
                        self.logger.debug(
                            f"Added {len(cookies)} cookies to the context."
                        )
                    except Exception as e:
                        self.logger.error(f"Failed to add cookies: {e}")

            # Apply stealth scripts
            await self._apply_stealth_scripts(self._context)

            # Get the initial page (usually one is created by default)
            if self._context.pages:
                self._playwright_page = self._context.pages[0]
                self.logger.debug("Using initial page from local context.")
            else:
                self.logger.debug("No initial page found, creating a new one.")
                self._playwright_page = await self._context.new_page()

            self.page = StagehandPage(self._playwright_page, self)
        else:
            # Should not happen due to __init__ validation
            raise RuntimeError(f"Invalid env value: {self.env}")

        self._initialized = True

    def agent(self, agent_config: AgentConfig) -> Agent:
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

        self.logger.debug(f"Creating Agent instance with config: {agent_config}")
        # Pass the required config directly to the Agent constructor
        return Agent(self, agent_config=agent_config)

    async def close(self):
        """
        Clean up resources.
        For BROWSERBASE: Ends the session on the server and stops Playwright.
        For LOCAL: Closes the local context, stops Playwright, and removes temporary directories.
        """
        if self._closed:
            return

        self.logger.debug("Closing resources...")

        if self.env == "BROWSERBASE":
            # --- BROWSERBASE Cleanup ---
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
                self.logger.debug(
                    "Cannot end server session: HTTP client not available."
                )

            # Close internal HTTPX client if it was created by Stagehand
            if self._client and not self.httpx_client:
                self.logger.debug("Closing the internal HTTPX client...")
                await self._client.aclose()
                self._client = None

        elif self.env == "LOCAL":
            if self._context:
                try:
                    self.logger.debug("Closing local browser context...")
                    await self._context.close()
                    self._context = None
                    self._browser = None  # Clear browser reference too
                except Exception as e:
                    self.logger.error(f"Error closing local context: {str(e)}")

            # Clean up temporary user data directory if created
            if self._local_user_data_dir_temp:
                try:
                    self.logger.debug(
                        f"Removing temporary user data directory: {self._local_user_data_dir_temp}"
                    )
                    shutil.rmtree(self._local_user_data_dir_temp)
                    self._local_user_data_dir_temp = None
                except Exception as e:
                    self.logger.error(
                        f"Error removing temporary directory {self._local_user_data_dir_temp}: {str(e)}"
                    )

        if self._playwright:
            try:
                self.logger.debug("Stopping Playwright...")
                await self._playwright.stop()
                self._playwright = None
            except Exception as e:
                self.logger.error(f"Error stopping Playwright: {str(e)}")

        self._closed = True
        self.logger.debug("All resources closed successfully")

    async def _create_session(self):
        """
        Create a new session by calling /sessions/start on the server.
        Depends on browserbase_api_key, browserbase_project_id, and model_api_key.
        """
        if not self.browserbase_api_key:
            raise ValueError("browserbase_api_key is required to create a session.")
        if not self.browserbase_project_id:
            raise ValueError("browserbase_project_id is required to create a session.")
        if not self.model_api_key:
            raise ValueError("model_api_key is required to create a session.")

        browserbase_session_create_params = (
            convert_dict_keys_to_camel_case(self.browserbase_session_create_params)
            if self.browserbase_session_create_params
            else None
        )

        payload = {
            "modelName": self.model_name,
            "verbose": self.log_config.get_remote_verbose(),
            "domSettleTimeoutMs": self.dom_settle_timeout_ms,
            "browserbaseSessionCreateParams": (
                browserbase_session_create_params
                if browserbase_session_create_params
                else {
                    "browserSettings": {
                        "blockAds": True,
                        "viewport": {
                            "width": 1024,
                            "height": 768,
                        },
                    },
                }
            ),
            "proxies": True,
        }

        # Add the new parameters if they have values
        if hasattr(self, "self_heal") and self.self_heal is not None:
            payload["selfHeal"] = self.self_heal

        if (
            hasattr(self, "wait_for_captcha_solves")
            and self.wait_for_captcha_solves is not None
        ):
            payload["waitForCaptchaSolves"] = self.wait_for_captcha_solves

        if hasattr(self, "act_timeout_ms") and self.act_timeout_ms is not None:
            payload["actTimeoutMs"] = self.act_timeout_ms

        if hasattr(self, "system_prompt") and self.system_prompt:
            payload["systemPrompt"] = self.system_prompt

        if hasattr(self, "model_client_options") and self.model_client_options:
            payload["modelClientOptions"] = self.model_client_options

        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "x-model-api-key": self.model_api_key,
            "Content-Type": "application/json",
            "x-language": "python",
        }

        client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
        async with client:
            resp = await client.post(
                f"{self.api_url}/sessions/start",
                json=payload,
                headers=headers,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to create session: {resp.text}")
            data = resp.json()
            self.logger.debug(f"Session created: {data}")
            if not data.get("success") or "sessionId" not in data.get("data", {}):
                raise RuntimeError(f"Invalid response format: {resp.text}")

            self.session_id = data["data"]["sessionId"]

    async def _execute(self, method: str, payload: dict[str, Any]) -> Any:
        """
        Internal helper to call /sessions/{session_id}/{method} with the given method and payload.
        Streams line-by-line, returning the 'result' from the final message (if any).
        """
        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            # Always enable streaming for better log handling
            "x-stream-response": "true",
        }
        if self.model_api_key:
            headers["x-model-api-key"] = self.model_api_key

        # Convert snake_case keys to camelCase for the API
        modified_payload = convert_dict_keys_to_camel_case(payload)

        client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)

        async with client:
            try:
                # Always use streaming for consistent log handling
                async with client.stream(
                    "POST",
                    f"{self.api_url}/sessions/{self.session_id}/{method}",
                    json=modified_payload,
                    headers=headers,
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_message = error_text.decode("utf-8")
                        self.logger.error(
                            f"[HTTP ERROR] Status {response.status_code}: {error_message}"
                        )
                        raise RuntimeError(
                            f"Request failed with status {response.status_code}: {error_message}"
                        )

                    result = None

                    async for line in response.aiter_lines():
                        # Skip empty lines
                        if not line.strip():
                            continue

                        try:
                            # Handle SSE-style messages that start with "data: "
                            if line.startswith("data: "):
                                line = line[len("data: ") :]

                            message = json.loads(line)
                            # Handle different message types
                            msg_type = message.get("type")

                            if msg_type == "system":
                                status = message.get("data", {}).get("status")
                                if status == "error":
                                    error_msg = message.get("data", {}).get(
                                        "error", "Unknown error"
                                    )
                                    self.logger.error(f"[ERROR] {error_msg}")
                                    raise RuntimeError(
                                        f"Server returned error: {error_msg}"
                                    )
                                elif status == "finished":
                                    result = message.get("data", {}).get("result")

                            elif msg_type == "log":
                                # Process log message using _handle_log
                                await self._handle_log(message)
                            else:
                                # Log any other message types
                                self.logger.debug(f"[UNKNOWN] Message type: {msg_type}")
                        except json.JSONDecodeError:
                            self.logger.debug(f"Could not parse line as JSON: {line}")

                    # Return the final result
                    return result
            except Exception as e:
                self.logger.error(f"[EXCEPTION] {str(e)}")
                raise

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
                "debug": 2,
                "info": 1,
                "error": 0,
            }

            # Convert string level to int if needed
            if isinstance(level_str, str):
                internal_level = level_map.get(level_str.lower(), 1)
            else:
                internal_level = min(level_str, 2)  # Ensure level is between 0-2

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
            level: Verbosity level (0=error, 1=info, 2=debug)
            category: Optional category for the message
            auxiliary: Optional auxiliary data to include
        """
        # Use the structured logger
        self.logger.log(message, level=level, category=category, auxiliary=auxiliary)

    async def _apply_stealth_scripts(self, context: BrowserContext):
        """Applies JavaScript init scripts to make the browser less detectable."""
        self.logger.debug("Applying stealth init scripts to the context...")
        # Adapted from the TypeScript version
        stealth_script = """
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

            // You might need to add more overrides depending on the detection methods used by websites.
            // For example, overriding Chrome runtime properties, canvas fingerprinting, etc.
        })();
        """
        try:
            await context.add_init_script(stealth_script)
            self.logger.debug("Stealth init script added successfully.")
        except Exception as e:
            self.logger.error(f"Failed to add stealth init script: {str(e)}")

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
