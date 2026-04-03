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
from typing_extensions import Literal, Protocol, TypedDict

import httpx

from .._version import __version__
from .sea_binary import resolve_binary_path


@dataclass(frozen=True)
class SeaServerConfig:
    host: str
    port: int
    headless: bool
    ready_timeout_s: float
    model_api_key: str | None
    chrome_path: str | None
    shutdown_on_close: bool


class _HasLocalModeState(Protocol):
    _server_mode: Literal["remote", "local"]
    _local_stagehand_binary_path: str | os.PathLike[str] | None
    _local_host: str
    _local_port: int
    _local_headless: bool
    _local_chrome_path: str | None
    _local_ready_timeout_s: float
    _local_shutdown_on_close: bool
    _sea_server: SeaServerManager | None


class LocalModeKwargs(TypedDict):
    server: Literal["remote", "local"]
    _local_stagehand_binary_path: str | os.PathLike[str] | None
    local_host: str
    local_port: int
    local_headless: bool
    local_chrome_path: str | None
    local_ready_timeout_s: float
    local_shutdown_on_close: bool


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


def _terminate_process_async_atexit(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is not None:
        return

    try:
        if sys.platform != "win32":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
    except Exception:
        pass


async def _terminate_process_async(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is not None:
        return

    try:
        if sys.platform != "win32":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        await asyncio.wait_for(proc.wait(), timeout=3)
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
            await asyncio.wait_for(proc.wait(), timeout=3)
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
        _local_stagehand_binary_path: str | os.PathLike[str] | None = None,
    ) -> None:
        self._config = config
        self._binary_path: Path = resolve_binary_path(
            _local_stagehand_binary_path=_local_stagehand_binary_path,
            version=__version__,
        )

        self._lock = Lock()
        self._async_lock = asyncio.Lock()

        self._proc: subprocess.Popen[bytes] | None = None
        self._async_proc: asyncio.subprocess.Process | None = None
        self._base_url: str | None = None
        self._atexit_registered: bool = False

    @property
    def base_url(self) -> str | None:
        return self._base_url

    def _build_process_env(self, *, port: int) -> dict[str, str]:
        proc_env = dict(os.environ)
        # Force production mode so inherited NODE_ENV=development never reaches the
        # SEA child process. Development mode breaks under SEA because pino-pretty
        # is an optional dependency that is not present in the packaged binary.
        proc_env["NODE_ENV"] = "production"
        # Server package expects BB_ENV to be set (see packages/server/src/lib/env.ts)
        proc_env.setdefault("BB_ENV", "local")
        proc_env["HOST"] = self._config.host
        proc_env["PORT"] = str(port)
        proc_env["HEADLESS"] = "true" if self._config.headless else "false"
        # Always set MODEL_API_KEY in the child env so the SDK constructor value wins
        # over any inherited parent MODEL_API_KEY. An empty string preserves the
        # "explicitly unset" case instead of silently reusing the parent's value.
        proc_env["MODEL_API_KEY"] = self._config.model_api_key or ""
        if self._config.chrome_path:
            proc_env["CHROME_PATH"] = self._config.chrome_path
            proc_env["LIGHTHOUSE_CHROMIUM_PATH"] = self._config.chrome_path
        return proc_env

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
            if self._async_proc is not None and self._async_proc.returncode is None and self._base_url is not None:
                return self._base_url

            base_url, proc = await self._start_async()
            self._base_url = base_url
            self._async_proc = proc
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
            if self._async_proc is None:
                return
            await _terminate_process_async(self._async_proc)
            self._async_proc = None
            self._base_url = None

    def _start_sync(self) -> tuple[str, subprocess.Popen[bytes]]:
        if not self._binary_path.exists():
            raise FileNotFoundError(
                f"Stagehand SEA binary not found at {self._binary_path}. "
                "Pass _local_stagehand_binary_path=... or set STAGEHAND_SEA_BINARY."
            )

        port = _pick_free_port(self._config.host) if self._config.port == 0 else self._config.port
        base_url = _build_base_url(host=self._config.host, port=port)
        proc_env = self._build_process_env(port=port)

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

    async def _start_async(self) -> tuple[str, asyncio.subprocess.Process]:
        if not self._binary_path.exists():
            raise FileNotFoundError(
                f"Stagehand SEA binary not found at {self._binary_path}. "
                "Pass _local_stagehand_binary_path=... or set STAGEHAND_SEA_BINARY."
            )

        port = _pick_free_port(self._config.host) if self._config.port == 0 else self._config.port
        base_url = _build_base_url(host=self._config.host, port=port)
        proc_env = self._build_process_env(port=port)

        proc = await asyncio.create_subprocess_exec(
            str(self._binary_path),
            env=proc_env,
            stdout=None,
            stderr=None,
            start_new_session=True,
        )

        if not self._atexit_registered:
            atexit.register(_terminate_process_async_atexit, proc)
            self._atexit_registered = True

        try:
            await _wait_ready_async(base_url=base_url, timeout_s=self._config.ready_timeout_s)
        except Exception:
            await _terminate_process_async(proc)
            raise

        return base_url, proc


def configure_client_base_url(
    client: _HasLocalModeState,
    *,
    server: Literal["remote", "local"],
    _local_stagehand_binary_path: str | os.PathLike[str] | None,
    local_host: str,
    local_port: int,
    local_headless: bool,
    local_chrome_path: str | None,
    local_ready_timeout_s: float,
    local_shutdown_on_close: bool,
    base_url: str | httpx.URL | None,
    model_api_key: str | None,
) -> str | httpx.URL:
    client._server_mode = server
    client._local_stagehand_binary_path = _local_stagehand_binary_path
    client._local_host = local_host
    client._local_port = local_port
    client._local_headless = local_headless
    client._local_chrome_path = local_chrome_path
    client._local_ready_timeout_s = local_ready_timeout_s
    client._local_shutdown_on_close = local_shutdown_on_close
    client._sea_server = None

    if server == "local":
        if base_url is None:
            base_url = "http://127.0.0.1"

        client._sea_server = SeaServerManager(
            config=SeaServerConfig(
                host=local_host,
                port=local_port,
                headless=local_headless,
                ready_timeout_s=local_ready_timeout_s,
                model_api_key=model_api_key,
                chrome_path=local_chrome_path,
                shutdown_on_close=local_shutdown_on_close,
            ),
            _local_stagehand_binary_path=_local_stagehand_binary_path,
        )
        return base_url

    if base_url is None:
        base_url = os.environ.get("STAGEHAND_BASE_URL")
    if base_url is None:
        base_url = "https://api.stagehand.browserbase.com"
    return base_url


def copy_local_mode_kwargs(
    client: _HasLocalModeState,
    *,
    server: Literal["remote", "local"] | None,
    _local_stagehand_binary_path: str | os.PathLike[str] | None,
    local_host: str | None,
    local_port: int | None,
    local_headless: bool | None,
    local_chrome_path: str | None,
    local_ready_timeout_s: float | None,
    local_shutdown_on_close: bool | None,
) -> LocalModeKwargs:
    return {
        "server": server or client._server_mode,
        "_local_stagehand_binary_path": (
            _local_stagehand_binary_path
            if _local_stagehand_binary_path is not None
            else client._local_stagehand_binary_path
        ),
        "local_host": local_host or client._local_host,
        "local_port": local_port if local_port is not None else client._local_port,
        "local_headless": local_headless if local_headless is not None else client._local_headless,
        "local_chrome_path": (
            local_chrome_path if local_chrome_path is not None else client._local_chrome_path
        ),
        "local_ready_timeout_s": (
            local_ready_timeout_s
            if local_ready_timeout_s is not None
            else client._local_ready_timeout_s
        ),
        "local_shutdown_on_close": (
            local_shutdown_on_close
            if local_shutdown_on_close is not None
            else client._local_shutdown_on_close
        ),
    }


def prepare_sync_client_base_url(client: _HasLocalModeState) -> str | None:
    if client._sea_server is None:
        return None
    return client._sea_server.ensure_running_sync()


async def prepare_async_client_base_url(client: _HasLocalModeState) -> str | None:
    if client._sea_server is None:
        return None
    return await client._sea_server.ensure_running_async()


def close_sync_client_sea_server(client: _HasLocalModeState) -> None:
    if client._sea_server is not None:
        client._sea_server.close()


async def close_async_client_sea_server(client: _HasLocalModeState) -> None:
    if client._sea_server is not None:
        await client._sea_server.aclose()
