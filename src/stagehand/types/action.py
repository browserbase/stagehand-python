# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Action"]


class Action(BaseModel):
    arguments: List[str]
    """Arguments for the method"""

    description: str
    """Human-readable description of the action"""

    method: str
    """Method to execute (e.g., "click", "fill")"""

    selector: str
    """CSS or XPath selector for the element"""

    backend_node_id: Optional[int] = FieldInfo(alias="backendNodeId", default=None)
    """CDP backend node ID"""
