# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionStartResponse", "Data"]


class Data(BaseModel):
    available: bool

    session_id: str = FieldInfo(alias="sessionId")
    """Unique session identifier"""


class SessionStartResponse(BaseModel):
    data: Data

    success: Literal[True]
