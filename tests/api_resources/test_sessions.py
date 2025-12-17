# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from stagehand import Stagehand, AsyncStagehand
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act(self, client: Stagehand) -> None:
        session = client.sessions.act(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_act_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.act(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_act(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.act(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_act(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.act(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_end(self, client: Stagehand) -> None:
        session = client.sessions.end(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_end_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.end(
            id={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_end(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.end(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_end(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.end(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_agent(self, client: Stagehand) -> None:
        session = client.sessions.execute_agent(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_agent_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.execute_agent(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_agent(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.execute_agent(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_agent(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.execute_agent(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract(self, client: Stagehand) -> None:
        session = client.sessions.extract(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.extract(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_extract(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.extract(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_extract(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.extract(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate(self, client: Stagehand) -> None:
        session = client.sessions.navigate(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_navigate_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.navigate(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_navigate(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.navigate(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_navigate(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.navigate(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe(self, client: Stagehand) -> None:
        session = client.sessions.observe(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_observe_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.observe(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_observe(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.observe(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_observe(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.observe(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start(self, client: Stagehand) -> None:
        session = client.sessions.start()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_with_all_params(self, client: Stagehand) -> None:
        session = client.sessions.start(
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start(self, client: Stagehand) -> None:
        response = client.sessions.with_raw_response.start()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start(self, client: Stagehand) -> None:
        with client.sessions.with_streaming_response.start() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_act(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.act(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_act_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.act(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_act(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.act(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_act(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.act(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_end(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.end(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_end_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.end(
            id={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_end(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.end(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_end(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.end(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_agent(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.execute_agent(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_agent_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.execute_agent(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_agent(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.execute_agent(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_agent(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.execute_agent(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.extract(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.extract(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_extract(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.extract(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_extract(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.extract(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.navigate(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_navigate_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.navigate(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_navigate(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.navigate(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_navigate(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.navigate(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.observe(
            id={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_observe_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.observe(
            id={},
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_observe(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.observe(
            id={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_observe(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.observe(
            id={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.start()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_with_all_params(self, async_client: AsyncStagehand) -> None:
        session = await async_client.sessions.start(
            body={},
            x_language={},
            x_sdk_version={},
            x_sent_at={},
            x_stream_response={},
        )
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncStagehand) -> None:
        response = await async_client.sessions.with_raw_response.start()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(object, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncStagehand) -> None:
        async with async_client.sessions.with_streaming_response.start() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(object, session, path=["response"])

        assert cast(Any, response.is_closed) is True
