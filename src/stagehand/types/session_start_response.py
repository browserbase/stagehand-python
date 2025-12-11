# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionStartResponse"]


class SessionStartResponse(BaseModel):
    available: bool
    """Whether the session is ready to use"""

    session_id: str = FieldInfo(alias="sessionId")
    """Unique identifier for the session"""
