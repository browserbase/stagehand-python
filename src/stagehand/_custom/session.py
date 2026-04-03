from __future__ import annotations

import inspect
import logging
from typing import TYPE_CHECKING, Any, Type, Mapping, cast
from typing_extensions import Unpack, Literal, Protocol

import httpx
from pydantic import BaseModel, ConfigDict

from ..types import (
    session_act_params,
    session_start_params,
    session_execute_params,
    session_extract_params,
    session_observe_params,
    session_navigate_params,
)
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import lru_cache
from .._constants import RAW_RESPONSE_HEADER
from .._exceptions import StagehandError
from ..resources.sessions import SessionsResource, AsyncSessionsResource
from ..types.session_act_response import SessionActResponse
from ..types.session_end_response import SessionEndResponse
from ..types.session_start_response import Data as SessionStartResponseData, SessionStartResponse
from ..types.session_execute_response import SessionExecuteResponse
from ..types.session_extract_response import SessionExtractResponse
from ..types.session_observe_response import SessionObserveResponse
from ..types.session_navigate_response import SessionNavigateResponse

if TYPE_CHECKING:
    from .._client import Stagehand, AsyncStagehand

logger = logging.getLogger(__name__)


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
    if page is None or "frame_id" in params:
        return params
    return {**params, "frame_id": _extract_frame_id_from_playwright_page(page)}


async def _maybe_inject_frame_id_async(params: dict[str, Any], page: Any | None) -> dict[str, Any]:
    if page is None or "frame_id" in params:
        return params
    return {**params, "frame_id": await _extract_frame_id_from_playwright_page_async(page)}


def _sync_session_call(
    session: Session,
    method_name: str,
    *,
    page: Any | None,
    extra_headers: Headers | None,
    extra_query: Query | None,
    extra_body: Body | None,
    timeout: float | httpx.Timeout | None | NotGiven,
    params: dict[str, Any],
) -> Any:
    method = getattr(session._client.sessions, method_name)
    return method(
        id=session.id,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        **_maybe_inject_frame_id(params, page),
    )


async def _async_session_call(
    session: AsyncSession,
    method_name: str,
    *,
    page: Any | None,
    extra_headers: Headers | None,
    extra_query: Query | None,
    extra_body: Body | None,
    timeout: float | httpx.Timeout | None | NotGiven,
    params: dict[str, Any],
) -> Any:
    method = getattr(session._client.sessions, method_name)
    return await method(
        id=session.id,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        **(await _maybe_inject_frame_id_async(params, page)),
    )


