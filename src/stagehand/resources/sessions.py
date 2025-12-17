# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import session_start_params
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

        self.start = to_raw_response_wrapper(
            sessions.start,
        )


class AsyncSessionsResourceWithRawResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.start = async_to_raw_response_wrapper(
            sessions.start,
        )


class SessionsResourceWithStreamingResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.start = to_streamed_response_wrapper(
            sessions.start,
        )


class AsyncSessionsResourceWithStreamingResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.start = async_to_streamed_response_wrapper(
            sessions.start,
        )
