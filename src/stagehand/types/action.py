# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["Action"]


class Action(BaseModel):
    """Action object returned by observe and used by act"""

    description: str
    """Human-readable description of the action"""

    selector: str
    """CSS selector or XPath for the element"""

    arguments: Optional[List[str]] = None
    """Arguments to pass to the method"""

    method: Optional[str] = None
    """The method to execute (click, fill, etc.)"""
