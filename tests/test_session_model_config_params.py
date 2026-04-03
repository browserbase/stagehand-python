# Manually maintained tests for model config request serialization.

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

MODEL_STRING = "openai/gpt-5-nano"
MODEL_OBJECT_INPUT = {
    "model_name": "openai/gpt-5-nano",
    "api_key": "sk-some-openai-api-key",
    "base_url": "https://api.openai.com/v1",
    "headers": {"x-foo": "bar"},
    "provider": "openai",
}
MODEL_OBJECT_WIRE = {
    "modelName": "openai/gpt-5-nano",
    "apiKey": "sk-some-openai-api-key",
    "baseURL": "https://api.openai.com/v1",
    "headers": {"x-foo": "bar"},
    "provider": "openai",
}


def _mock_start_route(respx_mock: MockRouter, session_id: str) -> None:
    respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )


def _mock_observe_route(respx_mock: MockRouter, session_id: str):
    return respx_mock.post(f"/v1/sessions/{session_id}/observe").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {"result": [{"description": "Click submit", "selector": "button[type=submit]"}]},
            },
        )
    )


def _mock_extract_route(respx_mock: MockRouter, session_id: str):
    return respx_mock.post(f"/v1/sessions/{session_id}/extract").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"result": {"value": "ok"}}},
        )
    )


def _mock_execute_route(respx_mock: MockRouter, session_id: str):
    return respx_mock.post(f"/v1/sessions/{session_id}/agentExecute").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": True,
                "data": {"result": {"actions": [], "completed": True, "message": "done", "success": True}},
            },
        )
    )


def _request_json(call: Call) -> dict[str, object]:
    return cast(dict[str, object], json.loads(call.request.content))


