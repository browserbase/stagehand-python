# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionExtractResponse", "Data"]


class Data(BaseModel):
    result: object
    """Extracted data matching the requested schema"""

    action_id: Optional[str] = FieldInfo(alias="actionId", default=None)
    """Action ID for tracking"""


class SessionExtractResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
