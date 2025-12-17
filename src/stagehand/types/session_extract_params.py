# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = ["SessionExtractParams", "Options"]


class SessionExtractParams(TypedDict, total=False):
    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Target frame ID for the extraction"""

    instruction: str
    """Natural language instruction for what to extract"""

    options: Options

    schema: Dict[str, object]
    """JSON Schema defining the structure of data to extract"""

    x_language: Annotated[Literal["typescript", "python", "playground"], PropertyInfo(alias="x-language")]
    """Client SDK language"""

    x_sdk_version: Annotated[str, PropertyInfo(alias="x-sdk-version")]
    """Version of the Stagehand SDK"""

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
    """CSS selector to scope extraction to a specific element"""

    timeout: float
    """Timeout in ms for the extraction"""
