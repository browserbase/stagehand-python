from __future__ import annotations

import os
import sys
import time
import atexit
import signal
import socket
import asyncio
import subprocess
from pathlib import Path
from threading import Lock
from dataclasses import dataclass

import httpx

from .._version import __version__
from .sea_binary import resolve_binary_path


@dataclass(frozen=True)
class SeaServerConfig:
    host: str
    port: int
    headless: bool
    ready_timeout_s: float
    openai_api_key: str | None
    shutdown_on_close: bool


def _pick_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _build_base_url(*, host: str, port: int) -> str:
    return f"http://{host}:{port}"


def _terminate_process(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return

    try:
        if sys.platform != "win32":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=3)
        return
    except Exception:
        pass

    try:
        if sys.platform != "win32":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
    finally:
        try:
            proc.wait(timeout=3)
        except Exception:
            pass


def _wait_ready_sync(*, base_url: str, timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s
    with httpx.Client(timeout=1.0) as client:
        while time.monotonic() < deadline:
            try:
                # stagehand-binary: /health
                # stagehand/packages/server: /readyz and /healthz
                for path in ("/readyz", "/healthz", "/health"):
                    resp = client.get(f"{base_url}{path}")
                    if resp.status_code == 200:
                        return
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
    raise TimeoutError(f"Stagehand SEA server not ready at {base_url} after {timeout_s}s")


async def _wait_ready_async(*, base_url: str, timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s
    async with httpx.AsyncClient(timeout=1.0) as client:
        while time.monotonic() < deadline:
            try:
                for path in ("/readyz", "/healthz", "/health"):
                    resp = await client.get(f"{base_url}{path}")
                    if resp.status_code == 200:
                        return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.1)
    raise TimeoutError(f"Stagehand SEA server not ready at {base_url} after {timeout_s}s")


class SeaServerManager:
    def __init__(
        self,
        *,
        config: SeaServerConfig,
        local_binary_path: str | os.PathLike[str] | None = None,
    ) -> None:
        self._config = config
        self._binary_path: Path = resolve_binary_path(local_binary_path=local_binary_path, version=__version__)

        self._lock = Lock()
        self._async_lock = asyncio.Lock()

        self._proc: subprocess.Popen[bytes] | None = None
        self._base_url: str | None = None
        self._atexit_registered: bool = False

    @property
    def base_url(self) -> str | None:
        return self._base_url

    def ensure_running_sync(self) -> str:
        with self._lock:
            if self._proc is not None and self._proc.poll() is None and self._base_url is not None:
                return self._base_url

            base_url, proc = self._start_sync()
            self._base_url = base_url
            self._proc = proc
            return base_url

    async def ensure_running_async(self) -> str:
        async with self._async_lock:
            if self._proc is not None and self._proc.poll() is None and self._base_url is not None:
                return self._base_url

            base_url, proc = await self._start_async()
            self._base_url = base_url
            self._proc = proc
            return base_url

    def close(self) -> None:
        if not self._config.shutdown_on_close:
            return

        with self._lock:
            if self._proc is None:
                return
            _terminate_process(self._proc)
            self._proc = None
            self._base_url = None

    async def aclose(self) -> None:
        if not self._config.shutdown_on_close:
            return

        async with self._async_lock:
            if self._proc is None:
                return
            _terminate_process(self._proc)
            self._proc = None
            self._base_url = None

    def _start_sync(self) -> tuple[str, subprocess.Popen[bytes]]:
        if not self._binary_path.exists():
            raise FileNotFoundError(
                f"Stagehand SEA binary not found at {self._binary_path}. "
                "Pass local_binary_path=... or set STAGEHAND_SEA_BINARY."
            )

        port = _pick_free_port(self._config.host) if self._config.port == 0 else self._config.port
        base_url = _build_base_url(host=self._config.host, port=port)

        proc_env = dict(os.environ)
        # Defaults that make the server boot under SEA (avoid pino-pretty transport)
        proc_env.setdefault("NODE_ENV", "production")
        # Server package expects BB_ENV to be set (see packages/server/src/lib/env.ts)
        proc_env.setdefault("BB_ENV", "local")
        proc_env["HOST"] = self._config.host
        proc_env["PORT"] = str(port)
        proc_env["HEADLESS"] = "true" if self._config.headless else "false"
        if self._config.openai_api_key:
            proc_env["OPENAI_API_KEY"] = self._config.openai_api_key

        preexec_fn = None
        creationflags = 0
        if sys.platform != "win32":
            preexec_fn = os.setsid
        else:
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        proc = subprocess.Popen(
            [str(self._binary_path)],
            env=proc_env,
            stdout=None,
            stderr=None,
            preexec_fn=preexec_fn,
            creationflags=creationflags,
        )

        if not self._atexit_registered:
            atexit.register(_terminate_process, proc)
            self._atexit_registered = True

        try:
            _wait_ready_sync(base_url=base_url, timeout_s=self._config.ready_timeout_s)
        except Exception:
            _terminate_process(proc)
            raise

        return base_url, proc

    async def _start_async(self) -> tuple[str, subprocess.Popen[bytes]]:
        if not self._binary_path.exists():
            raise FileNotFoundError(
                f"Stagehand SEA binary not found at {self._binary_path}. "
                "Pass local_binary_path=... or set STAGEHAND_SEA_BINARY."
            )

        port = _pick_free_port(self._config.host) if self._config.port == 0 else self._config.port
        base_url = _build_base_url(host=self._config.host, port=port)

        proc_env = dict(os.environ)
        proc_env.setdefault("NODE_ENV", "production")
        proc_env.setdefault("BB_ENV", "local")
        proc_env["HOST"] = self._config.host
        proc_env["PORT"] = str(port)
        proc_env["HEADLESS"] = "true" if self._config.headless else "false"
        if self._config.openai_api_key:
            proc_env["OPENAI_API_KEY"] = self._config.openai_api_key

        preexec_fn = None
        creationflags = 0
        if sys.platform != "win32":
            preexec_fn = os.setsid
        else:
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        proc = subprocess.Popen(
            [str(self._binary_path)],
            env=proc_env,
            stdout=None,
            stderr=None,
            preexec_fn=preexec_fn,
            creationflags=creationflags,
        )

        if not self._atexit_registered:
            atexit.register(_terminate_process, proc)
            self._atexit_registered = True

        try:
            await _wait_ready_async(base_url=base_url, timeout_s=self._config.ready_timeout_s)
        except Exception:
            _terminate_process(proc)
            raise

        return base_url, proc
