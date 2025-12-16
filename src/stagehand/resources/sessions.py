# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Dict, Optional, cast
from typing_extensions import Literal

import httpx

from ..types import (
    session_act_params,
    session_start_params,
    session_extract_params,
    session_observe_params,
    session_navigate_params,
    session_execute_agent_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import is_given, maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.session_act_response import SessionActResponse
from ..types.session_end_response import SessionEndResponse
from ..types.session_start_response import SessionStartResponse
from ..types.session_extract_response import SessionExtractResponse
from ..types.session_observe_response import SessionObserveResponse
from ..types.session_navigate_response import SessionNavigateResponse
from ..types.session_execute_agent_response import SessionExecuteAgentResponse

__all__ = ["SessionsResource", "AsyncSessionsResource"]


class SessionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/browserbase/stagehand-python#accessing-raw-response-data-eg-headers
        """
        return SessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/browserbase/stagehand-python#with_streaming_response
        """
        return SessionsResourceWithStreamingResponse(self)

    def act(
        self,
        session_id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse:
        """
        Performs a browser action based on natural language instruction or a specific
        action object returned by observe().

        Args:
          input: Natural language instruction

          frame_id: Frame ID to act on (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{session_id}/act",
            body=maybe_transform(
                {
                    "input": input,
                    "frame_id": frame_id,
                    "options": options,
                },
                session_act_params.SessionActParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionActResponse,
        )

    def end(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        """
        Closes the browser and cleans up all resources associated with the session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return self._post(
            f"/sessions/{session_id}/end",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionEndResponse,
        )

    def execute_agent(
        self,
        session_id: str,
        *,
        agent_config: session_execute_agent_params.AgentConfig,
        execute_options: session_execute_agent_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteAgentResponse:
        """
        Runs an autonomous agent that can perform multiple actions to complete a complex
        task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{session_id}/agentExecute",
            body=maybe_transform(
                {
                    "agent_config": agent_config,
                    "execute_options": execute_options,
                    "frame_id": frame_id,
                },
                session_execute_agent_params.SessionExecuteAgentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExecuteAgentResponse,
        )

    def extract(
        self,
        session_id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse:
        """
        Extracts data from the current page using natural language instructions and
        optional JSON schema for structured output.

        Args:
          frame_id: Frame ID to extract from

          instruction: Natural language instruction for extraction

          schema: JSON Schema for structured output

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return cast(
            SessionExtractResponse,
            self._post(
                f"/sessions/{session_id}/extract",
                body=maybe_transform(
                    {
                        "frame_id": frame_id,
                        "instruction": instruction,
                        "options": options,
                        "schema": schema,
                    },
                    session_extract_params.SessionExtractParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, SessionExtractResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def navigate(
        self,
        session_id: str,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Optional[SessionNavigateResponse]:
        """
        Navigates the browser to the specified URL and waits for page load.

        Args:
          url: URL to navigate to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{session_id}/navigate",
            body=maybe_transform(
                {
                    "url": url,
                    "frame_id": frame_id,
                    "options": options,
                },
                session_navigate_params.SessionNavigateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionNavigateResponse,
        )

    def observe(
        self,
        session_id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse:
        """
        Returns a list of candidate actions that can be performed on the page,
        optionally filtered by natural language instruction.

        Args:
          frame_id: Frame ID to observe

          instruction: Natural language instruction to filter actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{session_id}/observe",
            body=maybe_transform(
                {
                    "frame_id": frame_id,
                    "instruction": instruction,
                    "options": options,
                },
                session_observe_params.SessionObserveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionObserveResponse,
        )

    def start(
        self,
        *,
        browserbase_api_key: str,
        browserbase_project_id: str,
        dom_settle_timeout: int | Omit = omit,
        model: str | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionStartResponse:
        """Initializes a new Stagehand session with a browser instance.

        Returns a session
        ID that must be used for all subsequent requests.

        Args:
          browserbase_api_key: API key for Browserbase Cloud

          browserbase_project_id: Project ID for Browserbase

          dom_settle_timeout: Timeout in ms to wait for DOM to settle

          model: AI model to use for actions (must be prefixed with provider/)

          self_heal: Enable self-healing for failed actions

          system_prompt: Custom system prompt for AI actions

          verbose: Logging verbosity level

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/sessions/start",
            body=maybe_transform(
                {
                    "browserbase_api_key": browserbase_api_key,
                    "browserbase_project_id": browserbase_project_id,
                    "dom_settle_timeout": dom_settle_timeout,
                    "model": model,
                    "self_heal": self_heal,
                    "system_prompt": system_prompt,
                    "verbose": verbose,
                },
                session_start_params.SessionStartParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionStartResponse,
        )


class AsyncSessionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/browserbase/stagehand-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/browserbase/stagehand-python#with_streaming_response
        """
        return AsyncSessionsResourceWithStreamingResponse(self)

    async def act(
        self,
        session_id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse:
        """
        Performs a browser action based on natural language instruction or a specific
        action object returned by observe().

        Args:
          input: Natural language instruction

          frame_id: Frame ID to act on (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{session_id}/act",
            body=await async_maybe_transform(
                {
                    "input": input,
                    "frame_id": frame_id,
                    "options": options,
                },
                session_act_params.SessionActParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionActResponse,
        )

    async def end(
        self,
        session_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        """
        Closes the browser and cleans up all resources associated with the session.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        return await self._post(
            f"/sessions/{session_id}/end",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionEndResponse,
        )

    async def execute_agent(
        self,
        session_id: str,
        *,
        agent_config: session_execute_agent_params.AgentConfig,
        execute_options: session_execute_agent_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteAgentResponse:
        """
        Runs an autonomous agent that can perform multiple actions to complete a complex
        task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{session_id}/agentExecute",
            body=await async_maybe_transform(
                {
                    "agent_config": agent_config,
                    "execute_options": execute_options,
                    "frame_id": frame_id,
                },
                session_execute_agent_params.SessionExecuteAgentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExecuteAgentResponse,
        )

    async def extract(
        self,
        session_id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse:
        """
        Extracts data from the current page using natural language instructions and
        optional JSON schema for structured output.

        Args:
          frame_id: Frame ID to extract from

          instruction: Natural language instruction for extraction

          schema: JSON Schema for structured output

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return cast(
            SessionExtractResponse,
            await self._post(
                f"/sessions/{session_id}/extract",
                body=await async_maybe_transform(
                    {
                        "frame_id": frame_id,
                        "instruction": instruction,
                        "options": options,
                        "schema": schema,
                    },
                    session_extract_params.SessionExtractParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, SessionExtractResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def navigate(
        self,
        session_id: str,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Optional[SessionNavigateResponse]:
        """
        Navigates the browser to the specified URL and waits for page load.

        Args:
          url: URL to navigate to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{session_id}/navigate",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "frame_id": frame_id,
                    "options": options,
                },
                session_navigate_params.SessionNavigateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionNavigateResponse,
        )

    async def observe(
        self,
        session_id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse:
        """
        Returns a list of candidate actions that can be performed on the page,
        optionally filtered by natural language instruction.

        Args:
          frame_id: Frame ID to observe

          instruction: Natural language instruction to filter actions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not session_id:
            raise ValueError(f"Expected a non-empty value for `session_id` but received {session_id!r}")
        extra_headers = {
            **strip_not_given(
                {"x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given}
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{session_id}/observe",
            body=await async_maybe_transform(
                {
                    "frame_id": frame_id,
                    "instruction": instruction,
                    "options": options,
                },
                session_observe_params.SessionObserveParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionObserveResponse,
        )

    async def start(
        self,
        *,
        browserbase_api_key: str,
        browserbase_project_id: str,
        dom_settle_timeout: int | Omit = omit,
        model: str | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionStartResponse:
        """Initializes a new Stagehand session with a browser instance.

        Returns a session
        ID that must be used for all subsequent requests.

        Args:
          browserbase_api_key: API key for Browserbase Cloud

          browserbase_project_id: Project ID for Browserbase

          dom_settle_timeout: Timeout in ms to wait for DOM to settle

          model: AI model to use for actions (must be prefixed with provider/)

          self_heal: Enable self-healing for failed actions

          system_prompt: Custom system prompt for AI actions

          verbose: Logging verbosity level

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/sessions/start",
            body=await async_maybe_transform(
                {
                    "browserbase_api_key": browserbase_api_key,
                    "browserbase_project_id": browserbase_project_id,
                    "dom_settle_timeout": dom_settle_timeout,
                    "model": model,
                    "self_heal": self_heal,
                    "system_prompt": system_prompt,
                    "verbose": verbose,
                },
                session_start_params.SessionStartParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionStartResponse,
        )


class SessionsResourceWithRawResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.act = to_raw_response_wrapper(
            sessions.act,
        )
        self.end = to_raw_response_wrapper(
            sessions.end,
        )
        self.execute_agent = to_raw_response_wrapper(
            sessions.execute_agent,
        )
        self.extract = to_raw_response_wrapper(
            sessions.extract,
        )
        self.navigate = to_raw_response_wrapper(
            sessions.navigate,
        )
        self.observe = to_raw_response_wrapper(
            sessions.observe,
        )
        self.start = to_raw_response_wrapper(
            sessions.start,
        )


class AsyncSessionsResourceWithRawResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.act = async_to_raw_response_wrapper(
            sessions.act,
        )
        self.end = async_to_raw_response_wrapper(
            sessions.end,
        )
        self.execute_agent = async_to_raw_response_wrapper(
            sessions.execute_agent,
        )
        self.extract = async_to_raw_response_wrapper(
            sessions.extract,
        )
        self.navigate = async_to_raw_response_wrapper(
            sessions.navigate,
        )
        self.observe = async_to_raw_response_wrapper(
            sessions.observe,
        )
        self.start = async_to_raw_response_wrapper(
            sessions.start,
        )


class SessionsResourceWithStreamingResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.act = to_streamed_response_wrapper(
            sessions.act,
        )
        self.end = to_streamed_response_wrapper(
            sessions.end,
        )
        self.execute_agent = to_streamed_response_wrapper(
            sessions.execute_agent,
        )
        self.extract = to_streamed_response_wrapper(
            sessions.extract,
        )
        self.navigate = to_streamed_response_wrapper(
            sessions.navigate,
        )
        self.observe = to_streamed_response_wrapper(
            sessions.observe,
        )
        self.start = to_streamed_response_wrapper(
            sessions.start,
        )


class AsyncSessionsResourceWithStreamingResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.act = async_to_streamed_response_wrapper(
            sessions.act,
        )
        self.end = async_to_streamed_response_wrapper(
            sessions.end,
        )
        self.execute_agent = async_to_streamed_response_wrapper(
            sessions.execute_agent,
        )
        self.extract = async_to_streamed_response_wrapper(
            sessions.extract,
        )
        self.navigate = async_to_streamed_response_wrapper(
            sessions.navigate,
        )
        self.observe = async_to_streamed_response_wrapper(
            sessions.observe,
        )
        self.start = async_to_streamed_response_wrapper(
            sessions.start,
        )
