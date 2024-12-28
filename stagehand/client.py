import asyncio
import subprocess
from typing import Optional, Dict, Any, Callable, Awaitable, Type
from pathlib import Path
import httpx
import json
from typing import Union
from pydantic import BaseModel
import time
import socket
import os
import json
import re
from dotenv import load_dotenv
# from utils import EXTRACT_SCHEMA_PROMPT
load_dotenv()

class Stagehand:
    def __init__(
        self,
        env: str = "LOCAL",
        server_url: Optional[str] = None,
        on_log: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        verbose: int = 1,
        debug_dom: bool = False,
        enable_caching: bool = False,
        model_name: str = "gpt-4o",
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        headless: bool = False,
        dom_settle_timeout_ms: Optional[int] = None,
        browserbase_resume_session_id: Optional[str] = None,
        model_client_options: Optional[Dict[str, Any]] = None,
        launch_server: bool = True,
    ):
        self.env = env
        self.server_url = server_url or os.getenv("STAGEHAND_SERVER_URL", "http://localhost:3000")
        self.on_log = on_log
        self.verbose = verbose
        self.debug_dom = debug_dom
        self.enable_caching = enable_caching
        self.model_name = model_name
        self.api_key = api_key
        self.project_id = project_id
        self.headless = headless
        self.dom_settle_timeout_ms = dom_settle_timeout_ms
        self.browserbase_resume_session_id = browserbase_resume_session_id
        self.model_client_options = model_client_options
        self.launch_server = launch_server

        self.server_process: Optional[subprocess.Popen] = None

    async def init(self):
        if self.launch_server:
            await self._ensure_server_running()


    async def _ensure_server_running(self):
        if self.server_process is None:
            # Check if port 3000 is available
            port = 3000
            while not await self._is_port_available(port):
                port += 1

            # Start Next.js server in the background
            server_dir = Path(__file__).parent / "server"
            print(f"Starting server in {server_dir} on port {port}")

            # Set environment variables including PORT
            env = os.environ.copy()
            env["PORT"] = str(port)
            env = {str(k): str(v) for k, v in env.items()}

            # Use asyncio subprocess to avoid blocking the event loop
            self.server_process = await asyncio.create_subprocess_exec(
                "npm",
                "run",
                "dev",
                cwd=str(server_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            # Update the server_url with the actual port
            self.server_url = f"http://localhost:{port}"

            # Create tasks to read stdout and stderr
            asyncio.create_task(self._read_stream(self.server_process.stdout, "Server output"))
            asyncio.create_task(self._read_stream(self.server_process.stderr, "Server error"))

            # Wait for server to be ready
            await self._wait_for_server()

    async def _is_port_available(self, port: int) -> bool:
        try:
            # Try to create a socket binding
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return True
        except OSError:
            return False

    async def _read_stream(self, stream: asyncio.StreamReader, prefix: str):
        buffer = ''
        while True:
            chunk = await stream.read(1024)
            if not chunk:
                if buffer:
                    self._log(f"{prefix}: {buffer}", level=1)
                break
            buffer += chunk.decode(errors='replace')
            *lines, buffer = buffer.split('\n')
            for line in lines:
                self._log(f"{prefix}: {line.strip()}", level=1)

    async def _wait_for_server(self, timeout: int = 30):
        print(f"Waiting for server to start on {self.server_url}")
        start_time = time.time()
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.server_url}/api/healthcheck")
                    if response.status_code == 200:
                        print("Server successfully started!")
                        return
                    else:
                        print(f"Server returned status code: {response.status_code}")
            except httpx.ConnectError:
                print("Connection refused - server not ready yet")
            except Exception as e:
                print(f"Error checking server status: {str(e)}")

            if time.time() - start_time > timeout:
                raise TimeoutError(f"Server failed to start after {timeout} seconds")

            await asyncio.sleep(0.5)
            print(f"Waiting for server to start on {self.server_url}")


    async def act(
        self,
        action: str,
        url: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        use_vision: bool = False,
        model_name: Optional[str] = None,
    ):
        cache_key = ("act", action, frozenset(variables.items()) if variables else None)
        if self.enable_caching and cache_key in self._cache:
            return self._cache[cache_key]

        if variables:
            for key, value in variables.items():
                action = action.replace(f"<|{key}|>", str(value))
        payload = {
            "action": action,
            "url": url,
            "variables": variables,
            "useVision": use_vision,
            "modelName": model_name or self.model_name,
        }
        result = await self._stream_request("/api/act", payload)
        if self.enable_caching:
            self._cache[cache_key] = result
        return result

    async def extract(
        self,
        instruction: str,
        schema: Union[Type[BaseModel], Dict[str, Any]],
        url: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Any:
        if isinstance(schema, dict):
            schema_definition = schema
            parse_response = False
        elif issubclass(schema, BaseModel):
            schema_definition = schema.schema()
            parse_response = True
        else:
            raise ValueError("schema must be a Pydantic model class or a dictionary")
        
        payload = {
            "instruction": instruction,
            "schemaDefinition": schema_definition,
            "url": url,
            "modelName": model_name or self.model_name,
        }
        print('payload', payload)
        try:
            response_data = await self._stream_request("/api/extract", payload)
            if response_data:
                if parse_response:
                    return schema.parse_obj(response_data)
                else:
                    return response_data
            else:
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def observe(
        self,
        instruction: str,
        url: Optional[str] = None,
        use_vision: bool = False,
        model_name: Optional[str] = None,
    ):
        payload = {
            "instruction": instruction,
            "url": url,
            "useVision": use_vision,
            "modelName": model_name or self.model_name,
        }
        response_data = await self._stream_request("/api/observe", payload)
        return response_data

    async def navigate(
        self,
        url: str
    ):
        payload = {
            "url": url,
        }
        response_data = await self._stream_request("/api/navigate", payload)
        return response_data
    
    async def _stream_request(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        constructor_options = {}
        if self.env:
            constructor_options["env"] = self.env
        if self.api_key:
            constructor_options["apiKey"] = self.api_key
        if self.project_id:
            constructor_options["projectId"] = self.project_id
        if self.verbose:
            constructor_options["verbose"] = self.verbose
        if self.debug_dom:
            constructor_options["debugDom"] = self.debug_dom
        if self.headless:
            constructor_options["headless"] = self.headless
        if self.dom_settle_timeout_ms:
            constructor_options["domSettleTimeoutMs"] = self.dom_settle_timeout_ms
        if self.enable_caching:
            constructor_options["enableCaching"] = self.enable_caching
        if self.browserbase_resume_session_id:
            constructor_options["browserbaseResumeSessionID"] = self.browserbase_resume_session_id
        if self.model_name:
            constructor_options["modelName"] = self.model_name
        if self.model_client_options:
            constructor_options["modelClientOptions"] = self.model_client_options

        if constructor_options:
            payload["constructorOptions"] = constructor_options
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", f"{self.server_url}{endpoint}", json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    self._log(f"Error: {error_text.decode('utf-8')}", level=2)
                    return None
                data = ""
                async for line in response.aiter_lines():
                    if line:
                        log_data = self._parse_log_line(line)
                        self._log(log_data.get("message", ""), level=1)
                        data += line
                return json.loads(data)



    def _parse_log_line(self, line: str) -> Dict[str, Any]:
        # Remove any leading/trailing whitespace
        line = line.strip()
        # If the line starts with '{' and ends with '}', it's likely a JSON object
        if line.startswith('{') and line.endswith('}'):
            try:
                return json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Problematic line: {repr(line)}")
        else:
            # Attempt to extract JSON from within the line
            json_match = re.search(r'({.*})', line)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic JSON extracted: {repr(json_match.group(1))}")
        # If all else fails, return the line as a message
        return {"message": line}

    def _log(self, message: str, level: int = 1, auxiliary: Dict[str, Any] = None):
        if self.verbose >= level:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            aux_str = json.dumps(auxiliary) if auxiliary else ""
            print(f"{timestamp}::[stagehand] {message} {aux_str}")
        if self.on_log:
            asyncio.create_task(self.on_log({
                "message": message,
                "level": level,
                "auxiliary": auxiliary,
                "timestamp": time.time(),
            }))

    async def close(self):
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            self.server_process = None