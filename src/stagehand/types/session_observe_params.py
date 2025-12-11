# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = ["SessionObserveParams", "Options"]


class SessionObserveParams(TypedDict, total=False):
    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Frame ID to observe"""

    instruction: str
    """Natural language instruction to filter actions"""

    options: Options

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]


class Options(TypedDict, total=False):
    model: ModelConfigParam

    selector: str
    """Observe only elements matching this selector"""

    timeout: int
