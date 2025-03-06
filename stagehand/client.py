import asyncio
import json
import logging
import time
from collections.abc import Awaitable
from typing import Any, Callable, Dict, Optional

import httpx
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from .config import StagehandConfig
from .page import StagehandPage
from .utils import default_log_handler, convert_dict_keys_to_camel_case
from .base import StagehandBase

load_dotenv()

logger = logging.getLogger(__name__)


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
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[
            Callable[[Dict[str, Any]], Awaitable[None]]
        ] = default_log_handler,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        debug_dom: Optional[bool] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        timeout_settings: Optional[httpx.Timeout] = None,
        model_client_options: Optional[Dict[str, Any]] = None,
        stream_response: Optional[bool] = None,
    ):
        """
        Initialize the Stagehand client.

        Args:
            config (Optional[StagehandConfig]): Optional configuration object encapsulating common parameters.
            server_url (Optional[str]): The running Stagehand server URL.
            session_id (Optional[str]): An existing Browserbase session ID.
            browserbase_api_key (Optional[str]): Your Browserbase API key.
            browserbase_project_id (Optional[str]): Your Browserbase project ID.
            model_api_key (Optional[str]): Your model API key (e.g. OpenAI, Anthropic, etc.).
            on_log (Optional[Callable[[Dict[str, Any]], Awaitable[None]]]): Async callback for log messages from the server.
            verbose (int): Verbosity level for logs.
            model_name (Optional[str]): Model name to use when creating a new session.
            dom_settle_timeout_ms (Optional[int]): Additional time for the DOM to settle (in ms).
            debug_dom (Optional[bool]): Whether to enable DOM debugging mode.
            httpx_client (Optional[httpx.AsyncClient]): Optional custom httpx.AsyncClient instance.
            timeout_settings (Optional[httpx.Timeout]): Optional custom timeout settings for httpx.
            model_client_options (Optional[Dict[str, Any]]): Optional model client options.
            stream_response (Optional[bool]): Whether to stream responses from the server.
        """
        super().__init__(
            config=config,
            server_url=server_url,
            session_id=session_id,
            browserbase_api_key=browserbase_api_key,
            browserbase_project_id=browserbase_project_id,
            model_api_key=model_api_key,
            on_log=on_log,
            verbose=verbose,
            model_name=model_name,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
            debug_dom=debug_dom,
            timeout_settings=timeout_settings,
            stream_response=stream_response,
            model_client_options=model_client_options,
        )
        
        self.httpx_client = httpx_client
        self.timeout_settings = timeout_settings or httpx.Timeout(
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
            self._log(f"Created lock for session {self.session_id}", level=3)
        return self._session_locks[self.session_id]

    async def __aenter__(self):
        self._log("Entering Stagehand context manager (__aenter__)...", level=3)
        # Just call init() if not already done
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._log("Exiting Stagehand context manager (__aexit__)...", level=3)
        await self.close()

    async def init(self):
        """
        Public init() to mimic the TS usage: await stagehand.init()
        Creates or resumes the session, starts Playwright, and sets up self.page.
        """
        if self._initialized:
            self._log("Stagehand is already initialized; skipping init()", level=3)
            return

        self._log("Initializing Stagehand...", level=3)

        if not self._client:
            self._client = self.httpx_client or httpx.AsyncClient(
                timeout=self.timeout_settings
            )

        # Check server health
        await self._check_server_health()

        # Create session if we don't have one
        if not self.session_id:
            await self._create_session()
            self._log(f"Created new session: {self.session_id}", level=3)

        # Start Playwright and connect to remote
        self._log("Starting Playwright...", level=3)
        self._playwright = await async_playwright().start()

        connect_url = (
            f"wss://connect.browserbase.com?apiKey={self.browserbase_api_key}"
            f"&sessionId={self.session_id}"
        )
        self._log(f"Connecting to remote browser at: {connect_url}", level=3)
        self._browser = await self._playwright.chromium.connect_over_cdp(connect_url)
        self._log(f"Connected to remote browser: {self._browser}", level=3)

        # Access or create a context
        existing_contexts = self._browser.contexts
        self._log(f"Existing contexts: {len(existing_contexts)}", level=3)
        if existing_contexts:
            self._context = existing_contexts[0]
        else:
            self._log("Creating a new context...", level=3)
            self._context = await self._browser.new_context()

        # Access or create a page
        existing_pages = self._context.pages
        self._log(f"Existing pages: {len(existing_pages)}", level=3)
        if existing_pages:
            self._log("Using existing page", level=3)
            self._playwright_page = existing_pages[0]
        else:
            self._log("Creating a new page...", level=3)
            self._playwright_page = await self._context.new_page()

        # Wrap with StagehandPage
        self._log("Wrapping Playwright page in StagehandPage", level=3)
        self.page = StagehandPage(self._playwright_page, self)

        self._initialized = True

    async def close(self):
        """
        Public close() to clean up resources—similar to __aexit__ in the context manager.
        """
        if self._closed:
            # Already closed
            return

        self._log("Closing resources...", level=3)

        # End the session on the server if we have a session ID
        if self.session_id:
            try:
                self._log(f"Ending session {self.session_id} on the server...", level=3)
                client = self.httpx_client or httpx.AsyncClient(
                    timeout=self.timeout_settings
                )
                headers = {
                    "x-bb-api-key": self.browserbase_api_key,
                    "x-bb-project-id": self.browserbase_project_id,
                    "Content-Type": "application/json",
                }

                async with client:
                    await self._execute("end", {"sessionId": self.session_id})
                    self._log(f"Session {self.session_id} ended successfully", level=3)
            except Exception as e:
                self._log(f"Error ending session: {str(e)}", level=3)

        if self._playwright:
            self._log("Stopping Playwright...", level=3)
            await self._playwright.stop()
            self._playwright = None

        if self._client and not self.httpx_client:
            self._log("Closing the internal HTTPX client...", level=3)
            await self._client.aclose()
            self._client = None

        self._closed = True

    async def _check_server_health(self, timeout: int = 10):
        """
        Ping /healthcheck to verify the server is available.
        Uses exponential backoff for retries.
        """
        start = time.time()
        attempt = 0
        while True:
            try:
                client = self.httpx_client or httpx.AsyncClient(
                    timeout=self.timeout_settings
                )
                async with client:
                    headers = {
                        "x-bb-api-key": self.browserbase_api_key,
                    }
                    resp = await client.get(
                        f"{self.server_url}/healthcheck", headers=headers
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "ok":
                            self._log("Healthcheck passed. Server is running.", level=3)
                            return
            except Exception as e:
                self._log(f"Healthcheck error: {str(e)}", level=3)

            if time.time() - start > timeout:
                raise TimeoutError(f"Server not responding after {timeout} seconds.")

            wait_time = min(
                2**attempt * 0.5, 5.0
            )  # Exponential backoff, capped at 5 seconds
            await asyncio.sleep(wait_time)
            attempt += 1

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
            "debugDom": self.debug_dom,
        }
        
        if hasattr(self, "model_client_options") and self.model_client_options:
            payload["modelClientOptions"] = self.model_client_options

        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "x-model-api-key": self.model_api_key,
            "Content-Type": "application/json",
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
            self._log(f"Session created: {data}", level=3)
            if not data.get("success") or "sessionId" not in data.get("data", {}):
                raise RuntimeError(f"Invalid response format: {resp.text}")

            self.session_id = data["data"]["sessionId"]

    async def _execute(self, method: str, payload: Dict[str, Any]) -> Any:
        """
        Internal helper to call /sessions/{session_id}/{method} with the given method and payload.
        Streams line-by-line, returning the 'result' from the final message (if any).
        """
        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "x-stream-response": str(self.streamed_response).lower(),
        }
        if self.model_api_key:
            headers["x-model-api-key"] = self.model_api_key
        
        modified_payload = dict(payload)
        if hasattr(self, "model_client_options") and self.model_client_options and "modelClientOptions" not in modified_payload:
            modified_payload["modelClientOptions"] = self.model_client_options
        
        # Convert snake_case keys to camelCase for the API
        modified_payload = convert_dict_keys_to_camel_case(modified_payload)
        
        client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
        self._log(f"\n==== EXECUTING {method.upper()} ====", level=3)
        self._log(
            f"URL: {self.server_url}/sessions/{self.session_id}/{method}", level=3
        )
        self._log(f"Payload: {modified_payload}", level=3)
        self._log(f"Headers: {headers}", level=3)
        
        async with client:
            try:
                if not self.streamed_response:
                    # For non-streaming responses, just return the final result
                    response = await client.post(
                        f"{self.server_url}/sessions/{self.session_id}/{method}",
                        json=modified_payload,
                        headers=headers,
                    )
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_message = error_text.decode("utf-8")
                        self._log(f"Error: {error_message}", level=3)
                        return None
                    
                    data = response.json()
                    if data.get("success"):
                        return data.get("data", {}).get("result")
                    else:
                        raise RuntimeError(f"Request failed: {data.get('error', 'Unknown error')}")

                # Handle streaming response
                async with client.stream(
                    "POST",
                    f"{self.server_url}/sessions/{self.session_id}/{method}",
                    json=modified_payload,
                    headers=headers,
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_message = error_text.decode("utf-8")
                        self._log(f"Error: {error_message}", level=3)
                        return None

                    self._log("Starting to process streaming response...", level=3)
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
                                if status == "finished":
                                    result = message.get("data", {}).get("result")
                                    self._log(
                                        f"FINISHED WITH RESULT: {result}", level=3
                                    )
                                    return result
                            elif msg_type == "log":
                                # Log message from data.message
                                log_msg = message.get("data", {}).get("message", "")
                                self._log(log_msg, level=3)
                                if self.on_log:
                                    await self.on_log(message)
                            else:
                                # Log any other message types
                                self._log(f"Unknown message type: {msg_type}", level=3)
                                if self.on_log:
                                    await self.on_log(message)

                        except json.JSONDecodeError:
                            self._log(f"Could not parse line as JSON: {line}", level=3)
                            continue
            except Exception as e:
                self._log(f"EXCEPTION IN _EXECUTE: {str(e)}")
                raise

        # If we get here without seeing a "finished" message, something went wrong
        self._log("==== ERROR: No 'finished' message received ====", level=3)
        raise RuntimeError(
            "Server connection closed without sending 'finished' message"
        )

    async def _handle_log(self, msg: Dict[str, Any]):
        """
        Handle a log line from the server. If on_log is set, call it asynchronously.
        """
        if self.verbose >= 1:
            self._log(f"Log message: {msg}", level=3)
        if self.on_log:
            try:
                await self.on_log(msg)
            except Exception as e:
                self._log(f"on_log callback error: {str(e)}", level=3)

    def _log(self, message: str, level: int = 1):
        """
        Internal logging with optional verbosity control.
        Maps internal level to Python logging levels.
        """
        if self.verbose >= level:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            formatted_msg = f"{timestamp}::[stagehand] {message}"

            if level == 1:
                logger.info(formatted_msg)
            elif level == 2:
                logger.warning(formatted_msg)
            else:
                logger.debug(formatted_msg)
