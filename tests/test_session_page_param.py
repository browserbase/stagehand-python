# Manually maintained tests for Playwright page helpers (non-generated).

from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from stagehand import Stagehand, AsyncStagehand

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class _SyncCDP:
    def __init__(self, frame_id: str) -> None:
        self._frame_id = frame_id

    def send(self, method: str) -> dict[str, Any]:
        assert method == "Page.getFrameTree"
        return {"frameTree": {"frame": {"id": self._frame_id}}}


class _SyncContext:
    def __init__(self, frame_id: str) -> None:
        self._frame_id = frame_id

    def new_cdp_session(self, _page: Any) -> _SyncCDP:
        return _SyncCDP(self._frame_id)


class _SyncPage:
    def __init__(self, frame_id: str) -> None:
        self.context = _SyncContext(frame_id)


class _AsyncCDP:
    def __init__(self, frame_id: str) -> None:
        self._frame_id = frame_id

    async def send(self, method: str) -> dict[str, Any]:
        assert method == "Page.getFrameTree"
        return {"frameTree": {"frame": {"id": self._frame_id}}}


class _AsyncContext:
    def __init__(self, frame_id: str) -> None:
        self._frame_id = frame_id

    async def new_cdp_session(self, _page: Any) -> _AsyncCDP:
        return _AsyncCDP(self._frame_id)


class _AsyncPage:
    def __init__(self, frame_id: str) -> None:
        self.context = _AsyncContext(frame_id)


@pytest.mark.respx(base_url=base_url)
def test_session_act_injects_frame_id_from_page(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"
    frame_id = "frame-123"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    act_route = respx_mock.post(f"/v1/sessions/{session_id}/act").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"success": True, "message": "", "actionDescription": "", "actions": []}}},
        )
    )

    session = client.sessions.start(model_name="openai/gpt-5-nano")
    session.act(input="click something", page=_SyncPage(frame_id))

    assert act_route.called is True
    first_call = cast(Call, act_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert request_body["frameId"] == frame_id


@pytest.mark.respx(base_url=base_url)
def test_session_act_prefers_explicit_frame_id_over_page(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    act_route = respx_mock.post(f"/v1/sessions/{session_id}/act").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"success": True, "message": "", "actionDescription": "", "actions": []}}},
        )
    )

    session = client.sessions.start(model_name="openai/gpt-5-nano")

    class _ExplodingContext:
        def new_cdp_session(self, _page: Any) -> None:
            raise AssertionError("new_cdp_session should not be called when frame_id is provided")

    class _ExplodingPage:
        context = _ExplodingContext()

    session.act(input="click something", frame_id="explicit-frame", page=_ExplodingPage())

    assert act_route.called is True
    first_call = cast(Call, act_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert request_body["frameId"] == "explicit-frame"


@pytest.mark.respx(base_url=base_url)
async def test_async_session_act_injects_frame_id_from_page(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"
    frame_id = "frame-async-456"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    act_route = respx_mock.post(f"/v1/sessions/{session_id}/act").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"success": True, "message": "", "actionDescription": "", "actions": []}}},
        )
    )

    session = await async_client.sessions.start(model_name="openai/gpt-5-nano")
    await session.act(input="click something", page=_AsyncPage(frame_id))

    assert act_route.called is True
    first_call = cast(Call, act_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert request_body["frameId"] == frame_id
