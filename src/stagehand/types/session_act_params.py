# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = ["SessionActParams", "Input", "InputActionInput", "Options"]


class SessionActParams(TypedDict, total=False):
    input: Required[Input]
    """Natural language instruction or Action object"""

    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Target frame ID for the action"""

    options: Options

    x_language: Annotated[Literal["typescript", "python", "playground"], PropertyInfo(alias="x-language")]
    """Client SDK language"""

    x_sdk_version: Annotated[str, PropertyInfo(alias="x-sdk-version")]
    """Version of the Stagehand SDK"""

    x_sent_at: Annotated[Union[str, datetime], PropertyInfo(alias="x-sent-at", format="iso8601")]
    """ISO timestamp when request was sent"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


class InputActionInput(TypedDict, total=False):
    """Action object returned by observe and used by act"""

    description: Required[str]
    """Human-readable description of the action"""

    selector: Required[str]
    """CSS selector or XPath for the element"""

    arguments: SequenceNotStr[str]
    """Arguments to pass to the method"""

    method: str
    """The method to execute (click, fill, etc.)"""


Input: TypeAlias = Union[str, InputActionInput]


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
