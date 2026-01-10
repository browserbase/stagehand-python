# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = ["SessionObserveParamsBase", "Options", "SessionObserveParamsNonStreaming", "SessionObserveParamsStreaming"]


class SessionObserveParamsBase(TypedDict, total=False):
    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Target frame ID for the observation"""

    instruction: str
    """Natural language instruction for what actions to find"""

    options: Options

    x_sent_at: Annotated[Union[str, datetime], PropertyInfo(alias="x-sent-at", format="iso8601")]
    """ISO timestamp when request was sent"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


class Options(TypedDict, total=False):
    model: ModelConfigParam
    """
    Model name string with provider prefix (e.g., 'openai/gpt-5-nano',
    'anthropic/claude-4.5-opus')
    """

    selector: str
    """CSS selector to scope observation to a specific element"""

    timeout: float
    """Timeout in ms for the observation"""


class SessionObserveParamsNonStreaming(SessionObserveParamsBase, total=False):
    stream_response: Annotated[Literal[False], PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""


class SessionObserveParamsStreaming(SessionObserveParamsBase):
    stream_response: Required[Annotated[Literal[True], PropertyInfo(alias="streamResponse")]]
    """Whether to stream the response via SSE"""


SessionObserveParams = Union[SessionObserveParamsNonStreaming, SessionObserveParamsStreaming]