@pytest.mark.respx(base_url=base_url)
def test_session_start_serializes_string_model_name(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000010"
    start_route = respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    session = client.sessions.start(model_name=MODEL_STRING)

    assert session.id == session_id
    request_body = _request_json(cast(Call, start_route.calls[0]))
    assert request_body["modelName"] == MODEL_STRING


@pytest.mark.respx(base_url=base_url)
def test_session_observe_serializes_string_and_object_model(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000011"
    _mock_start_route(respx_mock, session_id)
    observe_route = _mock_observe_route(respx_mock, session_id)

    session = client.sessions.start(model_name=MODEL_STRING)

    session.observe(instruction="find the submit button", options={"model": MODEL_STRING})
    session.observe(
        instruction="find the submit button",
        options=cast(Any, {"model": MODEL_OBJECT_INPUT}),
    )

    first_request = _request_json(cast(Call, observe_route.calls[0]))
    second_request = _request_json(cast(Call, observe_route.calls[1]))
    assert cast(dict[str, object], first_request["options"])["model"] == MODEL_STRING
    assert cast(dict[str, object], second_request["options"])["model"] == MODEL_OBJECT_WIRE


@pytest.mark.respx(base_url=base_url)
def test_session_extract_serializes_string_and_object_model(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000012"
    _mock_start_route(respx_mock, session_id)
    extract_route = _mock_extract_route(respx_mock, session_id)

    session = client.sessions.start(model_name=MODEL_STRING)

    session.extract(
        instruction="extract the result",
        schema={"type": "object", "properties": {"value": {"type": "string"}}},
        options={"model": MODEL_STRING},
    )
    session.extract(
        instruction="extract the result",
        schema={"type": "object", "properties": {"value": {"type": "string"}}},
        options=cast(Any, {"model": MODEL_OBJECT_INPUT}),
    )

    first_request = _request_json(cast(Call, extract_route.calls[0]))
    second_request = _request_json(cast(Call, extract_route.calls[1]))
    assert cast(dict[str, object], first_request["options"])["model"] == MODEL_STRING
    assert cast(dict[str, object], second_request["options"])["model"] == MODEL_OBJECT_WIRE


@pytest.mark.respx(base_url=base_url)
def test_session_execute_serializes_string_and_object_models(respx_mock: MockRouter, client: Stagehand) -> None:
    session_id = "00000000-0000-0000-0000-000000000013"
    _mock_start_route(respx_mock, session_id)
    execute_route = _mock_execute_route(respx_mock, session_id)

    session = client.sessions.start(model_name=MODEL_STRING)

    session.execute(
        agent_config=cast(
            Any,
            {
                "model": MODEL_STRING,
                "execution_model": MODEL_OBJECT_INPUT,
            },
        ),
        execute_options={"instruction": "click submit"},
    )
    session.execute(
        agent_config=cast(
            Any,
            {
                "model": MODEL_OBJECT_INPUT,
                "execution_model": MODEL_STRING,
            },
        ),
        execute_options={"instruction": "click submit"},
    )

    first_request = _request_json(cast(Call, execute_route.calls[0]))
    second_request = _request_json(cast(Call, execute_route.calls[1]))
    first_agent_config = cast(dict[str, object], first_request["agentConfig"])
    second_agent_config = cast(dict[str, object], second_request["agentConfig"])
    assert first_agent_config["model"] == MODEL_STRING
    assert first_agent_config["executionModel"] == MODEL_OBJECT_WIRE
    assert second_agent_config["model"] == MODEL_OBJECT_WIRE
    assert second_agent_config["executionModel"] == MODEL_STRING


@pytest.mark.respx(base_url=base_url)
async def test_async_session_start_serializes_string_model_name(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000014"
    start_route = respx_mock.post("/v1/sessions/start").mock(
        return_value=httpx.Response(
            200,
            json={"success": True, "data": {"available": True, "sessionId": session_id}},
        )
    )

    session = await async_client.sessions.start(model_name=MODEL_STRING)

    assert session.id == session_id
    request_body = _request_json(cast(Call, start_route.calls[0]))
    assert request_body["modelName"] == MODEL_STRING


@pytest.mark.respx(base_url=base_url)
async def test_async_session_observe_serializes_string_and_object_model(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000015"
    _mock_start_route(respx_mock, session_id)
    observe_route = _mock_observe_route(respx_mock, session_id)

    session = await async_client.sessions.start(model_name=MODEL_STRING)

    await session.observe(instruction="find the submit button", options={"model": MODEL_STRING})
    await session.observe(
        instruction="find the submit button",
        options=cast(Any, {"model": MODEL_OBJECT_INPUT}),
    )

    first_request = _request_json(cast(Call, observe_route.calls[0]))
    second_request = _request_json(cast(Call, observe_route.calls[1]))
    assert cast(dict[str, object], first_request["options"])["model"] == MODEL_STRING
    assert cast(dict[str, object], second_request["options"])["model"] == MODEL_OBJECT_WIRE


@pytest.mark.respx(base_url=base_url)
async def test_async_session_extract_serializes_string_and_object_model(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000016"
    _mock_start_route(respx_mock, session_id)
    extract_route = _mock_extract_route(respx_mock, session_id)

    session = await async_client.sessions.start(model_name=MODEL_STRING)

    await session.extract(
        instruction="extract the result",
        schema={"type": "object", "properties": {"value": {"type": "string"}}},
        options={"model": MODEL_STRING},
    )
    await session.extract(
        instruction="extract the result",
        schema={"type": "object", "properties": {"value": {"type": "string"}}},
        options=cast(Any, {"model": MODEL_OBJECT_INPUT}),
    )

    first_request = _request_json(cast(Call, extract_route.calls[0]))
    second_request = _request_json(cast(Call, extract_route.calls[1]))
    assert cast(dict[str, object], first_request["options"])["model"] == MODEL_STRING
    assert cast(dict[str, object], second_request["options"])["model"] == MODEL_OBJECT_WIRE


@pytest.mark.respx(base_url=base_url)
async def test_async_session_execute_serializes_string_and_object_models(
    respx_mock: MockRouter, async_client: AsyncStagehand
) -> None:
    session_id = "00000000-0000-0000-0000-000000000017"
    _mock_start_route(respx_mock, session_id)
    execute_route = _mock_execute_route(respx_mock, session_id)

    session = await async_client.sessions.start(model_name=MODEL_STRING)

    await session.execute(
        agent_config=cast(
            Any,
            {
                "model": MODEL_STRING,
                "execution_model": MODEL_OBJECT_INPUT,
            },
        ),
        execute_options={"instruction": "click submit"},
    )
    await session.execute(
        agent_config=cast(
            Any,
            {
                "model": MODEL_OBJECT_INPUT,
                "execution_model": MODEL_STRING,
            },
        ),
        execute_options={"instruction": "click submit"},
    )

    first_request = _request_json(cast(Call, execute_route.calls[0]))
    second_request = _request_json(cast(Call, execute_route.calls[1]))
    first_agent_config = cast(dict[str, object], first_request["agentConfig"])
    second_agent_config = cast(dict[str, object], second_request["agentConfig"])
    assert first_agent_config["model"] == MODEL_STRING
    assert first_agent_config["executionModel"] == MODEL_OBJECT_WIRE
    assert second_agent_config["model"] == MODEL_OBJECT_WIRE
    assert second_agent_config["executionModel"] == MODEL_STRING
