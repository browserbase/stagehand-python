# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionStartResponse", "Data"]


class Data(BaseModel):
    available: bool

    connect_url: str = FieldInfo(alias="connectUrl")
    """CDP WebSocket URL for connecting to the Browserbase cloud browser"""

    session_id: str = FieldInfo(alias="sessionId")
    """Unique Browserbase session identifier"""


class SessionStartResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
