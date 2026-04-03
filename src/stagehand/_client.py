# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping

### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
# Keep the generated client thin: all runtime patch logic lives in `_custom`.
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._models import FinalRequestOptions
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from ._custom.session import install_stainless_session_patches
from ._custom.sea_server import (
    copy_local_mode_kwargs,
    configure_client_base_url,
    close_sync_client_sea_server,
    prepare_sync_client_base_url,
    close_async_client_sea_server,
    prepare_async_client_base_url,
)

### </END CUSTOM CODE>

if TYPE_CHECKING:
    from .resources import sessions

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    from ._custom.sea_server import SeaServerManager
    from .resources.sessions import SessionsResource, AsyncSessionsResource
    ### </END CUSTOM CODE>

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Stagehand",
    "AsyncStagehand",
    "Client",
    "AsyncClient",
]

### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
# Patch the generated resource classes in place so user-facing types stay on the
# original Stainless imports instead of custom wrapper classes.
install_stainless_session_patches()
### </END CUSTOM CODE>


class Stagehand(SyncAPIClient):
    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    # client options
    browserbase_api_key: str | None
    browserbase_project_id: str | None
    model_api_key: str | None
    # These are assigned indirectly by `configure_client_base_url(...)` so the
    # generated class still exposes typed local-mode state for `copy()` and tests.
    _server_mode: Literal["remote", "local"]
    _local_stagehand_binary_path: str | os.PathLike[str] | None
    _local_host: str
    _local_port: int
    _local_headless: bool
    _local_chrome_path: str | None
    _local_ready_timeout_s: float
    _local_shutdown_on_close: bool
    _sea_server: SeaServerManager | None
    ### </END CUSTOM CODE>

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    def __init__(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] = "remote",
        _local_stagehand_binary_path: str | os.PathLike[str] | None = None,
        local_host: str = "127.0.0.1",
        local_port: int = 0,
        local_headless: bool = True,
        local_chrome_path: str | None = None,
        local_ready_timeout_s: float = 10.0,
        local_shutdown_on_close: bool = True,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Stagehand client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `browserbase_api_key` from `BROWSERBASE_API_KEY`
        - `browserbase_project_id` from `BROWSERBASE_PROJECT_ID`

        `model_api_key` is intentionally not inferred from any AI provider environment variable.
        Pass it explicitly when you want the SDK to send `x-model-api-key` on remote requests or
        to forward `MODEL_API_KEY` to the local SEA child process.
        """
        if browserbase_api_key is None:
            browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
        if browserbase_project_id is None:
            browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")

        self.browserbase_api_key = browserbase_api_key
        self.browserbase_project_id = browserbase_project_id

        self.model_api_key = model_api_key

        # Centralize local-mode state hydration and base-url selection in `_custom`
        # so no constructor branching lives in the generated client.
        base_url = configure_client_base_url(
            self,
            server=server,
            _local_stagehand_binary_path=_local_stagehand_binary_path,
            local_host=local_host,
            local_port=local_port,
            local_headless=local_headless,
            local_chrome_path=local_chrome_path,
            local_ready_timeout_s=local_ready_timeout_s,
            local_shutdown_on_close=local_shutdown_on_close,
            base_url=base_url,
            model_api_key=model_api_key,
        )
    ### </END CUSTOM CODE>

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = Stream

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    @override
    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        # Start the local SEA server lazily on first request instead of at client
        # construction time, then swap the base URL to the started process.
        local_base_url = prepare_sync_client_base_url(self)
        if local_base_url is not None:
            self.base_url = local_base_url
        return super()._prepare_options(options)

    @override
    def close(self) -> None:
        try:
            super().close()
        finally:
            # Tear down the managed SEA process after HTTP resources close.
            close_sync_client_sea_server(self)
    ### </END CUSTOM CODE>

    @cached_property
    def sessions(self) -> SessionsResource:
        from .resources.sessions import SessionsResource

        return SessionsResource(self)

    @cached_property
    def with_raw_response(self) -> StagehandWithRawResponse:
        return StagehandWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StagehandWithStreamedResponse:
        return StagehandWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._bb_api_key_auth, **self._bb_project_id_auth, **self._llm_model_api_key_auth}

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    @property
    def _bb_api_key_auth(self) -> dict[str, str]:
        browserbase_api_key = self.browserbase_api_key
        return {"x-bb-api-key": browserbase_api_key} if browserbase_api_key else {}

    @property
    def _bb_project_id_auth(self) -> dict[str, str]:
        browserbase_project_id = self.browserbase_project_id
        return {"x-bb-project-id": browserbase_project_id} if browserbase_project_id else {}

    @property
    def _llm_model_api_key_auth(self) -> dict[str, str]:
        model_api_key = self.model_api_key
        return {"x-model-api-key": model_api_key} if model_api_key else {}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "x-language": "python",
            "x-sdk-version": __version__,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }
    ### </END CUSTOM CODE>

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    def copy(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] | None = None,
        _local_stagehand_binary_path: str | os.PathLike[str] | None = None,
        local_host: str | None = None,
        local_port: int | None = None,
        local_headless: bool | None = None,
        local_chrome_path: str | None = None,
        local_ready_timeout_s: float | None = None,
        local_shutdown_on_close: bool | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            browserbase_api_key=browserbase_api_key or self.browserbase_api_key,
            browserbase_project_id=browserbase_project_id or self.browserbase_project_id,
            model_api_key=model_api_key or self.model_api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            # Preserve local-mode configuration when cloning the client without
            # duplicating that branching logic in generated code.
            **copy_local_mode_kwargs(
                self,
                server=server,
                _local_stagehand_binary_path=_local_stagehand_binary_path,
                local_host=local_host,
                local_port=local_port,
                local_headless=local_headless,
                local_chrome_path=local_chrome_path,
                local_ready_timeout_s=local_ready_timeout_s,
                local_shutdown_on_close=local_shutdown_on_close,
            ),
            **_extra_kwargs,
        )
    ### </END CUSTOM CODE>

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncStagehand(AsyncAPIClient):
    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    # client options
    browserbase_api_key: str | None
    browserbase_project_id: str | None
    model_api_key: str | None
    # These are assigned indirectly by `configure_client_base_url(...)` so the
    # generated class still exposes typed local-mode state for `copy()` and tests.
    _server_mode: Literal["remote", "local"]
    _local_stagehand_binary_path: str | os.PathLike[str] | None
    _local_host: str
    _local_port: int
    _local_headless: bool
    _local_chrome_path: str | None
    _local_ready_timeout_s: float
    _local_shutdown_on_close: bool
    _sea_server: SeaServerManager | None
    ### </END CUSTOM CODE>

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    def __init__(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] = "remote",
        _local_stagehand_binary_path: str | os.PathLike[str] | None = None,
        local_host: str = "127.0.0.1",
        local_port: int = 0,
        local_headless: bool = True,
        local_chrome_path: str | None = None,
        local_ready_timeout_s: float = 10.0,
        local_shutdown_on_close: bool = True,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncStagehand client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `browserbase_api_key` from `BROWSERBASE_API_KEY`
        - `browserbase_project_id` from `BROWSERBASE_PROJECT_ID`

        `model_api_key` is intentionally not inferred from any AI provider environment variable.
        Pass it explicitly when you want the SDK to send `x-model-api-key` on remote requests or
        to forward `MODEL_API_KEY` to the local SEA child process.
        """
        if browserbase_api_key is None:
            browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
        if browserbase_project_id is None:
            browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")

        self.browserbase_api_key = browserbase_api_key
        self.browserbase_project_id = browserbase_project_id

        self.model_api_key = model_api_key

        # Centralize local-mode state hydration and base-url selection in `_custom`
        # so no constructor branching lives in the generated client.
        base_url = configure_client_base_url(
            self,
            server=server,
            _local_stagehand_binary_path=_local_stagehand_binary_path,
            local_host=local_host,
            local_port=local_port,
            local_headless=local_headless,
            local_chrome_path=local_chrome_path,
            local_ready_timeout_s=local_ready_timeout_s,
            local_shutdown_on_close=local_shutdown_on_close,
            base_url=base_url,
            model_api_key=model_api_key,
        )
    ### </END CUSTOM CODE>

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._default_stream_cls = AsyncStream

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    @override
    async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        # Start the local SEA server lazily on first request instead of at client
        # construction time, then swap the base URL to the started process.
        local_base_url = await prepare_async_client_base_url(self)
        if local_base_url is not None:
            self.base_url = local_base_url
        return await super()._prepare_options(options)

    @override
    async def close(self) -> None:
        try:
            await super().close()
        finally:
            # Tear down the managed SEA process after HTTP resources close.
            await close_async_client_sea_server(self)
    ### </END CUSTOM CODE>

    @cached_property
    def sessions(self) -> AsyncSessionsResource:
        from .resources.sessions import AsyncSessionsResource

        return AsyncSessionsResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncStagehandWithRawResponse:
        return AsyncStagehandWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStagehandWithStreamedResponse:
        return AsyncStagehandWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        return {**self._bb_api_key_auth, **self._bb_project_id_auth, **self._llm_model_api_key_auth}

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    @property
    def _bb_api_key_auth(self) -> dict[str, str]:
        browserbase_api_key = self.browserbase_api_key
        return {"x-bb-api-key": browserbase_api_key} if browserbase_api_key else {}

    @property
    def _bb_project_id_auth(self) -> dict[str, str]:
        browserbase_project_id = self.browserbase_project_id
        return {"x-bb-project-id": browserbase_project_id} if browserbase_project_id else {}

    @property
    def _llm_model_api_key_auth(self) -> dict[str, str]:
        model_api_key = self.model_api_key
        return {"x-model-api-key": model_api_key} if model_api_key else {}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "x-language": "python",
            "x-sdk-version": __version__,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }
    ### </END CUSTOM CODE>

    ### <CUSTOM CODE HANDWRITTEN BY STAGEHAND TEAM (not codegen)>
    def copy(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] | None = None,
        _local_stagehand_binary_path: str | os.PathLike[str] | None = None,
        local_host: str | None = None,
        local_port: int | None = None,
        local_headless: bool | None = None,
        local_chrome_path: str | None = None,
        local_ready_timeout_s: float | None = None,
        local_shutdown_on_close: bool | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            browserbase_api_key=browserbase_api_key or self.browserbase_api_key,
            browserbase_project_id=browserbase_project_id or self.browserbase_project_id,
            model_api_key=model_api_key or self.model_api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            # Preserve local-mode configuration when cloning the client without
            # duplicating that branching logic in generated code.
            **copy_local_mode_kwargs(
                self,
                server=server,
                _local_stagehand_binary_path=_local_stagehand_binary_path,
                local_host=local_host,
                local_port=local_port,
                local_headless=local_headless,
                local_chrome_path=local_chrome_path,
                local_ready_timeout_s=local_ready_timeout_s,
                local_shutdown_on_close=local_shutdown_on_close,
            ),
            **_extra_kwargs,
        )
    ### </END CUSTOM CODE>

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class StagehandWithRawResponse:
    _client: Stagehand

    def __init__(self, client: Stagehand) -> None:
        self._client = client

    @cached_property
    def sessions(self) -> sessions.SessionsResourceWithRawResponse:
        from .resources.sessions import SessionsResourceWithRawResponse

        return SessionsResourceWithRawResponse(self._client.sessions)


class AsyncStagehandWithRawResponse:
    _client: AsyncStagehand

    def __init__(self, client: AsyncStagehand) -> None:
        self._client = client

    @cached_property
    def sessions(self) -> sessions.AsyncSessionsResourceWithRawResponse:
        from .resources.sessions import AsyncSessionsResourceWithRawResponse

        return AsyncSessionsResourceWithRawResponse(self._client.sessions)


class StagehandWithStreamedResponse:
    _client: Stagehand

    def __init__(self, client: Stagehand) -> None:
        self._client = client

    @cached_property
    def sessions(self) -> sessions.SessionsResourceWithStreamingResponse:
        from .resources.sessions import SessionsResourceWithStreamingResponse

        return SessionsResourceWithStreamingResponse(self._client.sessions)


class AsyncStagehandWithStreamedResponse:
    _client: AsyncStagehand

    def __init__(self, client: AsyncStagehand) -> None:
        self._client = client

    @cached_property
    def sessions(self) -> sessions.AsyncSessionsResourceWithStreamingResponse:
        from .resources.sessions import AsyncSessionsResourceWithStreamingResponse

        return AsyncSessionsResourceWithStreamingResponse(self._client.sessions)


Client = Stagehand

AsyncClient = AsyncStagehand
