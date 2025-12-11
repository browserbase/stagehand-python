# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = ["SessionExtractParams", "Options"]


class SessionExtractParams(TypedDict, total=False):
    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Frame ID to extract from"""

    instruction: str
    """Natural language instruction for extraction"""

    options: Options

    schema: Dict[str, object]
    """JSON Schema for structured output"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]


class Options(TypedDict, total=False):
    model: ModelConfigParam

    selector: str
    """Extract only from elements matching this selector"""

    timeout: int
