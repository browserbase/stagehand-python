# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from stagehand import Stagehand, AsyncStagehand
from tests.utils import assert_matches_type
from stagehand.types import (
    SessionActResponse,
    SessionEndResponse,
    SessionStartResponse,
    SessionExecuteResponse,
    SessionExtractResponse,
    SessionObserveResponse,
    SessionNavigateResponse,
)
from stagehand._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act_with_all_params_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            frame_id="frameId",
            options={
                "model": "openai/gpt-5-nano",
                "timeout": 30000,
                "variables": {"username": "john_doe"},
            },
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_act_overload_1(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_act_overload_1(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionActResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_act_overload_1(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.act(
                id="",
                input="Click the login button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act_with_all_params_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
            frame_id="frameId",
            options={
                "model": "openai/gpt-5-nano",
                "timeout": 30000,
                "variables": {"username": "john_doe"},
            },
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_act_overload_2(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_act_overload_2(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_act_overload_2(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.act(
                id="",
                input="Click the login button",
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_end(self, client: Stagehand) -> None:
        session = client.sessions.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_end_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            _force_body={},
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_end(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_end(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionEndResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_end(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.end(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
        )
        assert_matches_type(SessionExecuteResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_with_all_params_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={
                "cua": True,
                "model": "openai/gpt-5-nano",
                "provider": "openai",
                "system_prompt": "systemPrompt",
            },
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings",
                "highlight_cursor": True,
                "max_steps": 20,
            },
            frame_id="frameId",
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionExecuteResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_overload_1(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionExecuteResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_overload_1(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionExecuteResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute_overload_1(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.execute(
                id="",
                agent_config={},
                execute_options={
                    "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
            stream_response=True,
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_with_all_params_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={
                "cua": True,
                "model": "openai/gpt-5-nano",
                "provider": "openai",
                "system_prompt": "systemPrompt",
            },
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings",
                "highlight_cursor": True,
                "max_steps": 20,
            },
            stream_response=True,
            frame_id="frameId",
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_overload_2(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_overload_2(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute_overload_2(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.execute(
                id="",
                agent_config={},
                execute_options={
                    "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
                },
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_with_all_params_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            frame_id="frameId",
            instruction="Extract all product names and prices from the page",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "#main-content",
                "timeout": 30000,
            },
            schema={"foo": "bar"},
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_extract_overload_1(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_extract_overload_1(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionExtractResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_extract_overload_1(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.extract(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_with_all_params_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
            frame_id="frameId",
            instruction="Extract all product names and prices from the page",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "#main-content",
                "timeout": 30000,
            },
            schema={"foo": "bar"},
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_extract_overload_2(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_extract_overload_2(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_extract_overload_2(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.extract(
                id="",
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate(self, client: Stagehand) -> None:
        session = client.sessions.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
        )
        assert_matches_type(SessionNavigateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
            frame_id="frameId",
            options={
                "referer": "referer",
                "timeout": 30000,
                "wait_until": "networkidle",
            },
            stream_response=True,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionNavigateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_navigate(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionNavigateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_navigate(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionNavigateResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_navigate(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.navigate(
                id="",
                url="https://example.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe_with_all_params_overload_1(self, client: Stagehand) -> None:
        session = client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            frame_id="frameId",
            instruction="Find all clickable navigation links",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "nav",
                "timeout": 30000,
            },
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_observe_overload_1(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_observe_overload_1(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionObserveResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_observe_overload_1(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.observe(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe_with_all_params_overload_2(self, client: Stagehand) -> None:
        session_stream = client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
            frame_id="frameId",
            instruction="Find all clickable navigation links",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "nav",
                "timeout": 30000,
            },
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        session_stream.response.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_observe_overload_2(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_observe_overload_2(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_observe_overload_2(self, client: Stagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.with_raw_response.observe(
                id="",
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start(self, client: Stagehand) -> None:
        session = client.sessions.start(
            model_name="openai/gpt-4o",
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.start(
            model_name="openai/gpt-4o",
            act_timeout_ms=0,
            browser={
                "cdp_url": "ws://localhost:9222",
                "launch_options": {
                    "accept_downloads": True,
                    "args": ["string"],
                    "cdp_url": "cdpUrl",
                    "chromium_sandbox": True,
                    "connect_timeout_ms": 0,
                    "device_scale_factor": 0,
                    "devtools": True,
                    "downloads_path": "downloadsPath",
                    "executable_path": "executablePath",
                    "has_touch": True,
                    "headless": True,
                    "ignore_default_args": True,
                    "ignore_https_errors": True,
                    "locale": "locale",
                    "preserve_user_data_dir": True,
                    "proxy": {
                        "server": "server",
                        "bypass": "bypass",
                        "password": "password",
                        "username": "username",
                    },
                    "user_data_dir": "userDataDir",
                    "viewport": {
                        "height": 0,
                        "width": 0,
                    },
                },
                "type": "local",
            },
            browserbase_session_create_params={
                "browser_settings": {
                    "advanced_stealth": True,
                    "block_ads": True,
                    "context": {
                        "id": "id",
                        "persist": True,
                    },
                    "extension_id": "extensionId",
                    "fingerprint": {
                        "browsers": ["chrome"],
                        "devices": ["desktop"],
                        "http_version": "1",
                        "locales": ["string"],
                        "operating_systems": ["android"],
                        "screen": {
                            "max_height": 0,
                            "max_width": 0,
                            "min_height": 0,
                            "min_width": 0,
                        },
                    },
                    "log_session": True,
                    "record_session": True,
                    "solve_captchas": True,
                    "viewport": {
                        "height": 0,
                        "width": 0,
                    },
                },
                "extension_id": "extensionId",
                "keep_alive": True,
                "project_id": "projectId",
                "proxies": True,
                "region": "us-west-2",
                "timeout": 0,
                "user_metadata": {"foo": "bar"},
            },
            browserbase_session_id="browserbaseSessionID",
            dom_settle_timeout_ms=5000,
            experimental=True,
            self_heal=True,
            system_prompt="systemPrompt",
            verbose=1,
            wait_for_captcha_solves=True,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.start(
            model_name="openai/gpt-4o",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.start(
            model_name="openai/gpt-4o",
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
    async def test_method_act_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_act_with_all_params_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            frame_id="frameId",
            options={
                "model": "openai/gpt-5-nano",
                "timeout": 30000,
                "variables": {"username": "john_doe"},
            },
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_act_overload_1(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionActResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_act_overload_1(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionActResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_act_overload_1(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.act(
                id="",
                input="Click the login button",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_act_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_act_with_all_params_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
            frame_id="frameId",
            options={
                "model": "openai/gpt-5-nano",
                "timeout": 30000,
                "variables": {"username": "john_doe"},
            },
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_act_overload_2(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_act_overload_2(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.act(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            input="Click the login button",
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_act_overload_2(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.act(
                id="",
                input="Click the login button",
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_end(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_end_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            _force_body={},
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_end(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionEndResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_end(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.end(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionEndResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_end(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.end(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
        )
        assert_matches_type(SessionExecuteResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_with_all_params_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={
                "cua": True,
                "model": "openai/gpt-5-nano",
                "provider": "openai",
                "system_prompt": "systemPrompt",
            },
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings",
                "highlight_cursor": True,
                "max_steps": 20,
            },
            frame_id="frameId",
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionExecuteResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_overload_1(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionExecuteResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_overload_1(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionExecuteResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute_overload_1(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.execute(
                id="",
                agent_config={},
                execute_options={
                    "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
            stream_response=True,
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_with_all_params_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={
                "cua": True,
                "model": "openai/gpt-5-nano",
                "provider": "openai",
                "system_prompt": "systemPrompt",
            },
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings",
                "highlight_cursor": True,
                "max_steps": 20,
            },
            stream_response=True,
            frame_id="frameId",
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_overload_2(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_overload_2(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.execute(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            agent_config={},
            execute_options={
                "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
            },
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute_overload_2(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.execute(
                id="",
                agent_config={},
                execute_options={
                    "instruction": "Log in with username 'demo' and password 'test123', then navigate to settings"
                },
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_with_all_params_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            frame_id="frameId",
            instruction="Extract all product names and prices from the page",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "#main-content",
                "timeout": 30000,
            },
            schema={"foo": "bar"},
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_extract_overload_1(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionExtractResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_extract_overload_1(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionExtractResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_extract_overload_1(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.extract(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_with_all_params_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
            frame_id="frameId",
            instruction="Extract all product names and prices from the page",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "#main-content",
                "timeout": 30000,
            },
            schema={"foo": "bar"},
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_extract_overload_2(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_extract_overload_2(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.extract(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_extract_overload_2(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.extract(
                id="",
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
        )
        assert_matches_type(SessionNavigateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
            frame_id="frameId",
            options={
                "referer": "referer",
                "timeout": 30000,
                "wait_until": "networkidle",
            },
            stream_response=True,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionNavigateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_navigate(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionNavigateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_navigate(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.navigate(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            url="https://example.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionNavigateResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_navigate(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.navigate(
                id="",
                url="https://example.com",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe_with_all_params_overload_1(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            frame_id="frameId",
            instruction="Find all clickable navigation links",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "nav",
                "timeout": 30000,
            },
            stream_response=False,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_observe_overload_1(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionObserveResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_observe_overload_1(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionObserveResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_observe_overload_1(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.observe(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe_with_all_params_overload_2(self, async_client: AsyncStagehand) -> None:
        session_stream = await async_client.sessions.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
            frame_id="frameId",
            instruction="Find all clickable navigation links",
            options={
                "model": "openai/gpt-5-nano",
                "selector": "nav",
                "timeout": 30000,
            },
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        await session_stream.response.aclose()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_observe_overload_2(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = await response.parse()
        await stream.close()

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_observe_overload_2(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.observe(
            id="c4dbf3a9-9a58-4b22-8a1c-9f20f9f9e123",
            stream_response=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_observe_overload_2(self, async_client: AsyncStagehand) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.with_raw_response.observe(
                id="",
                stream_response=True,
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.start(
            model_name="openai/gpt-4o",
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.start(
            model_name="openai/gpt-4o",
            act_timeout_ms=0,
            browser={
                "cdp_url": "ws://localhost:9222",
                "launch_options": {
                    "accept_downloads": True,
                    "args": ["string"],
                    "cdp_url": "cdpUrl",
                    "chromium_sandbox": True,
                    "connect_timeout_ms": 0,
                    "device_scale_factor": 0,
                    "devtools": True,
                    "downloads_path": "downloadsPath",
                    "executable_path": "executablePath",
                    "has_touch": True,
                    "headless": True,
                    "ignore_default_args": True,
                    "ignore_https_errors": True,
                    "locale": "locale",
                    "preserve_user_data_dir": True,
                    "proxy": {
                        "server": "server",
                        "bypass": "bypass",
                        "password": "password",
                        "username": "username",
                    },
                    "user_data_dir": "userDataDir",
                    "viewport": {
                        "height": 0,
                        "width": 0,
                    },
                },
                "type": "local",
            },
            browserbase_session_create_params={
                "browser_settings": {
                    "advanced_stealth": True,
                    "block_ads": True,
                    "context": {
                        "id": "id",
                        "persist": True,
                    },
                    "extension_id": "extensionId",
                    "fingerprint": {
                        "browsers": ["chrome"],
                        "devices": ["desktop"],
                        "http_version": "1",
                        "locales": ["string"],
                        "operating_systems": ["android"],
                        "screen": {
                            "max_height": 0,
                            "max_width": 0,
                            "min_height": 0,
                            "min_width": 0,
                        },
                    },
                    "log_session": True,
                    "record_session": True,
                    "solve_captchas": True,
                    "viewport": {
                        "height": 0,
                        "width": 0,
                    },
                },
                "extension_id": "extensionId",
                "keep_alive": True,
                "project_id": "projectId",
                "proxies": True,
                "region": "us-west-2",
                "timeout": 0,
                "user_metadata": {"foo": "bar"},
            },
            browserbase_session_id="browserbaseSessionID",
            dom_settle_timeout_ms=5000,
            experimental=True,
            self_heal=True,
            system_prompt="systemPrompt",
            verbose=1,
            wait_for_captcha_solves=True,
            x_sent_at=parse_datetime("2025-01-15T10:30:00Z"),
            x_stream_response="true",
        )
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.start(
            model_name="openai/gpt-4o",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionStartResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.start(
            model_name="openai/gpt-4o",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionStartResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True
