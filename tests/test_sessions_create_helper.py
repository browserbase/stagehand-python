# Manually maintained tests for non-generated helpers.

from __future__ import annotations

import os
import json
from typing import cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call

from stagehand import Stagehand, AsyncStagehand

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


@pytest.mark.respx(base_url=base_url)
def test_sessions_create_returns_bound_session(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {"available": True, "sessionId": session_id},
            },
        )
    )

    navigate_route = respx_mock.post(f"/v1/sessions/{session_id}/navigate").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": None}},
        )
    )

    session = client.sessions.create(model_name="openai/gpt-5-nano")
    assert session.id == session_id

    session.navigate(url="https://example.com")
    assert navigate_route.called is True
    first_call = cast(Call, navigate_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert request_body["frameId"] == ""


@pytest.mark.respx(base_url=base_url)
async def test_async_sessions_create_returns_bound_session(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {"available": True, "sessionId": session_id},
            },
        )
    )

    navigate_route = respx_mock.post(f"/v1/sessions/{session_id}/navigate").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": None}},
        )
    )

    session = await async_client.sessions.create(model_name="openai/gpt-5-nano")
    assert session.id == session_id

    await session.navigate(url="https://example.com")
    assert navigate_route.called is True
    first_call = cast(Call, navigate_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert request_body["frameId"] == ""
