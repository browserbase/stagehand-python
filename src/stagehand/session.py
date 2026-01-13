# Manually maintained helpers (not generated).

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union, Mapping, TypeVar, cast
from datetime import datetime
from typing_extensions import Unpack, Literal

import httpx

from .types import (
    session_act_params,
    session_execute_params,
    session_extract_params,
    session_observe_params,
    session_navigate_params,
)
from ._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .types.session_act_response import SessionActResponse
from .types.session_end_response import SessionEndResponse
from .types.session_start_response import Data as SessionStartResponseData, SessionStartResponse
from .types.session_execute_response import SessionExecuteResponse
from .types.session_extract_response import SessionExtractResponse
from .types.session_observe_response import SessionObserveResponse
from .types.session_navigate_response import SessionNavigateResponse

TSessionParams = TypeVar("TSessionParams", bound=Mapping[str, Any])


def _with_default_frame_id(params: TSessionParams) -> TSessionParams:
    prepared = dict(params)
    if "frame_id" not in prepared:
        prepared["frame_id"] = ""
    return cast(TSessionParams, prepared)

if TYPE_CHECKING:
    from ._client import Stagehand, AsyncStagehand


class Session(SessionStartResponse):
    """A Stagehand session bound to a specific `session_id`."""

    def __init__(self, client: Stagehand, id: str, data: SessionStartResponseData, success: bool) -> None:
        # Must call super().__init__() first to initialize Pydantic's __pydantic_extra__ before setting attributes
        super().__init__(data=data, success=success)
        self._client = client
        self.id = id
    

    def navigate(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_navigate_params.SessionNavigateParams],
    ) -> SessionNavigateResponse:
        return self._client.sessions.navigate(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    def act(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_act_params.SessionActParamsNonStreaming],
    ) -> SessionActResponse:
        return self._client.sessions.act(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    def observe(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_observe_params.SessionObserveParamsNonStreaming],
    ) -> SessionObserveResponse:
        return self._client.sessions.observe(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    def extract(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_extract_params.SessionExtractParamsNonStreaming],
    ) -> SessionExtractResponse:
        return self._client.sessions.extract(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    def execute(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_execute_params.SessionExecuteParamsNonStreaming],
    ) -> SessionExecuteResponse:
        return self._client.sessions.execute(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    def end(
        self,
        *,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        return self._client.sessions.end(
            id=self.id,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )


class AsyncSession(SessionStartResponse):
    """Async variant of `Session`."""

    def __init__(self, client: AsyncStagehand, id: str, data: SessionStartResponseData, success: bool) -> None:
        # Must call super().__init__() first to initialize Pydantic's __pydantic_extra__ before setting attributes
        super().__init__(data=data, success=success)
        self._client = client
        self.id = id

    async def navigate(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_navigate_params.SessionNavigateParams],
    ) -> SessionNavigateResponse:
        return await self._client.sessions.navigate(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    async def act(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_act_params.SessionActParamsNonStreaming],
    ) -> SessionActResponse:
        return await self._client.sessions.act(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    async def observe(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_observe_params.SessionObserveParamsNonStreaming],
    ) -> SessionObserveResponse:
        return await self._client.sessions.observe(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    async def extract(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_extract_params.SessionExtractParamsNonStreaming],
    ) -> SessionExtractResponse:
        return await self._client.sessions.extract(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    async def execute(
        self,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_execute_params.SessionExecuteParamsNonStreaming],
    ) -> SessionExecuteResponse:
        return await self._client.sessions.execute(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_with_default_frame_id(params),
        )

    async def end(
        self,
        *,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        return await self._client.sessions.end(
            id=self.id,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
