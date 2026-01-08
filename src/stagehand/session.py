# Manually maintained helpers (not generated).

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Union
from datetime import datetime
from typing_extensions import Literal, overload

import httpx

from .types import (
    session_act_params,
    session_execute_params,
    session_extract_params,
    session_observe_params,
    session_navigate_params,
)
from ._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ._streaming import Stream, AsyncStream
from .types.stream_event import StreamEvent
from .types.session_act_response import SessionActResponse
from .types.session_end_response import SessionEndResponse
from .types.session_execute_response import SessionExecuteResponse
from .types.session_extract_response import SessionExtractResponse
from .types.session_observe_response import SessionObserveResponse
from .types.session_navigate_response import SessionNavigateResponse

if TYPE_CHECKING:
    from ._client import Stagehand, AsyncStagehand


class Session:
    """A Stagehand session bound to a specific `session_id`.

    This is a small DX helper so you don't need to pass `id=` into every call.
    """

    def __init__(self, client: Stagehand, id: str) -> None:
        self._client = client
        self.id = id

    @overload
    def act(
        self,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse: ...

    @overload
    def act(
        self,
        *,
        input: session_act_params.Input,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[StreamEvent]: ...

    @overload
    def act(
        self,
        *,
        input: session_act_params.Input,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | Stream[StreamEvent]: ...

    def act(
        self,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | Stream[StreamEvent]:
        return self._client.sessions.act(
            id=self.id,
            input=input,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    def navigate(
        self,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        stream_response: bool | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionNavigateResponse:
        return self._client.sessions.navigate(
            id=self.id,
            url=url,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    @overload
    def observe(
        self,
        *,
        instruction: str,
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse: ...

    @overload
    def observe(
        self,
        *,
        instruction: str,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[StreamEvent]: ...

    @overload
    def observe(
        self,
        *,
        instruction: str,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | Stream[StreamEvent]: ...

    def observe(
        self,
        *,
        instruction: str,
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | Stream[StreamEvent]:
        return self._client.sessions.observe(
            id=self.id,
            instruction=instruction,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    def extract(
        self,
        *,
        instruction: str,
        schema: Dict[str, object],
        frame_id: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        stream_response: bool | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse:
        return self._client.sessions.extract(
            id=self.id,
            instruction=instruction,
            schema=schema,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    @overload
    def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse: ...

    @overload
    def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Stream[StreamEvent]: ...

    @overload
    def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | Stream[StreamEvent]: ...

    def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | Stream[StreamEvent]:
        return self._client.sessions.execute(
            id=self.id,
            agent_config=agent_config,
            execute_options=execute_options,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    def end(
        self,
        *,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        return self._client.sessions.end(
            id=self.id,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )


class AsyncSession:
    """Async variant of `Session`."""

    def __init__(self, client: AsyncStagehand, id: str) -> None:
        self._client = client
        self.id = id

    @overload
    async def act(
        self,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse: ...

    @overload
    async def act(
        self,
        *,
        input: session_act_params.Input,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[StreamEvent]: ...

    @overload
    async def act(
        self,
        *,
        input: session_act_params.Input,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | AsyncStream[StreamEvent]: ...

    async def act(
        self,
        *,
        input: session_act_params.Input,
        frame_id: str | Omit = omit,
        options: session_act_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionActResponse | AsyncStream[StreamEvent]:
        return await self._client.sessions.act(
            id=self.id,
            input=input,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    async def navigate(
        self,
        *,
        url: str,
        frame_id: str | Omit = omit,
        options: session_navigate_params.Options | Omit = omit,
        stream_response: bool | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionNavigateResponse:
        return await self._client.sessions.navigate(
            id=self.id,
            url=url,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    @overload
    async def observe(
        self,
        *,
        instruction: str,
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse: ...

    @overload
    async def observe(
        self,
        *,
        instruction: str,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[StreamEvent]: ...

    @overload
    async def observe(
        self,
        *,
        instruction: str,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | AsyncStream[StreamEvent]: ...

    async def observe(
        self,
        *,
        instruction: str,
        frame_id: str | Omit = omit,
        options: session_observe_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionObserveResponse | AsyncStream[StreamEvent]:
        return await self._client.sessions.observe(
            id=self.id,
            instruction=instruction,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    async def extract(
        self,
        *,
        instruction: str,
        schema: Dict[str, object],
        frame_id: str | Omit = omit,
        options: session_extract_params.Options | Omit = omit,
        stream_response: bool | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExtractResponse:
        return await self._client.sessions.extract(
            id=self.id,
            instruction=instruction,
            schema=schema,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    @overload
    async def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        stream_response: Literal[False] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse: ...

    @overload
    async def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: Literal[True],
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncStream[StreamEvent]: ...

    @overload
    async def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        stream_response: bool,
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | AsyncStream[StreamEvent]: ...

    async def execute(
        self,
        *,
        agent_config: session_execute_params.AgentConfig,
        execute_options: session_execute_params.ExecuteOptions,
        frame_id: str | Omit = omit,
        options: session_execute_params.Options | Omit = omit,
        stream_response: Literal[False] | Literal[True] | Omit = omit,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionExecuteResponse | AsyncStream[StreamEvent]:
        return await self._client.sessions.execute(
            id=self.id,
            agent_config=agent_config,
            execute_options=execute_options,
            frame_id=frame_id,
            options=options,
            stream_response=stream_response,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

    async def end(
        self,
        *,
        x_language: Literal["typescript", "python", "playground"] | Omit = omit,
        x_sdk_version: str | Omit = omit,
        x_sent_at: Union[str, datetime] | Omit = omit,
        x_stream_response: Literal["true", "false"] | Omit = omit,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionEndResponse:
        return await self._client.sessions.end(
            id=self.id,
            x_language=x_language,
            x_sdk_version=x_sdk_version,
            x_sent_at=x_sent_at,
            x_stream_response=x_stream_response,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
