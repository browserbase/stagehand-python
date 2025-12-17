# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .action import Action
from .._models import BaseModel

__all__ = ["SessionActResponse", "Data", "DataResult"]


class DataResult(BaseModel):
    action_description: str = FieldInfo(alias="actionDescription")
    """Description of the action that was performed"""

    actions: List[Action]
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

    success: Literal[True]
