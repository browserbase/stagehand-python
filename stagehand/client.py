import asyncio
import json
import time
import httpx
import os
import logging
from typing import Optional, Dict, Any, Callable, Awaitable
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from .page import StagehandPage
from .utils import default_log_handler

load_dotenv()

logger = logging.getLogger(__name__)

class Stagehand:
    """
    Python client for interacting with a running Stagehand server and Browserbase remote headless browser.
    
    Now supports automatically creating a new session if no session_id is provided.
    You can also optionally provide modelName, domSettleTimeoutMs, verbose, and debugDom,
    which will be sent to the server if a new session is created.
    """

    def __init__(
        self,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        on_log: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = default_log_handler,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        debug_dom: Optional[bool] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        timeout_settings: Optional[httpx.Timeout] = None,
    ):
        """
        :param server_url: The running Stagehand server URL.
        :param session_id: An existing Browserbase session ID (if you already have one).
        :param browserbase_api_key: Your Browserbase API key.
        :param browserbase_project_id: Your Browserbase project ID.
        :param openai_api_key: Your OpenAI API key (if needed, or used as the modelApiKey).
        :param on_log: Async callback for log messages streamed from the server.
        :param verbose: Verbosity level for console logs from this client.
        :param model_name: Model name to use when creating a new session (e.g., "gpt-4o").
        :param dom_settle_timeout_ms: Additional time for the DOM to settle.
        :param debug_dom: Whether or not to enable DOM debug mode.
        :param httpx_client: Optional custom httpx.AsyncClient instance.
        :param timeout_settings: Optional custom timeout settings for httpx.
        """

        self.server_url = server_url or os.getenv("STAGEHAND_SERVER_URL", "http://localhost:3000")
        self.session_id = session_id
        self.browserbase_api_key = browserbase_api_key or os.getenv("BROWSERBASE_API_KEY")
        self.browserbase_project_id = browserbase_project_id or os.getenv("BROWSERBASE_PROJECT_ID")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.on_log = on_log
        self.verbose = verbose
        self.model_name = model_name
        self.dom_settle_timeout_ms = dom_settle_timeout_ms
        self.debug_dom = debug_dom
        self.httpx_client = httpx_client
        self.timeout_settings = timeout_settings or httpx.Timeout(
            connect=90.0,  # connection timeout
            read=90.0,    # read timeout
            write=90.0,    # write timeout
            pool=90.0,     # pool timeout
        )

        self._client: Optional[httpx.AsyncClient] = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._playwright_page = None
        self.page: Optional[StagehandPage] = None

        self._initialized = False  # Flag to track if we've already run init()
        self._closed = False       # Flag to track if we've closed

        # Validate essential fields if session_id was given
        if self.session_id:
            if not self.browserbase_api_key:
                raise ValueError("browserbase_api_key is required (or set BROWSERBASE_API_KEY in env).")
            if not self.browserbase_project_id:
                raise ValueError("browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env).")

    async def __aenter__(self):
        self._log("Entering Stagehand context manager (__aenter__)...", level=1)
        # Just call init() if not already done
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._log("Exiting Stagehand context manager (__aexit__)...", level=1)
        await self.close()

    async def init(self):
        """
        Public init() to mimic the TS usage: await stagehand.init()
        Creates or resumes the session, starts Playwright, and sets up self.page.
        """
        if self._initialized:
            self._log("Stagehand is already initialized; skipping init()", level=2)
            return

        self._log("Initializing Stagehand...", level=1)

        if not self._client:
            self._client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)

        # Check server health
        await self._check_server_health()

        # Create session if we don't have one
        if not self.session_id:
            await self._create_session()
            self._log(f"Created new session: {self.session_id}", level=1)

        # Start Playwright and connect to remote
        self._log("Starting Playwright...", level=1)
        self._playwright = await async_playwright().start()

        connect_url = (
            f"wss://connect.browserbase.com?apiKey={self.browserbase_api_key}"
            f"&sessionId={self.session_id}"
        )
        self._log(f"Connecting to remote browser at: {connect_url}", level=1)
        self._browser = await self._playwright.chromium.connect_over_cdp(connect_url)
        self._log(f"Connected to remote browser: {self._browser}", level=1)
        
        # Access or create a context
        existing_contexts = self._browser.contexts
        self._log(f"Existing contexts: {len(existing_contexts)}", level=1)
        if existing_contexts:
            self._context = existing_contexts[0]
        else:
            self._log("Creating a new context...", level=1)
            self._context = await self._browser.new_context()

        # Access or create a page
        existing_pages = self._context.pages
        self._log(f"Existing pages: {len(existing_pages)}", level=1)
        if existing_pages:
            self._playwright_page = existing_pages[0]
        else:
            self._log("Creating a new page...", level=1)
            self._playwright_page = await self._context.new_page()

        # Wrap with StagehandPage
        self._log("Wrapping Playwright page in StagehandPage", level=1)
        self.page = StagehandPage(self._playwright_page, self)

        self._initialized = True

    async def close(self):
        """
        Public close() to clean up resources—similar to __aexit__ in the context manager.
        """
        if self._closed:
            # Already closed
            return

        self._log("Closing resources...", level=1)
        if self._playwright_page:
            self._log("Closing the Playwright page...", level=1)
            await self._playwright_page.close()
            self._playwright_page = None

        if self._context:
            self._log("Closing the context...", level=1)
            await self._context.close()
            self._context = None

        if self._browser:
            self._log("Closing the browser...", level=1)
            await self._browser.close()
            self._browser = None

        if self._playwright:
            self._log("Stopping Playwright...", level=1)
            await self._playwright.stop()
            self._playwright = None

        if self._client and not self.httpx_client:
            self._log("Closing the internal HTTPX client...", level=1)
            await self._client.aclose()
            self._client = None

        self._closed = True

    async def _check_server_health(self, timeout: int = 10):
        """
        Ping /api/healthcheck to verify the server is available.
        Uses exponential backoff for retries.
        """
        start = time.time()
        attempt = 0
        while True:
            try:
                client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
                async with client:
                    resp = await client.get(f"{self.server_url}/api/healthcheck")
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "ok":
                            self._log("Healthcheck passed. Server is running.", level=1)
                            return
            except Exception as e:
                self._log(f"Healthcheck error: {str(e)}", level=2)

            if time.time() - start > timeout:
                raise TimeoutError(f"Server not responding after {timeout} seconds.")
                
            wait_time = min(2 ** attempt * 0.5, 5.0)  # Exponential backoff, capped at 5 seconds
            await asyncio.sleep(wait_time)
            attempt += 1

    async def _create_session(self):
        """
        Create a new session by calling /api/start-session on the server.
        Depends on browserbase_api_key, browserbase_project_id, and openai_api_key.
        """
        if not self.browserbase_api_key:
            raise ValueError("browserbase_api_key is required to create a session.")
        if not self.browserbase_project_id:
            raise ValueError("browserbase_project_id is required to create a session.")
        if not self.openai_api_key:
            raise ValueError("openai_api_key is required as model-api-key to create a session.")

        payload = {
            "modelName": self.model_name,
            "domSettleTimeoutMs": self.dom_settle_timeout_ms,
            "verbose": self.verbose,
            "debugDom": self.debug_dom,
        }

        headers = {
            "browserbase-api-key": self.browserbase_api_key,
            "browserbase-project-id": self.browserbase_project_id,
            "model-api-key": self.openai_api_key,
            "Content-Type": "application/json",
        }

        client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
        async with client:
            resp = await client.post(
                f"{self.server_url}/api/start-session",
                json=payload,
                headers=headers,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to create session: {resp.text}")
            data = resp.json()
            if "sessionId" not in data:
                raise RuntimeError(f"Missing sessionId in response: {resp.text}")

            self.session_id = data["sessionId"]
    
    async def _execute(self, method: str, payload: Dict[str, Any]) -> Any:
        """
        Internal helper to call /api/execute with the given method and payload.
        Streams line-by-line, returning the 'result' from the final message (if any).
        """

        headers = {
            "browserbase-session-id": self.session_id,
            "browserbase-api-key": self.browserbase_api_key,
            "browserbase-project-id": self.browserbase_project_id,
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        }
        if self.openai_api_key:
            headers["openai-api-key"] = self.openai_api_key

        # We'll collect final_result from the 'finished' system message
        final_result = None
        client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
        async with client:
            async with client.stream(
                "POST", 
                f"{self.server_url}/api/{method}",
                json=payload,
                headers=headers,
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    self._log(f"Error: {error_text.decode('utf-8')}", level=2)
                    return None

                async for line in response.aiter_lines():
                    # Skip empty lines
                    if not line.strip():
                        continue

                    try:
                        # Handle SSE-style messages that start with "data: "
                        if line.startswith("data: "):
                            line = line[len("data: "):]
                        
                        message = json.loads(line)
                        logger.info(f"Message: {message}")
                        
                        # Handle different message types
                        msg_type = message.get("type")
                        
                        if msg_type == "system":
                            status = message.get("data", {}).get("status")
                            if status == "finished":
                                final_result = message.get("data", {}).get("result")
                                return final_result
                        elif msg_type == "log":
                            # Log message from data.message
                            log_msg = message.get("data", {}).get("message", "")
                            self._log(log_msg, level=1)
                            if self.on_log:
                                await self.on_log(message)
                        else:
                            # Log any other message types
                            self._log(f"Unknown message type: {msg_type}", level=2)
                            if self.on_log:
                                await self.on_log(message)

                    except json.JSONDecodeError:
                        self._log(f"Could not parse line as JSON: {line}", level=2)
                        continue

        return final_result

    async def _handle_log(self, msg: Dict[str, Any]):
        """
        Handle a log line from the server. If on_log is set, call it asynchronously.
        """
        if self.verbose >= 1:
            self._log(f"Log message: {msg}", level=1)
        if self.on_log:
            try:
                await self.on_log(msg)
            except Exception as e:
                self._log(f"on_log callback error: {str(e)}", level=2)

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