# Manually maintained helpers (not generated).

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, cast
from typing_extensions import Unpack, Literal, Protocol

import httpx

from .types import (
    session_act_params,
    session_execute_params,
    session_extract_params,
    session_observe_params,
    session_navigate_params,
)
from ._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ._exceptions import StagehandError
from .types.session_act_response import SessionActResponse
from .types.session_end_response import SessionEndResponse
from .types.session_start_response import Data as SessionStartResponseData, SessionStartResponse
from .types.session_execute_response import SessionExecuteResponse
from .types.session_extract_response import SessionExtractResponse
from .types.session_observe_response import SessionObserveResponse
from .types.session_navigate_response import SessionNavigateResponse

if TYPE_CHECKING:
    from ._client import Stagehand, AsyncStagehand


class _PlaywrightCDPSession(Protocol):
    def send(self, method: str, params: Any = ...) -> Any:  # noqa: ANN401
        ...


class _PlaywrightContext(Protocol):
    def new_cdp_session(self, page: Any) -> Any:  # noqa: ANN401
        ...


def _extract_frame_id_from_playwright_page(page: Any) -> str:
    context = getattr(page, "context", None)
    if context is None:
        raise StagehandError("page must be a Playwright Page with a .context attribute")

    if callable(context):
        context = context()

    new_cdp_session = getattr(context, "new_cdp_session", None)
    if not callable(new_cdp_session):
        raise StagehandError(
            "page must be a Playwright Page; expected page.context.new_cdp_session(...) to exist"
        )

    pw_context = cast(_PlaywrightContext, context)
    cdp = pw_context.new_cdp_session(page)
    if inspect.isawaitable(cdp):
        raise StagehandError(
            "Expected a synchronous Playwright Page, but received an async CDP session; use AsyncSession methods"
        )

    send = getattr(cdp, "send", None)
    if not callable(send):
        raise StagehandError("Playwright CDP session missing .send(...) method")

    pw_cdp = cast(_PlaywrightCDPSession, cdp)
    result = pw_cdp.send("Page.getFrameTree")
    if inspect.isawaitable(result):
        raise StagehandError(
            "Expected a synchronous Playwright Page, but received an async CDP session; use AsyncSession methods"
        )

    try:
        return cast(str, result["frameTree"]["frame"]["id"])
    except Exception as e:  # noqa: BLE001
        raise StagehandError("Failed to extract frame id from Playwright CDP Page.getFrameTree response") from e


async def _extract_frame_id_from_playwright_page_async(page: Any) -> str:
    context = getattr(page, "context", None)
    if context is None:
        raise StagehandError("page must be a Playwright Page with a .context attribute")

    if callable(context):
        context = context()

    new_cdp_session = getattr(context, "new_cdp_session", None)
    if not callable(new_cdp_session):
        raise StagehandError(
            "page must be a Playwright Page; expected page.context.new_cdp_session(...) to exist"
        )

    pw_context = cast(_PlaywrightContext, context)
    cdp = pw_context.new_cdp_session(page)
    if inspect.isawaitable(cdp):
        cdp = await cdp

    send = getattr(cdp, "send", None)
    if not callable(send):
        raise StagehandError("Playwright CDP session missing .send(...) method")

    pw_cdp = cast(_PlaywrightCDPSession, cdp)
    result = pw_cdp.send("Page.getFrameTree")
    if inspect.isawaitable(result):
        result = await result

    try:
        return cast(str, result["frameTree"]["frame"]["id"])
    except Exception as e:  # noqa: BLE001
        raise StagehandError("Failed to extract frame id from Playwright CDP Page.getFrameTree response") from e


def _maybe_inject_frame_id(params: dict[str, Any], page: Any | None) -> dict[str, Any]:
    if page is None:
        return params
    if "frame_id" in params:
        return params
    return {**params, "frame_id": _extract_frame_id_from_playwright_page(page)}


async def _maybe_inject_frame_id_async(params: dict[str, Any], page: Any | None) -> dict[str, Any]:
    if page is None:
        return params
    if "frame_id" in params:
        return params
    return {**params, "frame_id": await _extract_frame_id_from_playwright_page_async(page)}


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
        page: Any | None = None,
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
            **_maybe_inject_frame_id(dict(params), page),
        )

    def act(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_act_params.SessionActParamsNonStreaming],
    ) -> SessionActResponse:
        return cast(
            SessionActResponse,
            self._client.sessions.act(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_maybe_inject_frame_id(dict(params), page),
            ),
        )

    def observe(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_observe_params.SessionObserveParamsNonStreaming],
    ) -> SessionObserveResponse:
        return cast(
            SessionObserveResponse,
            self._client.sessions.observe(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_maybe_inject_frame_id(dict(params), page),
            ),
        )

    def extract(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_extract_params.SessionExtractParamsNonStreaming],
    ) -> SessionExtractResponse:
        return cast(
            SessionExtractResponse,
            self._client.sessions.extract(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_maybe_inject_frame_id(dict(params), page),
            ),
        )

    def execute(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_execute_params.SessionExecuteParamsNonStreaming],
    ) -> SessionExecuteResponse:
        return cast(
            SessionExecuteResponse,
            self._client.sessions.execute(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **_maybe_inject_frame_id(dict(params), page),
            ),
        )

    def end(
        self,
        *,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        return self._client.sessions.end(
            id=self.id,
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
        page: Any | None = None,
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
            **(await _maybe_inject_frame_id_async(dict(params), page)),
        )

    async def act(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_act_params.SessionActParamsNonStreaming],
    ) -> SessionActResponse:
        return cast(
            SessionActResponse,
            await self._client.sessions.act(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **(await _maybe_inject_frame_id_async(dict(params), page)),
            ),
        )

    async def observe(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_observe_params.SessionObserveParamsNonStreaming],
    ) -> SessionObserveResponse:
        return cast(
            SessionObserveResponse,
            await self._client.sessions.observe(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **(await _maybe_inject_frame_id_async(dict(params), page)),
            ),
        )

    async def extract(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_extract_params.SessionExtractParamsNonStreaming],
    ) -> SessionExtractResponse:
        return cast(
            SessionExtractResponse,
            await self._client.sessions.extract(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **(await _maybe_inject_frame_id_async(dict(params), page)),
            ),
        )

    async def execute(
        self,
        *,
        page: Any | None = None,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
        **params: Unpack[session_execute_params.SessionExecuteParamsNonStreaming],
    ) -> SessionExecuteResponse:
        return cast(
            SessionExecuteResponse,
            await self._client.sessions.execute(
            id=self.id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            **(await _maybe_inject_frame_id_async(dict(params), page)),
            ),
        )

    async def end(
        self,
        *,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        return await self._client.sessions.end(
            id=self.id,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
