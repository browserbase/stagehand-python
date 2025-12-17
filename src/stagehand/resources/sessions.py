# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import (
    session_act_params,
    session_start_params,
    session_execute_params,
    session_extract_params,
    session_observe_params,
    session_navigate_params,
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
from ..types.session_execute_response import SessionExecuteResponse
from ..types.session_extract_response import SessionExtractResponse
from ..types.session_observe_response import SessionObserveResponse
from ..types.session_navigate_response import SessionNavigateResponse

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
        id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          id: Unique session identifier

          input: Natural language instruction or Action object

          frame_id: Target frame ID for the action

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/sessions/{id}/act",
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
        id: str,
        *,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        """
        Terminates the browser session and releases all associated resources.

        Args:
          id: Unique session identifier

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/sessions/{id}/end",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionEndResponse,
        )

    def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          id: Unique session identifier

          frame_id: Target frame ID for the agent

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/sessions/{id}/agentExecute",
            body=maybe_transform(
                {
                    "agent_config": agent_config,
                    "execute_options": execute_options,
                    "frame_id": frame_id,
                },
                session_execute_params.SessionExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExecuteResponse,
        )

    def extract(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          id: Unique session identifier

          frame_id: Target frame ID for the extraction

          instruction: Natural language instruction for what to extract

          schema: JSON Schema defining the structure of data to extract

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/sessions/{id}/extract",
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
            cast_to=SessionExtractResponse,
        )

    def navigate(
        self,
        id: str,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionNavigateResponse:
        """
        Navigates the browser to the specified URL.

        Args:
          id: Unique session identifier

          url: URL to navigate to

          frame_id: Target frame ID for the navigation

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/sessions/{id}/navigate",
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
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          id: Unique session identifier

          frame_id: Target frame ID for the observation

          instruction: Natural language instruction for what actions to find

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/sessions/{id}/observe",
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
        model_name: str,
        act_timeout_ms: float | Omit = omit,
        browser: session_start_params.Browser | Omit = omit,
        browserbase_session_create_params: session_start_params.BrowserbaseSessionCreateParams | Omit = omit,
        browserbase_session_id: str | Omit = omit,
        debug_dom: bool | Omit = omit,
        dom_settle_timeout_ms: float | Omit = omit,
        experimental: bool | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: Literal[0, 1, 2] | Omit = omit,
        wait_for_captcha_solves: bool | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionStartResponse:
        """Creates a new browser session with the specified configuration.

        Returns a
        session ID used for all subsequent operations.

        Args:
          model_name: Model name to use for AI operations

          act_timeout_ms: Timeout in ms for act operations

          browserbase_session_id: Existing Browserbase session ID to resume

          dom_settle_timeout_ms: Timeout in ms to wait for DOM to settle

          self_heal: Enable self-healing for failed actions

          system_prompt: Custom system prompt for AI operations

          verbose: Logging verbosity level (0=quiet, 1=normal, 2=debug)

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            "/v1/sessions/start",
            body=maybe_transform(
                {
                    "model_name": model_name,
                    "act_timeout_ms": act_timeout_ms,
                    "browser": browser,
                    "browserbase_session_create_params": browserbase_session_create_params,
                    "browserbase_session_id": browserbase_session_id,
                    "debug_dom": debug_dom,
                    "dom_settle_timeout_ms": dom_settle_timeout_ms,
                    "experimental": experimental,
                    "self_heal": self_heal,
                    "system_prompt": system_prompt,
                    "verbose": verbose,
                    "wait_for_captcha_solves": wait_for_captcha_solves,
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
        id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          id: Unique session identifier

          input: Natural language instruction or Action object

          frame_id: Target frame ID for the action

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/sessions/{id}/act",
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
        id: str,
        *,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        """
        Terminates the browser session and releases all associated resources.

        Args:
          id: Unique session identifier

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/sessions/{id}/end",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionEndResponse,
        )

    async def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          id: Unique session identifier

          frame_id: Target frame ID for the agent

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/sessions/{id}/agentExecute",
            body=await async_maybe_transform(
                {
                    "agent_config": agent_config,
                    "execute_options": execute_options,
                    "frame_id": frame_id,
                },
                session_execute_params.SessionExecuteParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExecuteResponse,
        )

    async def extract(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          id: Unique session identifier

          frame_id: Target frame ID for the extraction

          instruction: Natural language instruction for what to extract

          schema: JSON Schema defining the structure of data to extract

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/sessions/{id}/extract",
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
            cast_to=SessionExtractResponse,
        )

    async def navigate(
        self,
        id: str,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionNavigateResponse:
        """
        Navigates the browser to the specified URL.

        Args:
          id: Unique session identifier

          url: URL to navigate to

          frame_id: Target frame ID for the navigation

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/sessions/{id}/navigate",
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
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          id: Unique session identifier

          frame_id: Target frame ID for the observation

          instruction: Natural language instruction for what actions to find

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/sessions/{id}/observe",
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
        model_name: str,
        act_timeout_ms: float | Omit = omit,
        browser: session_start_params.Browser | Omit = omit,
        browserbase_session_create_params: session_start_params.BrowserbaseSessionCreateParams | Omit = omit,
        browserbase_session_id: str | Omit = omit,
        debug_dom: bool | Omit = omit,
        dom_settle_timeout_ms: float | Omit = omit,
        experimental: bool | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: Literal[0, 1, 2] | Omit = omit,
        wait_for_captcha_solves: bool | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionStartResponse:
        """Creates a new browser session with the specified configuration.

        Returns a
        session ID used for all subsequent operations.

        Args:
          model_name: Model name to use for AI operations

          act_timeout_ms: Timeout in ms for act operations

          browserbase_session_id: Existing Browserbase session ID to resume

          dom_settle_timeout_ms: Timeout in ms to wait for DOM to settle

          self_heal: Enable self-healing for failed actions

          system_prompt: Custom system prompt for AI operations

          verbose: Logging verbosity level (0=quiet, 1=normal, 2=debug)

          x_language: Client SDK language

          x_sdk_version: Version of the Stagehand SDK

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": x_sdk_version,
                    "x-sent-at": x_sent_at.isoformat() if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            "/v1/sessions/start",
            body=await async_maybe_transform(
                {
                    "model_name": model_name,
                    "act_timeout_ms": act_timeout_ms,
                    "browser": browser,
                    "browserbase_session_create_params": browserbase_session_create_params,
                    "browserbase_session_id": browserbase_session_id,
                    "debug_dom": debug_dom,
                    "dom_settle_timeout_ms": dom_settle_timeout_ms,
                    "experimental": experimental,
                    "self_heal": self_heal,
                    "system_prompt": system_prompt,
                    "verbose": verbose,
                    "wait_for_captcha_solves": wait_for_captcha_solves,
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
        self.execute = to_raw_response_wrapper(
            sessions.execute,
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
        self.execute = async_to_raw_response_wrapper(
            sessions.execute,
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
        self.execute = to_streamed_response_wrapper(
            sessions.execute,
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
        self.execute = async_to_streamed_response_wrapper(
            sessions.execute,
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
