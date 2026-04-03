# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = [
    "SessionObserveParamsBase",
    "Options",
    "OptionsVariables",
    "OptionsVariablesUnionMember3",
    "SessionObserveParamsNonStreaming",
    "SessionObserveParamsStreaming",
]


class SessionObserveParamsBase(TypedDict, total=False):
    frame_id: Annotated[Optional[str], PropertyInfo(alias="frameId")]
    """Target frame ID for the observation"""

    instruction: str
    """Natural language instruction for what actions to find"""

    options: Options

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""

class OptionsVariablesUnionMember3(TypedDict, total=False):
    value: Required[Union[str, float, bool]]

    description: str


OptionsVariables: TypeAlias = Union[str, float, bool, OptionsVariablesUnionMember3]


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

    variables: Dict[str, OptionsVariables]
    """
    Variables whose names are exposed to the model so observe() returns
    %variableName% placeholders in suggested action arguments instead of literal
    values. Accepts flat primitives or { value, description? } objects.
    """


class SessionObserveParamsNonStreaming(SessionObserveParamsBase, total=False):
    stream_response: Annotated[Literal[False], PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""


class SessionObserveParamsStreaming(SessionObserveParamsBase):
    stream_response: Required[Annotated[Literal[True], PropertyInfo(alias="streamResponse")]]
    """Whether to stream the response via SSE"""


SessionObserveParams = Union[SessionObserveParamsNonStreaming, SessionObserveParamsStreaming]
