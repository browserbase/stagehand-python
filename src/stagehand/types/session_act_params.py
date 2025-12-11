# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .action_param import ActionParam
from .model_config_param import ModelConfigParam

__all__ = ["SessionActParams", "Input", "Options"]


class SessionActParams(TypedDict, total=False):
    input: Required[Input]
    """Natural language instruction"""

    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Frame ID to act on (optional)"""

    options: Options

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]


Input: TypeAlias = Union[str, ActionParam]


class Options(TypedDict, total=False):
    model: ModelConfigParam

    timeout: int
    """Timeout in milliseconds"""

    variables: Dict[str, str]
    """Template variables for instruction"""
