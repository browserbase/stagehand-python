# Manually maintained tests for Pydantic extract helpers.

from __future__ import annotations

import os
import json
from typing import cast

import httpx
import pytest
from pydantic import BaseModel
from respx import MockRouter
from respx.models import Call

from stagehand import AsyncStagehand, Stagehand

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class ExtractedUser(BaseModel):
    user_name: str
    lucky_number: int


class ExtractedName(BaseModel):
    user_name: str


@pytest.mark.respx(base_url=base_url)
def test_session_extract_accepts_pydantic_schema(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    extract_route = respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"userName": "Ada", "luckyNumber": 7}}},
        )
    )

    session = client.sessions.start(model_name="openai/gpt-5-nano")
    response = session.extract(instruction="extract the user", schema=ExtractedUser)

    assert isinstance(response.data.result, ExtractedUser)
    assert response.data.result.user_name == "Ada"
    assert response.data.result.lucky_number == 7

    first_call = cast(Call, extract_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert request_body["schema"]["properties"]["user_name"]["type"] == "string"
    assert request_body["schema"]["properties"]["lucky_number"]["type"] == "integer"


@pytest.mark.parametrize("client", [False], indirect=True)
@pytest.mark.respx(base_url=base_url)
def test_session_extract_allows_extra_fields_when_client_is_non_strict(
    respx_mock: MockRouter, client: Stagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000001"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"userName": "Ada", "favoriteColor": "blue"}}},
        )
    )

    session = client.sessions.start(model_name="openai/gpt-5-nano")
    response = session.extract(instruction="extract the user", schema=ExtractedName)

    assert isinstance(response.data.result, ExtractedName)
    assert response.data.result.user_name == "Ada"
    assert response.data.result.model_extra == {"favorite_color": "blue"}


@pytest.mark.respx(base_url=base_url)
def test_session_extract_rejects_extra_fields_when_client_is_strict(
    respx_mock: MockRouter, client: Stagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000002"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"userName": "Ada", "favoriteColor": "blue"}}},
        )
    )

    session = client.sessions.start(model_name="openai/gpt-5-nano")
    response = session.extract(instruction="extract the user", schema=ExtractedName)

    assert response.data.result == {"userName": "Ada", "favoriteColor": "blue"}


@pytest.mark.respx(base_url=base_url)
async def test_async_session_extract_accepts_pydantic_schema(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000000"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    extract_route = respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"userName": "Grace", "luckyNumber": 11}}},
        )
    )

    session = await async_client.sessions.start(model_name="openai/gpt-5-nano")
    response = await session.extract(instruction="extract the user", schema=ExtractedUser)

    assert isinstance(response.data.result, ExtractedUser)
    assert response.data.result.user_name == "Grace"
    assert response.data.result.lucky_number == 11

    first_call = cast(Call, extract_route.calls[0])
    request_body = json.loads(first_call.request.content)
    assert request_body["schema"]["properties"]["user_name"]["type"] == "string"
    assert request_body["schema"]["properties"]["lucky_number"]["type"] == "integer"


@pytest.mark.parametrize("async_client", [False], indirect=True)
@pytest.mark.respx(base_url=base_url)
async def test_async_session_extract_allows_extra_fields_when_client_is_non_strict(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000003"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"userName": "Grace", "favoriteColor": "green"}}},
        )
    )

    session = await async_client.sessions.start(model_name="openai/gpt-5-nano")
    response = await session.extract(instruction="extract the user", schema=ExtractedName)

    assert isinstance(response.data.result, ExtractedName)
    assert response.data.result.user_name == "Grace"
    assert response.data.result.model_extra == {"favorite_color": "green"}


@pytest.mark.respx(base_url=base_url)
async def test_async_session_extract_rejects_extra_fields_when_client_is_strict(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000004"

    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"userName": "Grace", "favoriteColor": "green"}}},
        )
    )

    session = await async_client.sessions.start(model_name="openai/gpt-5-nano")
    response = await session.extract(instruction="extract the user", schema=ExtractedName)

    assert response.data.result == {"userName": "Grace", "favoriteColor": "green"}
