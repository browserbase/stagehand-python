# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Optional, cast

import pytest

from stagehand import Stagehand, AsyncStagehand
from tests.utils import assert_matches_type
from stagehand.types import (
    SessionActResponse,
    SessionEndResponse,
    SessionStartResponse,
    SessionExtractResponse,
    SessionObserveResponse,
    SessionNavigateResponse,
    SessionExecuteAgentResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act(self, client: Stagehand) -> None:
        session = client.sessions.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
            frame_id="frameId",
            options={
                "model": {
                    "api_key": "apiKey",
                    "base_url": "https://example.com",
                    "model": "model",
                    "provider": "openai",
                },
                "timeout": 0,
                "variables": {"foo": "string"},
            },
            x_stream_response="true",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_act(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_act(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionActResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_act(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.sessions.with_raw_response.act(
                session_id="",
                input="click the sign in button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_end(self, client: Stagehand) -> None:
        session = client.sessions.end(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_end(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.end(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_end(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.end(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionEndResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_end(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.sessions.with_raw_response.end(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_agent(self, client: Stagehand) -> None:
        session = client.sessions.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={},
            execute_options={"instruction": "Find and click the first product"},
        )
        assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_agent_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={
                "cua": True,
                "model": "openai/gpt-4o",
                "provider": "openai",
                "system_prompt": "systemPrompt",
            },
            execute_options={
                "instruction": "Find and click the first product",
                "highlight_cursor": True,
                "max_steps": 10,
            },
            frame_id="frameId",
            x_stream_response="true",
        )
        assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_agent(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={},
            execute_options={"instruction": "Find and click the first product"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_agent(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={},
            execute_options={"instruction": "Find and click the first product"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute_agent(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.sessions.with_raw_response.execute_agent(
                session_id="",
                agent_config={},
                execute_options={"instruction": "Find and click the first product"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract(self, client: Stagehand) -> None:
        session = client.sessions.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            frame_id="frameId",
            instruction="extract the page title",
            options={
                "model": {
                    "api_key": "apiKey",
                    "base_url": "https://example.com",
                    "model": "model",
                    "provider": "openai",
                },
                "selector": "selector",
                "timeout": 0,
            },
            schema={"foo": "bar"},
            x_stream_response="true",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_extract(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_extract(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionExtractResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_extract(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.sessions.with_raw_response.extract(
                session_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate(self, client: Stagehand) -> None:
        session = client.sessions.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
        )
        assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
            frame_id="frameId",
            options={"wait_until": "load"},
            x_stream_response="true",
        )
        assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_navigate(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_navigate(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_navigate(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.sessions.with_raw_response.navigate(
                session_id="",
                url="https://example.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe(self, client: Stagehand) -> None:
        session = client.sessions.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            frame_id="frameId",
            instruction="instruction",
            options={
                "model": {
                    "api_key": "apiKey",
                    "base_url": "https://example.com",
                    "model": "model",
                    "provider": "openai",
                },
                "selector": "selector",
                "timeout": 0,
            },
            x_stream_response="true",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_observe(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_observe(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionObserveResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_observe(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.sessions.with_raw_response.observe(
                session_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start(self, client: Stagehand) -> None:
        session = client.sessions.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
            dom_settle_timeout=0,
            model="openai/gpt-4o",
            self_heal=True,
            system_prompt="systemPrompt",
            verbose=1,
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionStartResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_act(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_act_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
            frame_id="frameId",
            options={
                "model": {
                    "api_key": "apiKey",
                    "base_url": "https://example.com",
                    "model": "model",
                    "provider": "openai",
                },
                "timeout": 0,
                "variables": {"foo": "string"},
            },
            x_stream_response="true",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_act(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_act(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.act(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            input="click the sign in button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionActResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_act(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.sessions.with_raw_response.act(
                session_id="",
                input="click the sign in button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_end(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.end(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_end(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.end(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_end(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.end(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionEndResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_end(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.sessions.with_raw_response.end(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_agent(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={},
            execute_options={"instruction": "Find and click the first product"},
        )
        assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_agent_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={
                "cua": True,
                "model": "openai/gpt-4o",
                "provider": "openai",
                "system_prompt": "systemPrompt",
            },
            execute_options={
                "instruction": "Find and click the first product",
                "highlight_cursor": True,
                "max_steps": 10,
            },
            frame_id="frameId",
            x_stream_response="true",
        )
        assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_agent(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={},
            execute_options={"instruction": "Find and click the first product"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_agent(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.execute_agent(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            agent_config={},
            execute_options={"instruction": "Find and click the first product"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionExecuteAgentResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute_agent(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.sessions.with_raw_response.execute_agent(
                session_id="",
                agent_config={},
                execute_options={"instruction": "Find and click the first product"},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            frame_id="frameId",
            instruction="extract the page title",
            options={
                "model": {
                    "api_key": "apiKey",
                    "base_url": "https://example.com",
                    "model": "model",
                    "provider": "openai",
                },
                "selector": "selector",
                "timeout": 0,
            },
            schema={"foo": "bar"},
            x_stream_response="true",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_extract(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_extract(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.extract(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionExtractResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_extract(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.sessions.with_raw_response.extract(
                session_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
        )
        assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
            frame_id="frameId",
            options={"wait_until": "load"},
            x_stream_response="true",
        )
        assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_navigate(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_navigate(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.navigate(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            url="https://example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Optional[SessionNavigateResponse], session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_navigate(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.sessions.with_raw_response.navigate(
                session_id="",
                url="https://example.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            frame_id="frameId",
            instruction="instruction",
            options={
                "model": {
                    "api_key": "apiKey",
                    "base_url": "https://example.com",
                    "model": "model",
                    "provider": "openai",
                },
                "selector": "selector",
                "timeout": 0,
            },
            x_stream_response="true",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_observe(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_observe(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.observe(
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionObserveResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_observe(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.sessions.with_raw_response.observe(
                session_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
            dom_settle_timeout=0,
            model="openai/gpt-4o",
            self_heal=True,
            system_prompt="systemPrompt",
            verbose=1,
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.start(
            browserbase_api_key="BROWSERBASE_API_KEY",
            browserbase_project_id="BROWSERBASE_PROJECT_ID",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionStartResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True
