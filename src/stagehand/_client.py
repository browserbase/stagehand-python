# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping
from typing_extensions import Self, override

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
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, StagehandError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import sessions
    from .resources.sessions import SessionsResource, AsyncSessionsResource

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
        if browserbase_api_key is None:
            browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
        if browserbase_api_key is None:
            raise StagehandError(
                "The browserbase_api_key client option must be set either by passing browserbase_api_key to the client or by setting the BROWSERBASE_API_KEY environment variable"
            )
        self.browserbase_api_key = browserbase_api_key

        if browserbase_project_id is None:
            browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
        if browserbase_project_id is None:
            raise StagehandError(
                "The browserbase_project_id client option must be set either by passing browserbase_project_id to the client or by setting the BROWSERBASE_PROJECT_ID environment variable"
            )
        self.browserbase_project_id = browserbase_project_id

        if model_api_key is None:
            model_api_key = os.environ.get("MODEL_API_KEY")
        if model_api_key is None:
            raise StagehandError(
                "The model_api_key client option must be set either by passing model_api_key to the client or by setting the MODEL_API_KEY environment variable"
            )
        self.model_api_key = model_api_key

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

    @property
    def _bb_api_key_auth(self) -> dict[str, str]:
        browserbase_api_key = self.browserbase_api_key
        return {"x-bb-api-key": browserbase_api_key}

    @property
    def _bb_project_id_auth(self) -> dict[str, str]:
        browserbase_project_id = self.browserbase_project_id
        return {"x-bb-project-id": browserbase_project_id}

    @property
    def _llm_model_api_key_auth(self) -> dict[str, str]:
        model_api_key = self.model_api_key
        return {"x-model-api-key": model_api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
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
        if browserbase_api_key is None:
            browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
        if browserbase_api_key is None:
            raise StagehandError(
                "The browserbase_api_key client option must be set either by passing browserbase_api_key to the client or by setting the BROWSERBASE_API_KEY environment variable"
            )
        self.browserbase_api_key = browserbase_api_key

        if browserbase_project_id is None:
            browserbase_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
        if browserbase_project_id is None:
            raise StagehandError(
                "The browserbase_project_id client option must be set either by passing browserbase_project_id to the client or by setting the BROWSERBASE_PROJECT_ID environment variable"
            )
        self.browserbase_project_id = browserbase_project_id

        if model_api_key is None:
            model_api_key = os.environ.get("MODEL_API_KEY")
        if model_api_key is None:
            raise StagehandError(
                "The model_api_key client option must be set either by passing model_api_key to the client or by setting the MODEL_API_KEY environment variable"
            )
        self.model_api_key = model_api_key

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

    @property
    def _bb_api_key_auth(self) -> dict[str, str]:
        browserbase_api_key = self.browserbase_api_key
        return {"x-bb-api-key": browserbase_api_key}

    @property
    def _bb_project_id_auth(self) -> dict[str, str]:
        browserbase_project_id = self.browserbase_project_id
        return {"x-bb-project-id": browserbase_project_id}

    @property
    def _llm_model_api_key_auth(self) -> dict[str, str]:
        model_api_key = self.model_api_key
        return {"x-model-api-key": model_api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        browserbase_api_key: str | None = None,
        browserbase_project_id: str | None = None,
        model_api_key: str | None = None,
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
