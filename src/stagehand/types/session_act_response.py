# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .action import Action
from .._models import BaseModel

__all__ = ["SessionActResponse"]


class SessionActResponse(BaseModel):
    actions: List[Action]
    """Actions that were executed"""

    message: str
    """Result message"""

    success: bool
    """Whether the action succeeded"""
