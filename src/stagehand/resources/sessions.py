# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, TYPE_CHECKING, Union
from datetime import datetime, timezone
from typing_extensions import Literal, overload

import httpx

from ..types import (
    session_act_params,
    session_start_params,
    session_execute_params,
    session_extract_params,
    session_observe_params,
    session_navigate_params,
)

if TYPE_CHECKING:
    from .._client import Stagehand, AsyncStagehand
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import is_given, required_args, maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._streaming import Stream, AsyncStream
from .._base_client import make_request_options
from ..types.stream_event import StreamEvent
from ..types.session_act_response import SessionActResponse
from ..types.session_end_response import SessionEndResponse
from ..types.session_start_response import SessionStartResponse
from ..types.session_execute_response import SessionExecuteResponse
from ..types.session_extract_response import SessionExtractResponse
from ..types.session_observe_response import SessionObserveResponse
from ..types.session_navigate_response import SessionNavigateResponse
from .._exceptions import StagehandError

__all__ = ["SessionsResource", "AsyncSessionsResource"]


def _format_x_sent_at(value: Union[str, datetime] | Omit) -> str | NotGiven:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        value = value.astimezone(timezone.utc)
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, Omit):
        return not_given
    return value


def _requires_browserbase_credentials(
    _: "Stagehand | AsyncStagehand",
    browser: session_start_params.Browser | Omit,
) -> bool:
    if not is_given(browser):
        return True

    browser_type = None
    if isinstance(browser, dict):
        browser_type = browser.get("type")

    return browser_type != "local"


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

    @overload
    def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[StreamEvent]:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          id: Unique session identifier

          input: Natural language instruction or Action object

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the action

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | Stream[StreamEvent]:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          id: Unique session identifier

          input: Natural language instruction or Action object

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the action

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["input"], ["input", "stream_response"])
    def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | Stream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_act_params.SessionActParamsStreaming
                if stream_response
                else session_act_params.SessionActParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionActResponse,
            stream=stream_response or False,
            stream_cls=Stream[StreamEvent],
        )

    def end(
        self,
        id: str,
        *,
        _force_body: object | Omit = omit,
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
                    "x-sent-at": _format_x_sent_at(x_sent_at),
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/v1/sessions/{id}/end",
            body={},  # Empty object to satisfy Content-Type requirement
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionEndResponse,
        )

    @overload
    def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[StreamEvent]:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the agent

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: bool,
        frame_id: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | Stream[StreamEvent]:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the agent

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["agent_config", "execute_options"], ["agent_config", "execute_options", "stream_response"])
    def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | Stream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_execute_params.SessionExecuteParamsStreaming
                if stream_response
                else session_execute_params.SessionExecuteParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExecuteResponse,
            stream=stream_response or False,
            stream_cls=Stream[StreamEvent],
        )

    @overload
    def extract(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def extract(
        self,
        id: str,
        *,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[StreamEvent]:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the extraction

          instruction: Natural language instruction for what to extract

          schema: JSON Schema defining the structure of data to extract

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def extract(
        self,
        id: str,
        *,
        stream_response: bool,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse | Stream[StreamEvent]:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the extraction

          instruction: Natural language instruction for what to extract

          schema: JSON Schema defining the structure of data to extract

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    def extract(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse | Stream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_extract_params.SessionExtractParamsStreaming
                if stream_response
                else session_extract_params.SessionExtractParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExtractResponse,
            stream=stream_response or False,
            stream_cls=Stream[StreamEvent],
        )

    def navigate(
        self,
        id: str,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        stream_response: bool | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

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
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_navigate_params.SessionNavigateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionNavigateResponse,
        )

    @overload
    def observe(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def observe(
        self,
        id: str,
        *,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[StreamEvent]:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the observation

          instruction: Natural language instruction for what actions to find

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def observe(
        self,
        id: str,
        *,
        stream_response: bool,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | Stream[StreamEvent]:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the observation

          instruction: Natural language instruction for what actions to find

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    def observe(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | Stream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_observe_params.SessionObserveParamsStreaming
                if stream_response
                else session_observe_params.SessionObserveParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionObserveResponse,
            stream=stream_response or False,
            stream_cls=Stream[StreamEvent],
        )

    def start(
        self,
        *,
        model_name: str,
        act_timeout_ms: float | Omit = omit,
        browser: session_start_params.Browser | Omit = omit,
        browserbase_session_create_params: session_start_params.BrowserbaseSessionCreateParams | Omit = omit,
        browserbase_session_id: str | Omit = omit,
        dom_settle_timeout_ms: float | Omit = omit,
        experimental: bool | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: Literal[0, 1, 2] | Omit = omit,
        wait_for_captcha_solves: bool | Omit = omit,
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

          act_timeout_ms: Timeout in ms for act operations (deprecated, v2 only)

          browserbase_session_id: Existing Browserbase session ID to resume

          dom_settle_timeout_ms: Timeout in ms to wait for DOM to settle

          self_heal: Enable self-healing for failed actions

          system_prompt: Custom system prompt for AI operations

          verbose: Logging verbosity level (0=quiet, 1=normal, 2=debug)

          wait_for_captcha_solves: Wait for captcha solves (deprecated, v2 only)

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if _requires_browserbase_credentials(self._client, browser):
            missing: list[str] = []
            if not self._client.browserbase_api_key:
                missing.append("browserbase_api_key")
            if not self._client.browserbase_project_id:
                missing.append("browserbase_project_id")
            if missing:
                raise StagehandError(
                    f"Browserbase credentials are required when launching a Browserbase browser: missing {', '.join(missing)}."
                )
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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

    @overload
    async def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[StreamEvent]:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          id: Unique session identifier

          input: Natural language instruction or Action object

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the action

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | AsyncStream[StreamEvent]:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          id: Unique session identifier

          input: Natural language instruction or Action object

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the action

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["input"], ["input", "stream_response"])
    async def act(
        self,
        id: str,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | AsyncStream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_act_params.SessionActParamsStreaming
                if stream_response
                else session_act_params.SessionActParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionActResponse,
            stream=stream_response or False,
            stream_cls=AsyncStream[StreamEvent],
        )

    async def end(
        self,
        id: str,
        *,
        _force_body: object | Omit = omit,
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
                    "x-sent-at": _format_x_sent_at(x_sent_at),
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/v1/sessions/{id}/end",
            body={},  # Empty object to satisfy Content-Type requirement
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionEndResponse,
        )

    @overload
    async def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[StreamEvent]:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the agent

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: bool,
        frame_id: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | AsyncStream[StreamEvent]:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the agent

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["agent_config", "execute_options"], ["agent_config", "execute_options", "stream_response"])
    async def execute(
        self,
        id: str,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | AsyncStream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_execute_params.SessionExecuteParamsStreaming
                if stream_response
                else session_execute_params.SessionExecuteParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExecuteResponse,
            stream=stream_response or False,
            stream_cls=AsyncStream[StreamEvent],
        )

    @overload
    async def extract(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def extract(
        self,
        id: str,
        *,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[StreamEvent]:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the extraction

          instruction: Natural language instruction for what to extract

          schema: JSON Schema defining the structure of data to extract

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def extract(
        self,
        id: str,
        *,
        stream_response: bool,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse | AsyncStream[StreamEvent]:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the extraction

          instruction: Natural language instruction for what to extract

          schema: JSON Schema defining the structure of data to extract

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    async def extract(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        schema: Dict[str, object] | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse | AsyncStream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_extract_params.SessionExtractParamsStreaming
                if stream_response
                else session_extract_params.SessionExtractParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionExtractResponse,
            stream=stream_response or False,
            stream_cls=AsyncStream[StreamEvent],
        )

    async def navigate(
        self,
        id: str,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        stream_response: bool | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

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
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_navigate_params.SessionNavigateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionNavigateResponse,
        )

    @overload
    async def observe(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
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

          stream_response: Whether to stream the response via SSE

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def observe(
        self,
        id: str,
        *,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[StreamEvent]:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the observation

          instruction: Natural language instruction for what actions to find

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def observe(
        self,
        id: str,
        *,
        stream_response: bool,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | AsyncStream[StreamEvent]:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          id: Unique session identifier

          stream_response: Whether to stream the response via SSE

          frame_id: Target frame ID for the observation

          instruction: Natural language instruction for what actions to find

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    async def observe(
        self,
        id: str,
        *,
        frame_id: str | Omit = omit,
        instruction: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | AsyncStream[StreamEvent]:
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
                    "stream_response": stream_response,
                },
                session_observe_params.SessionObserveParamsStreaming
                if stream_response
                else session_observe_params.SessionObserveParamsNonStreaming,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionObserveResponse,
            stream=stream_response or False,
            stream_cls=AsyncStream[StreamEvent],
        )

    async def start(
        self,
        *,
        model_name: str,
        act_timeout_ms: float | Omit = omit,
        browser: session_start_params.Browser | Omit = omit,
        browserbase_session_create_params: session_start_params.BrowserbaseSessionCreateParams | Omit = omit,
        browserbase_session_id: str | Omit = omit,
        dom_settle_timeout_ms: float | Omit = omit,
        experimental: bool | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: Literal[0, 1, 2] | Omit = omit,
        wait_for_captcha_solves: bool | Omit = omit,
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

          act_timeout_ms: Timeout in ms for act operations (deprecated, v2 only)

          browserbase_session_id: Existing Browserbase session ID to resume

          dom_settle_timeout_ms: Timeout in ms to wait for DOM to settle

          self_heal: Enable self-healing for failed actions

          system_prompt: Custom system prompt for AI operations

          verbose: Logging verbosity level (0=quiet, 1=normal, 2=debug)

          wait_for_captcha_solves: Wait for captcha solves (deprecated, v2 only)

          x_sent_at: ISO timestamp when request was sent

          x_stream_response: Whether to stream the response via SSE

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if _requires_browserbase_credentials(self._client, browser):
            missing: list[str] = []
            if not self._client.browserbase_api_key:
                missing.append("browserbase_api_key")
            if not self._client.browserbase_project_id:
                missing.append("browserbase_project_id")
            if missing:
                raise StagehandError(
                    f"Browserbase credentials are required when launching a Browserbase browser: missing {', '.join(missing)}."
                )
        extra_headers = {
            **strip_not_given(
                {
                    "x-sent-at": _format_x_sent_at(x_sent_at),
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
