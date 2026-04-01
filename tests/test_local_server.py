from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
from respx import MockRouter

from stagehand import Stagehand, AsyncStagehand
from stagehand.lib import sea_server
from stagehand._exceptions import StagehandError


class _DummySeaServer:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self.started = 0
        self.closed = 0

    def ensure_running_sync(self) -> str:
        self.started += 1
        return self._base_url

    async def ensure_running_async(self) -> str:
        self.started += 1
        return self._base_url

    def close(self) -> None:
        self.closed += 1

    async def aclose(self) -> None:
        self.closed += 1


class _DummyProcess:
    pid = 12345

    def __init__(self) -> None:
        self._returncode: int | None = None

    def poll(self) -> int | None:
        return self._returncode

    def wait(self, _timeout: float | None = None) -> int:
        self._returncode = 0
        return 0

    def terminate(self) -> None:
        self._returncode = 0

    def kill(self) -> None:
        self._returncode = 0


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROWSERBASE_API_KEY", "bb_key")
    monkeypatch.setenv("BROWSERBASE_PROJECT_ID", "bb_project")


def _set_browserbase_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROWSERBASE_API_KEY", "bb_key")
    monkeypatch.setenv("BROWSERBASE_PROJECT_ID", "bb_project")


def _install_fake_sea_runtime(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    captured_env: dict[str, str],
    *,
    port: int,
) -> None:
    binary_path = tmp_path / "stagehand-test-binary"
    binary_path.write_text("binary")

    def _fake_popen(
        args: list[str],
        env: dict[str, str],
        stdout: object,
        stderr: object,
        preexec_fn: object,
        creationflags: int,
    ) -> _DummyProcess:
        del args, stdout, stderr, preexec_fn, creationflags
        captured_env.update(env)
        return _DummyProcess()

    monkeypatch.setattr(sea_server, "_pick_free_port", lambda _host: port)
    monkeypatch.setattr(sea_server, "_terminate_process", lambda proc: setattr(proc, "_returncode", 0))
    monkeypatch.setattr(sea_server, "_wait_ready_sync", lambda **_kwargs: None)
    monkeypatch.setattr(sea_server, "resolve_binary_path", lambda **_kwargs: binary_path)
    monkeypatch.setattr(sea_server.subprocess, "Popen", _fake_popen)


@pytest.mark.respx(base_url="http://127.0.0.1:43123")
def test_sync_local_mode_starts_before_first_request(respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)

    dummy = _DummySeaServer("http://127.0.0.1:43123")

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {
                    "available": True,
                    "connectUrl": "ws://example",
                    "sessionId": "00000000-0000-0000-0000-000000000000",
                },
            },
        )
    )

    client = Stagehand(
        server="local",
        model_api_key="model_key",
        _local_stagehand_binary_path="/does/not/matter/in/test",
    )
    # Swap in a dummy server so we don't spawn a real binary in unit tests.
    client._sea_server = dummy  # type: ignore[attr-defined]

    resp = client.sessions.start(model_name="openai/gpt-5-nano")
    assert resp.success is True
    assert dummy.started == 1

    client.close()
    assert dummy.closed == 1


@pytest.mark.respx(base_url="http://127.0.0.1:43127")
def test_sync_local_mode_defaults_browser_type_local_when_omitted(
    respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    _set_required_env(monkeypatch)

    dummy = _DummySeaServer("http://127.0.0.1:43127")
    request_body: dict[str, object] = {}

    def _capture_start_request(request: httpx.Request) -> httpx.Response:
        request_body["json"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={
                "success": True,
                "data": {
                    "available": True,
                    "connectUrl": "ws://example",
                    "sessionId": "00000000-0000-0000-0000-000000000001",
                },
            },
        )

    respx_mock.post("/v1/sessions/start").mock(side_effect=_capture_start_request)

    client = Stagehand(
        server="local",
        model_api_key="model_key",
        _local_stagehand_binary_path="/does/not/matter/in/test",
    )
    client._sea_server = dummy  # type: ignore[attr-defined]

    resp = client.sessions.start(model_name="openai/gpt-5-nano")
    assert resp.success is True
    assert request_body["json"] == {
        "modelName": "openai/gpt-5-nano",
        "browser": {"type": "local"},
    }

    client.close()
    assert dummy.closed == 1


@pytest.mark.respx(base_url="http://127.0.0.1:43124")
@pytest.mark.asyncio
async def test_async_local_mode_starts_before_first_request(
    respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    _set_required_env(monkeypatch)

    dummy = _DummySeaServer("http://127.0.0.1:43124")

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {
                    "available": True,
                    "connectUrl": "ws://example",
                    "sessionId": "00000000-0000-0000-0000-000000000000",
                },
            },
        )
    )

    async with AsyncStagehand(
        server="local",
        model_api_key="model_key",
        _local_stagehand_binary_path="/does/not/matter/in/test",
    ) as client:
        client._sea_server = dummy  # type: ignore[attr-defined]
        resp = await client.sessions.start(model_name="openai/gpt-5-nano")
        assert resp.success is True
        assert dummy.started == 1

    assert dummy.closed == 1


