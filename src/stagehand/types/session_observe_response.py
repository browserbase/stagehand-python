# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionObserveResponse", "Data", "DataResult"]


class DataResult(BaseModel):
    """Action object returned by observe and used by act"""

    description: str
    """Human-readable description of the action"""

    selector: str
    """CSS selector or XPath for the element"""

    arguments: Optional[List[str]] = None
    """Arguments to pass to the method"""

    backend_node_id: Optional[float] = FieldInfo(alias="backendNodeId", default=None)
    """Backend node ID for the element"""

    method: Optional[str] = None
    """The method to execute (click, fill, etc.)"""


class Data(BaseModel):
    result: List[DataResult]

    action_id: Optional[str] = FieldInfo(alias="actionId", default=None)
    """Action ID for tracking"""


class SessionObserveResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
