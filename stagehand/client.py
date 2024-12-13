# stagehand/client.py
import asyncio
import subprocess
from typing import Optional, Dict, Any, Callable, Awaitable
from pathlib import Path
import httpx
import json


class Stagehand:
    def __init__(
        self,
        env: str = "BROWSERBASE",
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        server_url: str = "http://localhost:3000",
        on_log: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    ):
        self.env = env
        self.api_key = api_key
        self.project_id = project_id
        self.server_url = server_url
        self.on_log = on_log

        self.server_process: Optional[subprocess.Popen] = None

    async def init(self):
        await self._ensure_server_running()

    async def _ensure_server_running(self):
        if self.server_process is None:
            # Start Next.js server in the background
            server_dir = Path(__file__).parent / "server"
            self.server_process = subprocess.Popen(
                ["npm", "run", "start"],
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

    async def close(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None

    async def act(
        self,
        action: str,
        url: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
    ):
        payload = {
            "action": action,
            "url": url,
            "variables": variables,
        }
        await self._stream_request("/api/act", payload)

    async def extract(
        self,
        instruction: str,
        schema: Dict[str, Any],
        url: Optional[str] = None,
    ):
        payload = {
            "instruction": instruction,
            "schema": schema,
            "url": url,
        }
        await self._stream_request("/api/extract", payload)

    async def observe(
        self,
        instruction: str,
        url: Optional[str] = None,
    ):
        payload = {
            "instruction": instruction,
            "url": url,
        }
        await self._stream_request("/api/observe", payload)

    async def _stream_request(self, endpoint: str, payload: Dict[str, Any]):
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", f"{self.server_url}{endpoint}", json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"Error: {error_text.decode('utf-8')}")
                    return
                async for line in response.aiter_lines():
                    if line:
                        log_data = self._parse_log_line(line)
                        if self.on_log:
                            await self.on_log(log_data)
                        else:
                            print(log_data)

    def _parse_log_line(self, line: str) -> Dict[str, Any]:
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return {"message": line}