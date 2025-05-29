import asyncio
import json
from collections.abc import Awaitable
from typing import Any, Callable, Optional

import httpx
from browserbase import Browserbase
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from .agent import Agent
from .base import StagehandBase
from .config import StagehandConfig
from .context import StagehandContext
from .page import StagehandPage
from .schemas import AgentConfig
from .utils import StagehandLogger, convert_dict_keys_to_camel_case, default_log_handler

load_dotenv()

# Note: No need to create a global logger here since we're using StagehandLogger from utils.py


class Stagehand(StagehandBase):
    """
    Python client for interacting with a running Stagehand server and Browserbase remote headless browser.

    Now supports automatically creating a new session if no session_id is provided.
    You can also optionally provide a configuration via the 'config' parameter to centralize all parameters.
    """

    # Dictionary to store one lock per session_id
    _session_locks = {}

    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        server_url: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[
            Callable[[dict[str, Any]], Awaitable[None]]
        ] = default_log_handler,
        timeout_settings: Optional[httpx.Timeout] = None,
        model_client_options: Optional[dict[str, Any]] = None,
        stream_response: Optional[bool] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        use_rich_logging: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize the Stagehand client.

        Args:
            config (Optional[StagehandConfig]): Optional configuration object encapsulating common parameters.
            server_url (Optional[str]): The running Stagehand server URL.
            model_api_key (Optional[str]): Your model API key (e.g. OpenAI, Anthropic, etc.).
            on_log (Optional[Callable[[dict[str, Any]], Awaitable[None]]]): Async callback for log messages from the server.
            timeout_settings (Optional[httpx.Timeout]): Optional custom timeout settings for httpx.
            model_client_options (Optional[dict[str, Any]]): Optional model client options.
            stream_response (Optional[bool]): Whether to stream responses from the server.
            httpx_client (Optional[httpx.AsyncClient]): Optional custom httpx.AsyncClient instance.
            use_rich_logging (bool): Whether to use Rich for colorized logging.
            **kwargs: Additional configuration options passed to StagehandBase.
        """
        super().__init__(
            config=config,
            server_url=server_url,
            model_api_key=model_api_key,
            on_log=on_log,
            timeout_settings=timeout_settings,
            stream_response=stream_response,
            model_client_options=model_client_options,
            **kwargs,
        )

        # Initialize the centralized logger with the specified verbosity from base
        self.logger = StagehandLogger(
            verbose=self.verbose, external_logger=on_log, use_rich=use_rich_logging
        )

        # Store client-specific settings
        self.httpx_client = httpx_client
        # Use timeout_settings passed to base or default if None
        self.timeout_settings = self.timeout_settings or httpx.Timeout(
            connect=180.0,
            read=180.0,
            write=180.0,
            pool=180.0,
        )

        self._client: Optional[httpx.AsyncClient] = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._playwright_page = None
        self.page: Optional[StagehandPage] = None

        self._initialized = False  # Flag to track if init() has run
        self._closed = False  # Flag to track if resources have been closed

        # Validate essential fields if session_id was provided
        if self.session_id:
            if not self.browserbase_api_key:
                raise ValueError(
                    "browserbase_api_key is required (or set BROWSERBASE_API_KEY in env)."
                )
            if not self.browserbase_project_id:
                raise ValueError(
                    "browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env)."
                )

    def _get_lock_for_session(self) -> asyncio.Lock:
        """
        Return an asyncio.Lock for this session. If one doesn't exist yet, create it.
        """
        if self.session_id not in self._session_locks:
            self._session_locks[self.session_id] = asyncio.Lock()
            self.logger.debug(f"Created lock for session {self.session_id}")
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
        Public init() to mimic the TS usage: await stagehand.init()
        Creates or resumes the session, starts Playwright, and sets up self.page.
        """
        if self._initialized:
            self.logger.debug("Stagehand is already initialized; skipping init()")
            return

        self.logger.debug("Initializing Stagehand...")

        if not self._client:
            self._client = self.httpx_client or httpx.AsyncClient(
                timeout=self.timeout_settings
            )

        # Create session if we don't have one
        if not self.session_id:
            await self._create_session()
            self.logger.debug(f"Created new session: {self.session_id}")

        # Start Playwright and connect to remote
        self.logger.debug("Starting Playwright...")
        self._playwright = await async_playwright().start()
        bb = Browserbase(api_key=self.browserbase_api_key)
        try:
            session = bb.sessions.retrieve(self.session_id)
            connect_url = session.connectUrl
        except Exception as e:
            self.logger.error(f"Error retrieving session: {str(e)}")
            raise

        self.logger.debug(f"Connecting to remote browser at: {connect_url}")

        self._browser = await self._playwright.chromium.connect_over_cdp(connect_url)
        self.logger.debug(f"Connected to remote browser: {self._browser}")

        # Access or create a context
        existing_contexts = self._browser.contexts
        self.logger.debug(f"Existing contexts: {len(existing_contexts)}")
        if existing_contexts:
            self._context = existing_contexts[0]
        else:
            self.logger.debug("Creating a new context...")
            self._context = await self._browser.new_context()

        # Wrap the context with StagehandContext to ensure custom script injection
        self.stagehand_context = await StagehandContext.init(self._context, self)

        # Access or create a page via StagehandContext
        existing_pages = self._context.pages
        self.logger.debug(f"Existing pages: {len(existing_pages)}")
        if existing_pages:
            self.logger.debug("Using existing page via StagehandContext")
            self.page = await self.stagehand_context.get_stagehand_page(
                existing_pages[0]
            )
            self._playwright_page = existing_pages[0]
        else:
            self.logger.debug("Creating a new page via StagehandContext")
            self.page = await self.stagehand_context.new_page()
            self._playwright_page = self.page.page

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
        Public close() to clean up resources—similar to __aexit__ in the context manager.
        """
        if self._closed:
            # Already closed
            return

        self.logger.debug("Closing resources...")

        # End the session on the server if we have a session ID
        if self.session_id:
            try:
                self.logger.debug(f"Ending session {self.session_id} on the server...")
                client = self.httpx_client or httpx.AsyncClient(
                    timeout=self.timeout_settings
                )

                async with client:
                    await self._execute("end", {"sessionId": self.session_id})
                    self.logger.debug(f"Session {self.session_id} ended successfully")
            except Exception as e:
                self.logger.error(f"Error ending session: {str(e)}")

        if self._playwright:
            self.logger.debug("Stopping Playwright...")
            await self._playwright.stop()
            self._playwright = None

        if self._client and not self.httpx_client:
            self.logger.debug("Closing the internal HTTPX client...")
            await self._client.aclose()
            self._client = None

        self._closed = True

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
            },
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
                f"{self.server_url}/sessions/start",
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
        self.logger.debug(f"\n==== EXECUTING {method.upper()} ====")
        self.logger.debug(f"URL: {self.server_url}/sessions/{self.session_id}/{method}")
        self.logger.debug(f"Payload: {modified_payload}")
        self.logger.debug(f"Headers: {headers}")

        async with client:
            try:
                # Always use streaming for consistent log handling
                async with client.stream(
                    "POST",
                    f"{self.server_url}/sessions/{self.session_id}/{method}",
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

                    self.logger.debug("[STREAM] Processing server response")
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
                                    self.logger.debug(
                                        "[SYSTEM] Operation completed successfully"
                                    )
                            elif msg_type == "log":
                                # Process log message using _handle_log
                                await self._handle_log(message)
                            else:
                                # Log any other message types
                                self.logger.debug(f"[UNKNOWN] Message type: {msg_type}")
                        except json.JSONDecodeError:
                            self.logger.warning(f"Could not parse line as JSON: {line}")

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
