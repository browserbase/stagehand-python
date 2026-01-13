from __future__ import annotations

import httpx
import pytest
from respx import MockRouter

from stagehand import Stagehand, AsyncStagehand
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


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BROWSERBASE_API_KEY", "bb_key")
    monkeypatch.setenv("BROWSERBASE_PROJECT_ID", "bb_project")
    monkeypatch.setenv("MODEL_API_KEY", "model_key")


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

    client = Stagehand(server="local", local_binary_path="/does/not/matter/in/test")
    # Swap in a dummy server so we don't spawn a real binary in unit tests.
    client._sea_server = dummy  # type: ignore[attr-defined]

    resp = client.sessions.start(model_name="openai/gpt-5-nano")
    assert resp.success is True
    assert dummy.started == 1

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

    async with AsyncStagehand(server="local", local_binary_path="/does/not/matter/in/test") as client:
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
    client = Stagehand(server="local")
    with pytest.raises(StagehandError):
        client.sessions.start(model_name="openai/gpt-5-nano")


def test_local_server_allows_local_browser_without_browserbase_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.delenv("BROWSERBASE_API_KEY", raising=False)
    monkeypatch.delenv("BROWSERBASE_PROJECT_ID", raising=False)
    client = Stagehand(server="local")
    client._post = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("post called"))

    with pytest.raises(RuntimeError, match="post called"):
        client.sessions.start(
            model_name="openai/gpt-5-nano",
            browser={"type": "local"},
        )
