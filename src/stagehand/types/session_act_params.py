# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .action_param import ActionParam
from .model_config_param import ModelConfigParam

__all__ = ["SessionActParamsBase", "Input", "Options", "SessionActParamsNonStreaming", "SessionActParamsStreaming"]


class SessionActParamsBase(TypedDict, total=False):
    input: Required[Input]
    """Natural language instruction or Action object"""

    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Target frame ID for the action"""

    options: Options

    x_sent_at: Annotated[Union[str, datetime], PropertyInfo(alias="x-sent-at", format="iso8601")]
    """ISO timestamp when request was sent"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


Input: TypeAlias = Union[str, ActionParam]


class Options(TypedDict, total=False):
    model: ModelConfigParam
    """
    Model name string with provider prefix (e.g., 'openai/gpt-5-nano',
    'anthropic/claude-4.5-opus')
    """

    timeout: float
    """Timeout in ms for the action"""

    variables: Dict[str, str]
    """Variables to substitute in the action instruction"""


class SessionActParamsNonStreaming(SessionActParamsBase, total=False):
    stream_response: Annotated[Literal[False], PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""


class SessionActParamsStreaming(SessionActParamsBase):
    stream_response: Required[Annotated[Literal[True], PropertyInfo(alias="streamResponse")]]
    """Whether to stream the response via SSE"""


SessionActParams = Union[SessionActParamsNonStreaming, SessionActParamsStreaming]
