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

    session = client.sessions.start(model_name="openai/gpt-5-nano")
    assert session.id == session_id

    session.navigate(url="https://example.com")
    assert navigate_route.called is True
    first_call = cast(Call, navigate_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert "frameId" not in request_body


@pytest.mark.respx(base_url=base_url)
def test_sessions_create_preserves_default_model_config(respx_mock: MockRouter) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"
    client = Stagehand(
        base_url=base_url,
        browserbase_api_key="My Browserbase API Key",
        browserbase_project_id="My Browserbase Project ID",
        model_api_key=None,
    )

    start_route = respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {"available": True, "sessionId": session_id},
            },
        )
    )

    extract_route = respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"title": "Example"}}},
        )
    )

    session = client.sessions.start(
        model_name="bedrock/anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_client_options={
            "api_key": "bedrock-bearer-token",
            "region": "us-east-1",
        },
    )

    start_call = cast(Call, start_route.calls[0])
    start_request_body = json.loads(start_call.request.content)
    assert start_request_body == {
        "modelName": "bedrock/anthropic.claude-3-7-sonnet-20250219-v1:0",
        "modelClientOptions": {
            "apiKey": "bedrock-bearer-token",
            "region": "us-east-1",
        },
    }
    assert start_call.request.headers.get("x-model-api-key") is None

    session.extract(
        instruction="extract the page title",
        schema={"type": "object", "properties": {"title": {"type": "string"}}},
    )

    extract_call = cast(Call, extract_route.calls[0])
    extract_request_body = json.loads(extract_call.request.content)
    assert extract_request_body["options"]["model"] == {
        "modelName": "bedrock/anthropic.claude-3-7-sonnet-20250219-v1:0",
        "apiKey": "bedrock-bearer-token",
        "region": "us-east-1",
    }

    client.close()


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

    session = await async_client.sessions.start(model_name="openai/gpt-5-nano")
    assert session.id == session_id

    await session.navigate(url="https://example.com")
    assert navigate_route.called is True
    first_call = cast(Call, navigate_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert "frameId" not in request_body


@pytest.mark.respx(base_url=base_url)
async def test_async_sessions_create_preserves_default_model_config(
    respx_mock: MockRouter,
) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"
    client = AsyncStagehand(
        base_url=base_url,
        browserbase_api_key="My Browserbase API Key",
        browserbase_project_id="My Browserbase Project ID",
        model_api_key=None,
    )

    start_route = respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {"available": True, "sessionId": session_id},
            },
        )
    )

    extract_route = respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"title": "Example"}}},
        )
    )

    session = await client.sessions.start(
        model_name="bedrock/anthropic.claude-3-7-sonnet-20250219-v1:0",
        model_client_options={
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "secret",
            "session_token": "session-token",
            "region": "us-east-1",
        },
    )

    start_call = cast(Call, start_route.calls[0])
    start_request_body = json.loads(start_call.request.content)
    assert start_request_body == {
        "modelName": "bedrock/anthropic.claude-3-7-sonnet-20250219-v1:0",
        "modelClientOptions": {
            "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
            "secretAccessKey": "secret",
            "sessionToken": "session-token",
            "region": "us-east-1",
        },
    }
    assert start_call.request.headers.get("x-model-api-key") is None

    await session.extract(
        instruction="extract the page title",
        schema={"type": "object", "properties": {"title": {"type": "string"}}},
    )

    extract_call = cast(Call, extract_route.calls[0])
    extract_request_body = json.loads(extract_call.request.content)
    assert extract_request_body["options"]["model"] == {
        "modelName": "bedrock/anthropic.claude-3-7-sonnet-20250219-v1:0",
        "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "secretAccessKey": "secret",
        "sessionToken": "session-token",
        "region": "us-east-1",
    }

    await client.close()
