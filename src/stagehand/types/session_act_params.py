# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .action_param import ActionParam
from .model_config_param import ModelConfigParam

__all__ = ["SessionActParamsBase", "Input", "Options", "SessionActParamsNonStreaming", "SessionActParamsStreaming"]


class SessionActParamsBase(TypedDict, total=False):
    input: Required[Input]
    """Natural language instruction or Action object"""

    frame_id: Annotated[Optional[str], PropertyInfo(alias="frameId")]
    """Target frame ID for the action"""

    options: Options

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


Input: TypeAlias = Union[str, ActionParam]


class Options(TypedDict, total=False):
    model: ModelConfigParam
    """Model name string with provider prefix.

    Always use the format 'provider/model-name' (e.g., 'openai/gpt-4o',
    'anthropic/claude-sonnet-4-5-20250929', 'google/gemini-2.0-flash')
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
