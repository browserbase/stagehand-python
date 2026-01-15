# Manually maintained helpers (not generated).

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import session_start_params
from .._constants import RAW_RESPONSE_HEADER
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ..session import Session, AsyncSession
from .sessions import SessionsResource, AsyncSessionsResource
from ..types.session_start_response import SessionStartResponse


class SessionsResourceWithHelpers(SessionsResource):
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
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        # Preserve generated `.with_raw_response.start(...)` and `.with_streaming_response.start(...)`
        # behavior: those wrappers set `X-Stainless-Raw-Response` and expect an APIResponse.
        if extra_headers is not None and RAW_RESPONSE_HEADER in extra_headers:
            return super().start(
                model_name=model_name,
                act_timeout_ms=act_timeout_ms,
                browser=browser,
                browserbase_session_create_params=browserbase_session_create_params,
                browserbase_session_id=browserbase_session_id,
                dom_settle_timeout_ms=dom_settle_timeout_ms,
                experimental=experimental,
                self_heal=self_heal,
                system_prompt=system_prompt,
                verbose=verbose,
                wait_for_captcha_solves=wait_for_captcha_solves,
                x_sent_at=x_sent_at,
                x_stream_response=x_stream_response,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
        start_response = super().start(
            model_name=model_name,
            act_timeout_ms=act_timeout_ms,
            browser=browser,
            browserbase_session_create_params=browserbase_session_create_params,
            browserbase_session_id=browserbase_session_id,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
            experimental=experimental,
            self_heal=self_heal,
            system_prompt=system_prompt,
            verbose=verbose,
            wait_for_captcha_solves=wait_for_captcha_solves,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return Session(self._client, start_response.data.session_id, data=start_response.data, success=start_response.success)


class AsyncSessionsResourceWithHelpers(AsyncSessionsResource):
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
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncSession:
        # Preserve generated `.with_raw_response.start(...)` and `.with_streaming_response.start(...)`
        # behavior: those wrappers set `X-Stainless-Raw-Response` and expect an APIResponse.
        if extra_headers is not None and RAW_RESPONSE_HEADER in extra_headers:
            return await super().start(
                model_name=model_name,
                act_timeout_ms=act_timeout_ms,
                browser=browser,
                browserbase_session_create_params=browserbase_session_create_params,
                browserbase_session_id=browserbase_session_id,
                dom_settle_timeout_ms=dom_settle_timeout_ms,
                experimental=experimental,
                self_heal=self_heal,
                system_prompt=system_prompt,
                verbose=verbose,
                wait_for_captcha_solves=wait_for_captcha_solves,
                x_sent_at=x_sent_at,
                x_stream_response=x_stream_response,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )
        start_response: SessionStartResponse = await super().start(
            model_name=model_name,
            act_timeout_ms=act_timeout_ms,
            browser=browser,
            browserbase_session_create_params=browserbase_session_create_params,
            browserbase_session_id=browserbase_session_id,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
            experimental=experimental,
            self_heal=self_heal,
            system_prompt=system_prompt,
            verbose=verbose,
            wait_for_captcha_solves=wait_for_captcha_solves,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return AsyncSession(self._client, start_response.data.session_id, data=start_response.data, success=start_response.success)
