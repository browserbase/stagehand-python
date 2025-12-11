# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionNavigateParams", "Options"]


class SessionNavigateParams(TypedDict, total=False):
    url: Required[str]
    """URL to navigate to"""

    frame_id: Annotated[str, PropertyInfo(alias="frameId")]

    options: Options

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]


class Options(TypedDict, total=False):
    wait_until: Annotated[Literal["load", "domcontentloaded", "networkidle"], PropertyInfo(alias="waitUntil")]
    """When to consider navigation complete"""
