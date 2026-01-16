# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionEndParams"]


class SessionEndParams(TypedDict, total=False):
    _force_body: Annotated[object, PropertyInfo(alias="_forceBody")]

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""