class Session(SessionStartResponse):
    """A Stagehand session bound to a specific `session_id`."""

    def __init__(self, client: Stagehand, id: str, data: SessionStartResponseData, success: bool) -> None:
        # Must call super().__init__() first to initialize Pydantic's __pydantic_extra__
        # before setting attributes.
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
        return cast(
            SessionNavigateResponse,
            _sync_session_call(
                self,
                "navigate",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
            ),
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
            _sync_session_call(
                self,
                "act",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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
            _sync_session_call(
                self,
                "observe",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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
            _sync_session_call(
                self,
                "extract",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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
            _sync_session_call(
                self,
                "execute",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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
        # Must call super().__init__() first to initialize Pydantic's __pydantic_extra__
        # before setting attributes.
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
        return cast(
            SessionNavigateResponse,
            await _async_session_call(
                self,
                "navigate",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
            ),
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
            await _async_session_call(
                self,
                "act",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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
            await _async_session_call(
                self,
                "observe",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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
            await _async_session_call(
                self,
                "extract",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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
            await _async_session_call(
                self,
                "execute",
                page=page,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                params=dict(params),
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


def is_pydantic_model(schema: Any) -> bool:
    return inspect.isclass(schema) and issubclass(schema, BaseModel)


def pydantic_model_to_json_schema(schema: Type[BaseModel]) -> dict[str, object]:
    schema.model_rebuild()
    return cast(dict[str, object], schema.model_json_schema())


def validate_extract_response(
    result: object,
    schema: Type[BaseModel],
    *,
    strict_response_validation: bool,
) -> object:
    validation_schema = _validation_schema(schema, strict_response_validation)
    try:
        return validation_schema.model_validate(result)
    except Exception:
        try:
            normalized = _convert_dict_keys_to_snake_case(result)
            return validation_schema.model_validate(normalized)
        except Exception:
            logger.warning(
                "Failed to validate extracted data against schema %s. Returning raw data.",
                schema.__name__,
            )
            return result


@lru_cache(maxsize=256)
def _validation_schema(schema: Type[BaseModel], strict_response_validation: bool) -> Type[BaseModel]:
    extra_behavior: Literal["allow", "forbid"] = "forbid" if strict_response_validation else "allow"
    validation_schema = cast(
        Type[BaseModel],
        type(
            f"{schema.__name__}ExtractValidation",
            (schema,),
            {
                "__module__": schema.__module__,
                "model_config": ConfigDict(extra=extra_behavior),
            },
        ),
    )
    validation_schema.model_rebuild(force=True)
    return validation_schema


def _camel_to_snake(name: str) -> str:
    chars: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i != 0 and not name[i - 1].isupper():
            chars.append("_")
        chars.append(ch.lower())
    return "".join(chars)


def _convert_dict_keys_to_snake_case(data: Any) -> Any:
    if isinstance(data, dict):
        items = cast(dict[object, object], data).items()
        return {
            _camel_to_snake(k) if isinstance(k, str) else k: _convert_dict_keys_to_snake_case(v)
            for k, v in items
        }
    if isinstance(data, list):
        return [_convert_dict_keys_to_snake_case(item) for item in cast(list[object], data)]
    return data


def _with_schema(
    params: Mapping[str, object],
    schema: dict[str, object] | type | None,
) -> session_extract_params.SessionExtractParamsNonStreaming:
    api_params = dict(params)
    if schema is not None:
        api_params["schema"] = cast(Any, schema)
    return cast(session_extract_params.SessionExtractParamsNonStreaming, api_params)


def _resolve_extract_schema(
    *,
    schema: dict[str, object] | type | None,
    params: dict[str, object],
) -> tuple[Type[BaseModel] | None, dict[str, object] | type | None]:
    params_schema_obj = params.pop("schema", None)
    params_schema: dict[str, object] | type | None
    if params_schema_obj is None:
        params_schema = params_schema_obj
    elif isinstance(params_schema_obj, dict):
        params_schema = cast(dict[str, object], params_schema_obj)
    elif isinstance(params_schema_obj, type):
        params_schema = params_schema_obj
    else:
        params_schema = None

    resolved_schema = schema if schema is not None else params_schema

    if not is_pydantic_model(resolved_schema):
        return None, resolved_schema

    pydantic_cls = cast(Type[BaseModel], resolved_schema)
    return pydantic_cls, pydantic_model_to_json_schema(pydantic_cls)


def _apply_extract_validation(
    response: SessionExtractResponse,
    *,
    schema: Type[BaseModel] | None,
    strict_response_validation: bool,
) -> SessionExtractResponse:
    if schema is not None and response.data and response.data.result is not None:
        response.data.result = validate_extract_response(
            response.data.result,
            schema,
            strict_response_validation=strict_response_validation,
        )
    return response


_ORIGINAL_SESSION_EXTRACT = Session.extract
_ORIGINAL_ASYNC_SESSION_EXTRACT = AsyncSession.extract


def _sync_extract(  # type: ignore[override, misc]
    self: Session,
    *,
    schema: dict[str, object] | type | None = None,
    page: Any | None = None,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = not_given,
    **params: Unpack[session_extract_params.SessionExtractParamsNonStreaming],  # pyright: ignore[reportGeneralTypeIssues]
) -> SessionExtractResponse:
    raw_params = dict(params)
    pydantic_cls, resolved_schema = _resolve_extract_schema(schema=schema, params=raw_params)
    response = _ORIGINAL_SESSION_EXTRACT(
        self,
        page=page,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        **_with_schema(raw_params, resolved_schema),
    )
    return _apply_extract_validation(
        response,
        schema=pydantic_cls,
        strict_response_validation=self._client._strict_response_validation,
    )


async def _async_extract(  # type: ignore[override, misc]
    self: AsyncSession,
    *,
    schema: dict[str, object] | type | None = None,
    page: Any | None = None,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = not_given,
    **params: Unpack[session_extract_params.SessionExtractParamsNonStreaming],  # pyright: ignore[reportGeneralTypeIssues]
) -> SessionExtractResponse:
    raw_params = dict(params)
    pydantic_cls, resolved_schema = _resolve_extract_schema(schema=schema, params=raw_params)
    response = await _ORIGINAL_ASYNC_SESSION_EXTRACT(
        self,
        page=page,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        **_with_schema(raw_params, resolved_schema),
    )
    return _apply_extract_validation(
        response,
        schema=pydantic_cls,
        strict_response_validation=self._client._strict_response_validation,
    )


def install_pydantic_extract_patch() -> None:
    if getattr(Session.extract, "__stagehand_pydantic_extract_patch__", False):
        return

    _sync_extract.__module__ = _ORIGINAL_SESSION_EXTRACT.__module__
    _sync_extract.__name__ = _ORIGINAL_SESSION_EXTRACT.__name__
    _sync_extract.__qualname__ = _ORIGINAL_SESSION_EXTRACT.__qualname__
    _sync_extract.__doc__ = _ORIGINAL_SESSION_EXTRACT.__doc__
    setattr(_sync_extract, "__stagehand_pydantic_extract_patch__", True)  # noqa: B010

    _async_extract.__module__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__module__
    _async_extract.__name__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__name__
    _async_extract.__qualname__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__qualname__
    _async_extract.__doc__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__doc__
    setattr(_async_extract, "__stagehand_pydantic_extract_patch__", True)  # noqa: B010

    Session.extract = _sync_extract  # type: ignore[assignment]
    AsyncSession.extract = _async_extract  # type: ignore[assignment]


def _resolve_start_browser(client: Any, browser: session_start_params.Browser | Omit) -> session_start_params.Browser | Omit:
    if browser is not omit or getattr(client, "_server_mode", None) != "local":
        return browser

    if client.browserbase_api_key is None or client.browserbase_project_id is None:
        raise StagehandError(
            "Local server mode without Browserbase credentials requires an explicit local browser, "
            "e.g. browser={'type': 'local'}."
        )

    return {"type": "local"}


def _is_raw_or_streaming_start(extra_headers: Headers | None) -> bool:
    if not extra_headers:
        return False

    header_value = extra_headers.get(RAW_RESPONSE_HEADER)
    return header_value in {"raw", "stream"}


_ORIGINAL_SESSIONS_START = SessionsResource.start
_ORIGINAL_ASYNC_SESSIONS_START = AsyncSessionsResource.start


def _sync_start(
    self: SessionsResource,
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
    x_stream_response: Literal["true", "false"] | Omit = omit,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = not_given,
) -> object:
    start_response = _ORIGINAL_SESSIONS_START(
        self,
        model_name=model_name,
        act_timeout_ms=act_timeout_ms,
        browser=_resolve_start_browser(self._client, browser),
        browserbase_session_create_params=browserbase_session_create_params,
        browserbase_session_id=browserbase_session_id,
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
    if _is_raw_or_streaming_start(extra_headers):
        return start_response
    return Session(self._client, start_response.data.session_id, data=start_response.data, success=start_response.success)


async def _async_start(
    self: AsyncSessionsResource,
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
    x_stream_response: Literal["true", "false"] | Omit = omit,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = not_given,
) -> object:
    start_response = await _ORIGINAL_ASYNC_SESSIONS_START(
        self,
        model_name=model_name,
        act_timeout_ms=act_timeout_ms,
        browser=_resolve_start_browser(self._client, browser),
        browserbase_session_create_params=browserbase_session_create_params,
        browserbase_session_id=browserbase_session_id,
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
    if _is_raw_or_streaming_start(extra_headers):
        return start_response
    return AsyncSession(
        self._client,
        start_response.data.session_id,
        data=start_response.data,
        success=start_response.success,
    )


def install_stainless_session_patches() -> None:
    install_pydantic_extract_patch()

    if getattr(SessionsResource.start, "__stagehand_bound_session_patch__", False):
        return

    _sync_start.__module__ = _ORIGINAL_SESSIONS_START.__module__
    _sync_start.__name__ = _ORIGINAL_SESSIONS_START.__name__
    _sync_start.__qualname__ = _ORIGINAL_SESSIONS_START.__qualname__
    _sync_start.__doc__ = _ORIGINAL_SESSIONS_START.__doc__
    setattr(_sync_start, "__stagehand_bound_session_patch__", True)  # noqa: B010

    _async_start.__module__ = _ORIGINAL_ASYNC_SESSIONS_START.__module__
    _async_start.__name__ = _ORIGINAL_ASYNC_SESSIONS_START.__name__
    _async_start.__qualname__ = _ORIGINAL_ASYNC_SESSIONS_START.__qualname__
    _async_start.__doc__ = _ORIGINAL_ASYNC_SESSIONS_START.__doc__
    setattr(_async_start, "__stagehand_bound_session_patch__", True)  # noqa: B010

    SessionsResource.start = _sync_start  # type: ignore[assignment]
    AsyncSessionsResource.start = _async_start  # type: ignore[assignment]


install_stainless_session_patches()


__all__ = [
    "AsyncSession",
    "Session",
    "install_pydantic_extract_patch",
    "install_stainless_session_patches",
]
