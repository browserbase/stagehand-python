# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionObserveParams"]


class SessionObserveParams(TypedDict, total=False):
    body: object

    x_language: Annotated[object, PropertyInfo(alias="x-language")]

    x_sdk_version: Annotated[object, PropertyInfo(alias="x-sdk-version")]

    x_sent_at: Annotated[object, PropertyInfo(alias="x-sent-at")]

    x_stream_response: Annotated[object, PropertyInfo(alias="x-stream-response")]
