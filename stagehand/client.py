
# 2. Modify the Existing Stagehand Class
# In the current Stagehand class:
# Add a property page: Optional[StagehandPage] = None.
# This will be a reference to our new Pythonic Playwright page object.
# Initialize Playwright in Stagehand.__aenter__ (or in a dedicated method like init_playwright) if a local user wants to do normal browser operations.
# Connect to the remote Browserbase instance or start a local browser if needed.
# Create a Playwright page or context linked to the session_id.
# Set up self.page = StagehandPage(...) once the browser context is connected.
# This ensures that stagehand.page is a valid object for typical Playwright methods (page.goto(), page.wait_for_selector(), etc.).
# Proxy AI actions. When a user calls:
# await stagehand.page.act("search for something") → Under the hood, StagehandPage.act should call the existing _execute("act", ...) method to talk to NextJS.
# await stagehand.page.extract(...) → Similarly, pass to _execute("extract", ...).
# await stagehand.page.observe(...) → Pass to _execute("observe", ...).
# Meanwhile, all other page actions (like goto, click, wait_for_selector) are handled purely in Python via Playwright’s normal APIs.
# ---
# 4. Managing the Remote Browser Context
# Connect to Browserbase:
# If Browserbase provides a WebSocket/CDP endpoint for the remote browser, call browser = await playwright.chromium.connect_over_cdp(remote_endpoint) or a similar method. Then fetch the relevant context/page.
# Alternatively, if you must spin up a local browser and the NextJS side does the same, that’s more complicated. Generally, you want them to share the same underlying browser session.
# Tie in the session_id to ensure both the NextJS server and Python are operating on the same remote instance. That might happen automatically if you connect to an endpoint that’s pinned to the session, or you might have to pass the session ID as part of the browser’s connect arguments.
# Once connected, create or retrieve the page object:
# Or if you’re reusing an existing context from the NextJS session, you might do context.pages[0] to retrieve the page.

# . Updating the Existing Stagehand Workflow
# a. New Initialization Flow
# • In Stagehand.__aenter__, after (or before) _check_server_health(), also set up the Playwright connection:
# async def __aenter__(self):
#     self._client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
#     await self.init()
#     # Connect to remote playwright / or launch local.
#     self._playwright = await async_playwright().start()
#     self._browser = await self._playwright.chromium.connect_over_cdp(self.remote_cdp_endpoint)
#     # or however you're connecting with session_id
#     self._context = await self._browser.new_context()
#     self._playwright_page = await self._context.new_page()

#     # Wrap with StagehandPage
#     self.page = StagehandPage(self._playwright_page, self)

#     return self

# b. Proxy the AI Actions
# Existing methods like await self.act("some action") can remain. Under the hood they’ll do:

# # If called via Stagehand directly:
# async def act(self, action: str):
#     return await self.page.act(action)

# Then page.act calls _execute("act", ...). So you have a single path for all AI calls, but now they exist on both Stagehand itself and the new StagehandPage.

# 6. Handling Edge Cases
# Synchronization: Ensuring local Python operations with the page do not conflict with the NextJS operations. If NextJS is also controlling the page, you’ll want to handle concurrency carefully.
# Session expiry or reloading: If the NextJS side tears down the session, ensure the Python side re-initializes or fails gracefully.
# Error handling: If a user calls Python’s page.goto(...) but no remote browser is actually connected, define a good exception path.
# ---
# 7. Summary
# By adding a custom StagehandPage class (that either subclasses or proxies Playwright’s own Page), we can expose a Pythonic browser automation interface in the Stagehand library. Normal Playwright methods (e.g. wait_for_selector, click) stay local and synchronous. The special AI-based instructions (act, extract, observe) get redirected to your existing NextJS-based _execute calls. This consolidates everything into a single Python interface:
# • Users do:

#   async with Stagehand(...) as sh:
#       await sh.page.goto("https://example.com")
#       el = await sh.page.wait_for_selector("#my-element")
#       await sh.page.act("click the button to continue")
# • Internally, goto, wait_for_selector, etc. call real Playwright. act calls _execute → NextJS AI flow.
# This approach combines the power of local Pythonic Playwright with your existing “AI action” approach, preserving backward compatibility while adding a straightforward user experience for normal browser automation.
import asyncio
import json
import time
import httpx
import os
import logging
from typing import Optional, Dict, Any, Callable, Awaitable, List, Union
from pydantic import BaseModel
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from .playwright_proxy import StagehandPage

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
        on_log: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
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

        self.server_url = server_url or os.getenv("SERVER_URL", "http://localhost:3000")
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
            connect=10.0,  # connection timeout
            read=120.0,    # read timeout
            write=10.0,    # write timeout
            pool=10.0,     # pool timeout
        )
        self._client: Optional[httpx.AsyncClient] = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._playwright_page = None
        self.page: Optional[StagehandPage] = None

        # Validate essential fields if session_id was given;
        # if session_id is not provided, we'll create one later.
        if self.session_id:
            if not self.browserbase_api_key:
                raise ValueError("browserbase_api_key is required (or set BROWSERBASE_API_KEY in env).")
            if not self.browserbase_project_id:
                raise ValueError("browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env).")

    async def __aenter__(self):
        """Initialize the httpx client and session when entering context."""
        self._client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
        await self.init()
        
        # Set up Playwright connection
        self._playwright = await async_playwright().start()
        
        # TODO - use browserbase python SDK here?

        # Connect to Browserbase CDP endpoint
        connect_url = f"wss://connect.browserbase.com?apiKey={self.browserbase_api_key}&sessionId={self.session_id}"
        self._browser = await self._playwright.chromium.connect_over_cdp(connect_url)
        
        # Get or create browser context and page
        # TODO - will this be handled here or on BB?
        self._context = self._browser.contexts()[0] if self._browser.contexts() else await self._browser.new_context()
        self._playwright_page = self._context.pages[0] if self._context.pages else await self._context.new_page()
        
        # Create StagehandPage wrapper
        self.page = StagehandPage(self._playwright_page, self)
        
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        if self._playwright_page:
            await self._playwright_page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        if self._client and not self.httpx_client:  # Only close if we created it
            await self._client.aclose()
        self._client = None

    async def init(self):
        """
        Confirm the server is up by pinging /api/healthcheck.
        If no session_id is provided, create a new session using /api/start-session.
        """
        await self._check_server_health()

        if not self.session_id:
            await self._create_session()
            self._log(f"Created new session: {self.session_id}", level=1)

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
            raise ValueError("openai_api_key is required as modelApiKey to create a session.")

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
            "Content-Type": "application/json"
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

    async def _execute(self, method: str, args: List[Any]) -> Any:
        """
        Internal helper to call /api/execute with the given method and args.
        Streams line-by-line, returning the 'result' from the final message (if any).
        """
        payload = {
            "method": method,
            "args": args,
        }

        headers = {
            "browserbase-session-id": self.session_id,
            "browserbase-api-key": self.browserbase_api_key,
            "browserbase-project-id": self.browserbase_project_id,
            "Content-Type": "application/json",
        }
        if self.openai_api_key:
            headers["openai-api-key"] = self.openai_api_key

        # We'll collect final_result from the 'finished' system message
        final_result = None

        client = self.httpx_client or httpx.AsyncClient(timeout=self.timeout_settings)
        async with client:
            async with client.stream(
                "POST",
                f"{self.server_url}/api/execute",
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