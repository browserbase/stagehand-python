# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionNavigateParams", "Options"]


class SessionNavigateParams(TypedDict, total=False):
    url: Required[str]
    """URL to navigate to"""

    frame_id: Annotated[Optional[str], PropertyInfo(alias="frameId")]
    """Target frame ID for the navigation"""

    options: Options

    stream_response: Annotated[bool, PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


class Options(TypedDict, total=False):
    referer: str
    """Referer header to send with the request"""

    timeout: float
    """Timeout in ms for the navigation"""

    wait_until: Annotated[Literal["load", "domcontentloaded", "networkidle"], PropertyInfo(alias="waitUntil")]
    """When to consider navigation complete"""