def test_local_server_requires_browserbase_keys_for_browserbase_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.delenv("BROWSERBASE_API_KEY", raising=False)
    monkeypatch.delenv("BROWSERBASE_PROJECT_ID", raising=False)
    client = Stagehand(
        server="local",
        model_api_key="model_key",
        _local_stagehand_binary_path="/does/not/matter/in/test",
    )
    client._sea_server = _DummySeaServer("http://127.0.0.1:43125")  # type: ignore[attr-defined]
    with pytest.raises(StagehandError):
        client.sessions.start(model_name="openai/gpt-5-nano")


def test_local_server_allows_local_browser_without_browserbase_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.delenv("BROWSERBASE_API_KEY", raising=False)
    monkeypatch.delenv("BROWSERBASE_PROJECT_ID", raising=False)
    client = Stagehand(
        server="local",
        model_api_key="model_key",
        _local_stagehand_binary_path="/does/not/matter/in/test",
    )
    client._sea_server = _DummySeaServer("http://127.0.0.1:43126")  # type: ignore[attr-defined]

    def _post(*_args: object, **_kwargs: object) -> object:
        raise RuntimeError("post called")

    client.sessions._post = _post  # type: ignore[method-assign]
    client.base_url = httpx.URL("http://127.0.0.1:43126")

    with pytest.raises(RuntimeError, match="post called"):
        client.sessions.start(
            model_name="openai/gpt-5-nano",
            browser={"type": "local"},
        )


@pytest.mark.parametrize(
    ("explicit_model_api_key", "expected_model_api_key"),
    [
        (None, ""),
        ("good1", "good1"),
    ],
)
def test_local_mode_masks_inherited_model_api_key_envs_and_prefers_explicit_param(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    explicit_model_api_key: str | None,
    expected_model_api_key: str,
) -> None:
    _set_browserbase_env(monkeypatch)
    # Simulate a parent process with conflicting inherited env. The child SEA process
    # should keep unrelated env intact while MODEL_API_KEY follows constructor intent.
    monkeypatch.setenv("MODEL_API_KEY", "bad1")
    monkeypatch.setenv("OPENAI_API_KEY", "bad2")

    captured_env: dict[str, str] = {}
    _install_fake_sea_runtime(monkeypatch, tmp_path, captured_env, port=43129)

    client_kwargs: dict[str, object] = {
        "server": "local",
        "_local_stagehand_binary_path": "/does/not/matter/in/test",
    }
    if explicit_model_api_key is not None:
        client_kwargs["model_api_key"] = explicit_model_api_key

    client = Stagehand(**client_kwargs)
    assert client._sea_server is not None

    client._sea_server.ensure_running_sync()

    assert captured_env["MODEL_API_KEY"] == expected_model_api_key
    assert captured_env["OPENAI_API_KEY"] == "bad2"
    client.close()


def test_local_mode_forwards_flow_log_and_config_dir_env_to_sea_binary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("BROWSERBASE_FLOW_LOGS", "1")
    monkeypatch.setenv("BROWSERBASE_CONFIG_DIR", "./tmp")

    captured_env: dict[str, str] = {}
    _install_fake_sea_runtime(monkeypatch, tmp_path, captured_env, port=43131)

    client = Stagehand(
        server="local",
        model_api_key="model_key",
        _local_stagehand_binary_path="/does/not/matter/in/test",
    )
    assert client._sea_server is not None

    client._sea_server.ensure_running_sync()

    assert captured_env["BROWSERBASE_FLOW_LOGS"] == "1"
    assert captured_env["BROWSERBASE_CONFIG_DIR"] == "./tmp"
    client.close()
