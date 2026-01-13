# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionStartResponse", "Data"]


class Data(BaseModel):
    available: bool

    session_id: str = FieldInfo(alias="sessionId")
    """Unique Browserbase session identifier"""

    cdp_url: Optional[str] = FieldInfo(alias="cdpUrl", default=None)
    """
    CDP WebSocket URL for connecting to the Browserbase cloud browser (present when
    available)
    """


class SessionStartResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
