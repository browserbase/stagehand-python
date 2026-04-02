# Manually maintained helpers (not generated).

from __future__ import annotations

import inspect
import logging
from typing import Any, Type, Mapping, cast
from typing_extensions import Unpack, Literal, override

import httpx
from pydantic import BaseModel, ConfigDict

from ..types import session_start_params, session_extract_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import lru_cache
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
from ..types.session_extract_response import SessionExtractResponse

logger = logging.getLogger(__name__)

_ORIGINAL_SESSION_EXTRACT = Session.extract
_ORIGINAL_ASYNC_SESSION_EXTRACT = AsyncSession.extract


def install_pydantic_extract_patch() -> None:
    if getattr(Session.extract, "__stagehand_pydantic_extract_patch__", False):
        return

    Session.extract = _sync_extract  # type: ignore[assignment]
    AsyncSession.extract = _async_extract  # type: ignore[assignment]


def is_pydantic_model(schema: Any) -> bool:
    return inspect.isclass(schema) and issubclass(schema, BaseModel)


def pydantic_model_to_json_schema(schema: Type[BaseModel]) -> dict[str, object]:
    schema.model_rebuild()
    return cast(dict[str, object], schema.model_json_schema())


def validate_extract_response(
    result: object, schema: Type[BaseModel], *, strict_response_validation: bool
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

    pydantic_cls: Type[BaseModel] | None = None
    if is_pydantic_model(resolved_schema):
        pydantic_cls = cast(Type[BaseModel], resolved_schema)
        resolved_schema = pydantic_model_to_json_schema(pydantic_cls)

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

    pydantic_cls: Type[BaseModel] | None = None
    if is_pydantic_model(resolved_schema):
        pydantic_cls = cast(Type[BaseModel], resolved_schema)
        resolved_schema = pydantic_model_to_json_schema(pydantic_cls)

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


install_pydantic_extract_patch()


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
        if browser is omit and getattr(self._client, "_server_mode", None) == "local":
            browser = {"type": "local"}

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
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return Session(self._client, start_response.data.session_id, data=start_response.data, success=start_response.success)


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
        if browser is omit and getattr(self._client, "_server_mode", None) == "local":
            browser = {"type": "local"}

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
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        return AsyncSession(self._client, start_response.data.session_id, data=start_response.data, success=start_response.success)
