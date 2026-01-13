# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionActResponse", "Data", "DataResult", "DataResultAction"]


class DataResultAction(BaseModel):
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


class DataResult(BaseModel):
    action_description: str = FieldInfo(alias="actionDescription")
    """Description of the action that was performed"""

    actions: List[DataResultAction]
    """List of actions that were executed"""

    message: str
    """Human-readable result message"""

    success: bool
    """Whether the action completed successfully"""


class Data(BaseModel):
    result: DataResult

    action_id: Optional[str] = FieldInfo(alias="actionId", default=None)
    """Action ID for tracking"""


class SessionActResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
