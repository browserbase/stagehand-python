# Manually maintained helpers (not generated).

from __future__ import annotations

from typing import Any
from typing_extensions import Literal, override

import httpx

from ..types import session_start_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._compat import cached_property
from ..session import Session, AsyncSession
from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..types.session_start_response import SessionStartResponse


def _has_explicit_aws_credentials(model_config: dict[str, Any]) -> bool:
    return any(model_config.get(key) for key in ("access_key_id", "secret_access_key", "session_token"))


def _build_default_model_config(
    *,
    model_name: str,
    model_client_options: session_start_params.ModelClientOptions | Omit,
    fallback_api_key: str | None,
) -> dict[str, Any]:
    model_config: dict[str, Any] = {"model_name": model_name}
    if isinstance(model_client_options, dict):
        model_config.update(model_client_options)

    if fallback_api_key and "api_key" not in model_config and not _has_explicit_aws_credentials(model_config):
        model_config["api_key"] = fallback_api_key

    return model_config


class SessionsResourceWithHelpersRawResponse(SessionsResourceWithRawResponse):
    def __init__(self, sessions: SessionsResourceWithHelpers) -> None:  # type: ignore[name-defined]
        super().__init__(sessions)
        self.start = to_raw_response_wrapper(super(SessionsResourceWithHelpers, sessions).start)


class SessionsResourceWithHelpersStreamingResponse(SessionsResourceWithStreamingResponse):
    def __init__(self, sessions: SessionsResourceWithHelpers) -> None:  # type: ignore[name-defined]
        super().__init__(sessions)
        self.start = to_streamed_response_wrapper(super(SessionsResourceWithHelpers, sessions).start)


class AsyncSessionsResourceWithHelpersRawResponse(AsyncSessionsResourceWithRawResponse):
    def __init__(self, sessions: AsyncSessionsResourceWithHelpers) -> None:  # type: ignore[name-defined]
        super().__init__(sessions)
        self.start = async_to_raw_response_wrapper(super(AsyncSessionsResourceWithHelpers, sessions).start)


class AsyncSessionsResourceWithHelpersStreamingResponse(AsyncSessionsResourceWithStreamingResponse):
    def __init__(self, sessions: AsyncSessionsResourceWithHelpers) -> None:  # type: ignore[name-defined]
        super().__init__(sessions)
        self.start = async_to_streamed_response_wrapper(super(AsyncSessionsResourceWithHelpers, sessions).start)


class SessionsResourceWithHelpers(SessionsResource):
    @cached_property
    @override
    def with_raw_response(self) -> SessionsResourceWithHelpersRawResponse:
        return SessionsResourceWithHelpersRawResponse(self)

    @cached_property
    @override
    def with_streaming_response(self) -> SessionsResourceWithHelpersStreamingResponse:
        return SessionsResourceWithHelpersStreamingResponse(self)

    @override
    def start(
        self,
        *,
        model_name: str,
        act_timeout_ms: float | Omit = omit,
        browser: session_start_params.Browser | Omit = omit,
        browserbase_session_create_params: session_start_params.BrowserbaseSessionCreateParams | Omit = omit,
        browserbase_session_id: str | Omit = omit,
        model_client_options: session_start_params.ModelClientOptions | Omit = omit,
        dom_settle_timeout_ms: float | Omit = omit,
        experimental: bool | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: Literal[0, 1, 2] | Omit = omit,
        wait_for_captcha_solves: bool | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        start_response = super().start(
            model_name=model_name,
            act_timeout_ms=act_timeout_ms,
            browser=browser,
            browserbase_session_create_params=browserbase_session_create_params,
            browserbase_session_id=browserbase_session_id,
            model_client_options=model_client_options,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
            experimental=experimental,
            self_heal=self_heal,
            system_prompt=system_prompt,
            verbose=verbose,
            wait_for_captcha_solves=wait_for_captcha_solves,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return Session(
            self._client,
            start_response.data.session_id,
            data=start_response.data,
            success=start_response.success,
            default_model=_build_default_model_config(
                model_name=model_name,
                model_client_options=model_client_options,
                fallback_api_key=self._client.model_api_key,
            ),
        )


class AsyncSessionsResourceWithHelpers(AsyncSessionsResource):
    @cached_property
    @override
    def with_raw_response(self) -> AsyncSessionsResourceWithHelpersRawResponse:
        return AsyncSessionsResourceWithHelpersRawResponse(self)

    @cached_property
    @override
    def with_streaming_response(self) -> AsyncSessionsResourceWithHelpersStreamingResponse:
        return AsyncSessionsResourceWithHelpersStreamingResponse(self)

    @override
    async def start(
        self,
        *,
        model_name: str,
        act_timeout_ms: float | Omit = omit,
        browser: session_start_params.Browser | Omit = omit,
        browserbase_session_create_params: session_start_params.BrowserbaseSessionCreateParams | Omit = omit,
        browserbase_session_id: str | Omit = omit,
        model_client_options: session_start_params.ModelClientOptions | Omit = omit,
        dom_settle_timeout_ms: float | Omit = omit,
        experimental: bool | Omit = omit,
        self_heal: bool | Omit = omit,
        system_prompt: str | Omit = omit,
        verbose: Literal[0, 1, 2] | Omit = omit,
        wait_for_captcha_solves: bool | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncSession:
        start_response: SessionStartResponse = await super().start(
            model_name=model_name,
            act_timeout_ms=act_timeout_ms,
            browser=browser,
            browserbase_session_create_params=browserbase_session_create_params,
            browserbase_session_id=browserbase_session_id,
            model_client_options=model_client_options,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
            experimental=experimental,
            self_heal=self_heal,
            system_prompt=system_prompt,
            verbose=verbose,
            wait_for_captcha_solves=wait_for_captcha_solves,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return AsyncSession(
            self._client,
            start_response.data.session_id,
            data=start_response.data,
            success=start_response.success,
            default_model=_build_default_model_config(
                model_name=model_name,
                model_client_options=model_client_options,
                fallback_api_key=self._client.model_api_key,
            ),
        )
