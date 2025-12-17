# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .action import Action
from .._models import BaseModel

__all__ = ["SessionObserveResponse", "Data"]


class Data(BaseModel):
    result: List[Action]

    action_id: Optional[str] = FieldInfo(alias="actionId", default=None)
    """Action ID for tracking"""


class SessionObserveResponse(BaseModel):
    data: Data

    success: Literal[True]
