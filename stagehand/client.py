import asyncio
import subprocess
from typing import Optional, Dict, Any, Callable, Awaitable, Type
from pathlib import Path
import httpx
import json
from pydantic import BaseModel
import time

class Stagehand:
    def __init__(
        self,
        env: str = "LOCAL",
        server_url: str = "http://localhost:3000",
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
    ):
        self.env = env
        self.server_url = server_url
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

        self.server_process: Optional[subprocess.Popen] = None

    async def init(self):
        await self._ensure_server_running()

    async def _ensure_server_running(self):
        if self.server_process is None:
            # Start Next.js server in the background
            server_dir = Path(__file__).parent / "server"
            self.server_process = subprocess.Popen(
                ["npm", "run", "dev "],
                cwd=server_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # Wait for server to be ready
            await self._wait_for_server()

    async def _wait_for_server(self, timeout: int = 30):
        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{self.server_url}/api/health")
                    if response.status_code == 200:
                        return
            except:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError("Server failed to start")
                await asyncio.sleep(0.5)

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
        schema: Type[BaseModel],
        url: Optional[str] = None,
    ) -> Any:
        payload = {
            "instruction": instruction,
            "schema": schema.schema(),
            "url": url,
            "modelName": self.model_name,
        }
        response_data = await self._stream_request("/api/extract", payload)
        if response_data:
            return schema.parse_obj(response_data)
        else:
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
        payload["constructorOptions"] = {
            "env": self.env,
            "apiKey": self.api_key,
            "projectId": self.project_id,
            "verbose": self.verbose,
            "debugDom": self.debug_dom,
            "headless": self.headless,
            "domSettleTimeoutMs": self.dom_settle_timeout_ms,
            "enableCaching": self.enable_caching,
            "browserbaseResumeSessionID": self.browserbase_resume_session_id,
            "modelName": self.model_name,
            "modelClientOptions": self.model_client_options
        }
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
        try:
            return json.loads(line)
        except json.JSONDecodeError:
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
            self.server_process = None