import asyncio
import json
import time
import httpx
from typing import Optional, Dict, Any, Callable, Awaitable, List, Union
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Stagehand:
    """
    Stagehand client for interacting with a running BrowserBase/Stagehand server.

    This version:
    - No longer attempts to automatically spawn an underlying Next.js server.
    - Instead, it just pings /api/healthcheck to verify availability.
    - Then it calls /api/execute with the required headers for each request (method + args).
    - Streams back the logs line by line, and calls on_log() if provided.
    - Returns the final 'result' from the server's “finished” message, if present.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:3000",
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        on_log: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        verbose: int = 1,
    ):
        """
        :param server_url: The running Stagehand/BrowserBase server URL.
        :param session_id: Your existing BrowserBase session ID.
        :param browserbase_api_key: Your BrowserBase API key.
        :param browserbase_project_id: Your BrowserBase project ID.
        :param openai_api_key: Your OpenAI API key (if needed).
        :param on_log: Async callback for log messages streamed from the server.
        :param verbose: Verbosity level for console logs from this client.
        """
        self.server_url = server_url
        self.session_id = session_id or os.getenv("BROWSERBASE_SESSION_ID")
        self.browserbase_api_key = browserbase_api_key or os.getenv("BROWSERBASE_API_KEY")
        self.browserbase_project_id = browserbase_project_id or os.getenv("BROWSERBASE_PROJECT_ID")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.on_log = on_log
        self.verbose = verbose

        # Validate essential fields
        if not self.session_id:
            raise ValueError("session_id is required (or set BROWSERBASE_SESSION_ID in env).")
        if not self.browserbase_api_key:
            raise ValueError("browserbase_api_key is required (or set BROWSERBASE_API_KEY in env).")
        if not self.browserbase_project_id:
            raise ValueError("browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env).")

    async def init(self):
        """
        Confirm the server is up by pinging /api/healthcheck.
        Raise an exception if the server is not responsive.
        """
        await self._check_server_health()

    async def _check_server_health(self, timeout: int = 10):
        """
        Ping /api/healthcheck to verify the server is available.
        """
        start = time.time()
        while True:
            try:
                async with httpx.AsyncClient() as client:
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
            await asyncio.sleep(0.5)

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

        # Configure longer timeouts for streaming responses
        timeout_settings = httpx.Timeout(
            connect=10.0,  # connection timeout
            read=120.0,    # read timeout
            write=10.0,   # write timeout
            pool=10.0,    # pool timeout
        )

        async with httpx.AsyncClient(timeout=timeout_settings) as client:
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
        """
        if self.verbose >= level:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"{timestamp}::[stagehand] {message}")