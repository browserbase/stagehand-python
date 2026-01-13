# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import datetime
from typing import TYPE_CHECKING, Any, Mapping
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
from ._exceptions import APIStatusError, StagehandError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .lib.sea_server import SeaServerConfig, SeaServerManager

if TYPE_CHECKING:
    from .resources import sessions
    from .resources.sessions_helpers import SessionsResourceWithHelpers, AsyncSessionsResourceWithHelpers

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


class Stagehand(SyncAPIClient):
    # client options
    browserbase_api_key: str
    browserbase_project_id: str
    model_api_key: str

    def __init__(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] = "remote",
        local_binary_path: str | os.PathLike[str] | None = None,
        local_host: str = "127.0.0.1",
        local_port: int = 0,
        local_headless: bool = True,
        local_ready_timeout_s: float = 10.0,
        local_openai_api_key: str | None = None,
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
        - `model_api_key` from `MODEL_API_KEY`
        """
        self._server_mode: Literal["remote", "local"] = server
        self._local_binary_path = local_binary_path
        self._local_host = local_host
        self._local_port = local_port
        self._local_headless = local_headless
        self._local_ready_timeout_s = local_ready_timeout_s
        self._local_openai_api_key = local_openai_api_key
        self._local_shutdown_on_close = local_shutdown_on_close

        if browserbase_api_key is None:
            browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
        if browserbase_project_id is None:
            browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")

        self.browserbase_api_key = browserbase_api_key
        self.browserbase_project_id = browserbase_project_id

        if model_api_key is None:
            model_api_key = os.environ.get("MODEL_API_KEY")
        if model_api_key is None:
            raise StagehandError(
                "The model_api_key client option must be set either by passing model_api_key to the client or by setting the MODEL_API_KEY environment variable"
            )
        self.model_api_key = model_api_key

        self._sea_server: SeaServerManager | None = None
        if server == "local":
            # We'll switch `base_url` to the started server before the first request.
            if base_url is None:
                base_url = "http://127.0.0.1"

            openai_api_key = local_openai_api_key or os.environ.get("OPENAI_API_KEY") or model_api_key
            self._sea_server = SeaServerManager(
                config=SeaServerConfig(
                    host=local_host,
                    port=local_port,
                    headless=local_headless,
                    ready_timeout_s=local_ready_timeout_s,
                    openai_api_key=openai_api_key,
                    shutdown_on_close=local_shutdown_on_close,
                ),
                local_binary_path=local_binary_path,
            )
        else:
            if base_url is None:
                base_url = os.environ.get("STAGEHAND_BASE_URL")
            if base_url is None:
                base_url = f"https://api.stagehand.browserbase.com"

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

    @override
    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if self._sea_server is not None:
            self.base_url = self._sea_server.ensure_running_sync()
        return super()._prepare_options(options)

    @override
    def close(self) -> None:
        try:
            super().close()
        finally:
            if self._sea_server is not None:
                self._sea_server.close()

    @cached_property
    def sessions(self) -> SessionsResourceWithHelpers:
        from .resources.sessions_helpers import SessionsResourceWithHelpers

        return SessionsResourceWithHelpers(self)

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
        return {"x-model-api-key": model_api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "x-language": "python",
            "x-sdk-version": __version__,
            "x-sent-at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] | None = None,
        local_binary_path: str | os.PathLike[str] | None = None,
        local_host: str | None = None,
        local_port: int | None = None,
        local_headless: bool | None = None,
        local_ready_timeout_s: float | None = None,
        local_openai_api_key: str | None = None,
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
            server=server or self._server_mode,
            local_binary_path=local_binary_path if local_binary_path is not None else self._local_binary_path,
            local_host=local_host or self._local_host,
            local_port=local_port if local_port is not None else self._local_port,
            local_headless=local_headless if local_headless is not None else self._local_headless,
            local_ready_timeout_s=local_ready_timeout_s
            if local_ready_timeout_s is not None
            else self._local_ready_timeout_s,
            local_openai_api_key=local_openai_api_key
            if local_openai_api_key is not None
            else self._local_openai_api_key,
            local_shutdown_on_close=local_shutdown_on_close
            if local_shutdown_on_close is not None
            else self._local_shutdown_on_close,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

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
    # client options
    browserbase_api_key: str
    browserbase_project_id: str
    model_api_key: str

    def __init__(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] = "remote",
        local_binary_path: str | os.PathLike[str] | None = None,
        local_host: str = "127.0.0.1",
        local_port: int = 0,
        local_headless: bool = True,
        local_ready_timeout_s: float = 10.0,
        local_openai_api_key: str | None = None,
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
        - `model_api_key` from `MODEL_API_KEY`
        """
        self._server_mode: Literal["remote", "local"] = server
        self._local_binary_path = local_binary_path
        self._local_host = local_host
        self._local_port = local_port
        self._local_headless = local_headless
        self._local_ready_timeout_s = local_ready_timeout_s
        self._local_openai_api_key = local_openai_api_key
        self._local_shutdown_on_close = local_shutdown_on_close

        if browserbase_api_key is None:
            browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
        if browserbase_project_id is None:
            browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")

        self.browserbase_api_key = browserbase_api_key
        self.browserbase_project_id = browserbase_project_id

        if model_api_key is None:
            model_api_key = os.environ.get("MODEL_API_KEY")
        if model_api_key is None:
            raise StagehandError(
                "The model_api_key client option must be set either by passing model_api_key to the client or by setting the MODEL_API_KEY environment variable"
            )
        self.model_api_key = model_api_key

        self._sea_server: SeaServerManager | None = None
        if server == "local":
            if base_url is None:
                base_url = "http://127.0.0.1"

            openai_api_key = local_openai_api_key or os.environ.get("OPENAI_API_KEY") or model_api_key
            self._sea_server = SeaServerManager(
                config=SeaServerConfig(
                    host=local_host,
                    port=local_port,
                    headless=local_headless,
                    ready_timeout_s=local_ready_timeout_s,
                    openai_api_key=openai_api_key,
                    shutdown_on_close=local_shutdown_on_close,
                ),
                local_binary_path=local_binary_path,
            )
        else:
            if base_url is None:
                base_url = os.environ.get("STAGEHAND_BASE_URL")
            if base_url is None:
                base_url = f"https://api.stagehand.browserbase.com"

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

    @override
    async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        if self._sea_server is not None:
            self.base_url = await self._sea_server.ensure_running_async()
        return await super()._prepare_options(options)

    @override
    async def close(self) -> None:
        try:
            await super().close()
        finally:
            if self._sea_server is not None:
                await self._sea_server.aclose()

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithHelpers:
        from .resources.sessions_helpers import AsyncSessionsResourceWithHelpers

        return AsyncSessionsResourceWithHelpers(self)

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
        return {"x-model-api-key": model_api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "x-language": "python",
            "x-sdk-version": __version__,
            "x-sent-at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
        server: Literal["remote", "local"] | None = None,
        local_binary_path: str | os.PathLike[str] | None = None,
        local_host: str | None = None,
        local_port: int | None = None,
        local_headless: bool | None = None,
        local_ready_timeout_s: float | None = None,
        local_openai_api_key: str | None = None,
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
            server=server or self._server_mode,
            local_binary_path=local_binary_path if local_binary_path is not None else self._local_binary_path,
            local_host=local_host or self._local_host,
            local_port=local_port if local_port is not None else self._local_port,
            local_headless=local_headless if local_headless is not None else self._local_headless,
            local_ready_timeout_s=local_ready_timeout_s
            if local_ready_timeout_s is not None
            else self._local_ready_timeout_s,
            local_openai_api_key=local_openai_api_key
            if local_openai_api_key is not None
            else self._local_openai_api_key,
            local_shutdown_on_close=local_shutdown_on_close
            if local_shutdown_on_close is not None
            else self._local_shutdown_on_close,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

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
