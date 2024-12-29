import asyncio
import json
import time
import httpx
import os
import logging
from typing import Optional, Dict, Any, Callable, Awaitable, List, Union
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Stagehand:
    """
    Python client for interacting with a running BrowserBase/Stagehand server.
    
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
        :param server_url: The running Stagehand/BrowserBase server URL.
        :param session_id: An existing BrowserBase session ID (if you already have one).
        :param browserbase_api_key: Your BrowserBase API key.
        :param browserbase_project_id: Your BrowserBase project ID.
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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
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

    async def navigate(self, url: str):
        """
        Example convenience method wrapping 'goto'.
        """
        return await self._execute("goto", [url])

    async def act(self, action: str):
        """
        Example convenience method for 'act'.
        """
        return await self._execute("act", [{"action": action}])

    async def observe(self, options: Optional[Dict[str, Any]] = None):
        """
        Example convenience method for 'observe'.
        Options might include: {"timeoutMs": 5000} etc.
        """
        return await self._execute("observe", [options or {}])

    async def extract(
        self,
        instruction: str,
        schema: Union[Dict[str, Any], type(BaseModel)],
        **kwargs
    ) -> Any:
        """
        Extract data from the page using a JSON schema or a Pydantic model.
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            # Convert Pydantic schema to JSON schema
            schema_definition = schema.schema()
        elif isinstance(schema, dict):
            schema_definition = schema
        else:
            raise ValueError("schema must be a dict or a Pydantic model class.")

        # Build args object
        args_obj = {"instruction": instruction, "schemaDefinition": schema_definition}
        # Merge any additional kwargs (like url, modelName, etc.)
        args_obj.update(kwargs)

        return await self._execute("extract", [args_obj])

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
                        
                        # Log non-system messages
                        if message.get("type") != "system":
                            self._log(
                                message.get("data", {}).get("message", {}).get("message", ""),
                                level=message.get("data", {}).get("message", {}).get("level", 1),
                            )
                            continue

                        # Handle system messages
                        if message.get("type") == "system":
                            status = message.get("data", {}).get("status")
                            
                            if status == "finished":
                                return message.get("data", {}).get("result")

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