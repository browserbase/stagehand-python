# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionNavigateResponse", "Data"]


class Data(BaseModel):
    result: object
    """Navigation response (Playwright Response object or null)"""

    action_id: Optional[str] = FieldInfo(alias="actionId", default=None)
    """Action ID for tracking"""


class SessionNavigateResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
