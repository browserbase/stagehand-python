# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{id}/act",
            body=maybe_transform(body, session_act_params.SessionActParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def end(
        self,
        id: object,
        *,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Terminates the browser session and releases all associated resources.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{id}/end",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def execute_agent(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{id}/agentExecute",
            body=maybe_transform(body, session_execute_agent_params.SessionExecuteAgentParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def extract(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{id}/extract",
            body=maybe_transform(body, session_extract_params.SessionExtractParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def navigate(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Navigates the browser to the specified URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{id}/navigate",
            body=maybe_transform(body, session_navigate_params.SessionNavigateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def observe(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/sessions/{id}/observe",
            body=maybe_transform(body, session_observe_params.SessionObserveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def start(
        self,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Creates a new browser session with the specified configuration.

        Returns a
        session ID used for all subsequent operations.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            "/sessions/start",
            body=maybe_transform(body, session_start_params.SessionStartParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
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
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Executes a browser action using natural language instructions or a predefined
        Action object.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{id}/act",
            body=await async_maybe_transform(body, session_act_params.SessionActParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def end(
        self,
        id: object,
        *,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Terminates the browser session and releases all associated resources.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{id}/end",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def execute_agent(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Runs an autonomous AI agent that can perform complex multi-step browser tasks.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{id}/agentExecute",
            body=await async_maybe_transform(body, session_execute_agent_params.SessionExecuteAgentParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def extract(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Extracts structured data from the current page using AI-powered analysis.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{id}/extract",
            body=await async_maybe_transform(body, session_extract_params.SessionExtractParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def navigate(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Navigates the browser to the specified URL.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{id}/navigate",
            body=await async_maybe_transform(body, session_navigate_params.SessionNavigateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def observe(
        self,
        id: object,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Identifies and returns available actions on the current page that match the
        given instruction.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/sessions/{id}/observe",
            body=await async_maybe_transform(body, session_observe_params.SessionObserveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def start(
        self,
        *,
        body: object | Omit = omit,
        x_language: object | Omit = omit,
        x_sdk_version: object | Omit = omit,
        x_sent_at: object | Omit = omit,
        x_stream_response: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """Creates a new browser session with the specified configuration.

        Returns a
        session ID used for all subsequent operations.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "x-language": str(x_language) if is_given(x_language) else not_given,
                    "x-sdk-version": str(x_sdk_version) if is_given(x_sdk_version) else not_given,
                    "x-sent-at": str(x_sent_at) if is_given(x_sent_at) else not_given,
                    "x-stream-response": str(x_stream_response) if is_given(x_stream_response) else not_given,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            "/sessions/start",
            body=await async_maybe_transform(body, session_start_params.SessionStartParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
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
