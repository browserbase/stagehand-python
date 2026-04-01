"""Custom extract patch installed on top of the session helpers."""

from __future__ import annotations

from typing import Any, cast

import httpx
from typing_extensions import Unpack

from ._pydantic_extract import is_pydantic_model, pydantic_model_to_json_schema, validate_extract_response
from ._types import Body, Headers, NotGiven, Query, not_given
from .session import AsyncSession, Session
from .types import session_extract_params
from .types.session_extract_response import SessionExtractResponse

_ORIGINAL_SESSION_EXTRACT = Session.extract
_ORIGINAL_ASYNC_SESSION_EXTRACT = AsyncSession.extract


def install_pydantic_extract_patch() -> None:
    if getattr(Session.extract, "__stagehand_pydantic_extract_patch__", False):
        return

    Session.extract = _sync_extract  # type: ignore[assignment]
    AsyncSession.extract = _async_extract  # type: ignore[assignment]


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
    params_schema = params.pop("schema", None)  # type: ignore[misc]
    resolved_schema = schema if schema is not None else params_schema

    pydantic_cls: type[Any] | None = None
    if is_pydantic_model(resolved_schema):
        pydantic_cls = resolved_schema  # type: ignore[assignment]
        resolved_schema = pydantic_model_to_json_schema(pydantic_cls)  # type: ignore[arg-type]

    response = _ORIGINAL_SESSION_EXTRACT(
        self,
        page=page,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        **_with_schema(params, resolved_schema),
    )

    if pydantic_cls is not None and response.data and response.data.result is not None:
        response.data.result = validate_extract_response(
            response.data.result,
            pydantic_cls,
            strict_response_validation=self._client._strict_response_validation,
        )

    return response


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
    params_schema = params.pop("schema", None)  # type: ignore[misc]
    resolved_schema = schema if schema is not None else params_schema

    pydantic_cls: type[Any] | None = None
    if is_pydantic_model(resolved_schema):
        pydantic_cls = resolved_schema  # type: ignore[assignment]
        resolved_schema = pydantic_model_to_json_schema(pydantic_cls)  # type: ignore[arg-type]

    response = await _ORIGINAL_ASYNC_SESSION_EXTRACT(
        self,
        page=page,
        extra_headers=extra_headers,
        extra_query=extra_query,
        extra_body=extra_body,
        timeout=timeout,
        **_with_schema(params, resolved_schema),
    )

    if pydantic_cls is not None and response.data and response.data.result is not None:
        response.data.result = validate_extract_response(
            response.data.result,
            pydantic_cls,
            strict_response_validation=self._client._strict_response_validation,
        )

    return response


def _with_schema(
    params: session_extract_params.SessionExtractParamsNonStreaming,
    schema: dict[str, object] | type | None,
) -> session_extract_params.SessionExtractParamsNonStreaming:
    api_params = dict(params)
    if schema is not None:
        api_params["schema"] = cast(Any, schema)
    return cast(session_extract_params.SessionExtractParamsNonStreaming, api_params)


_sync_extract.__module__ = _ORIGINAL_SESSION_EXTRACT.__module__
_sync_extract.__name__ = _ORIGINAL_SESSION_EXTRACT.__name__
_sync_extract.__qualname__ = _ORIGINAL_SESSION_EXTRACT.__qualname__
_sync_extract.__doc__ = _ORIGINAL_SESSION_EXTRACT.__doc__
_sync_extract.__stagehand_pydantic_extract_patch__ = True

_async_extract.__module__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__module__
_async_extract.__name__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__name__
_async_extract.__qualname__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__qualname__
_async_extract.__doc__ = _ORIGINAL_ASYNC_SESSION_EXTRACT.__doc__
_async_extract.__stagehand_pydantic_extract_patch__ = True
