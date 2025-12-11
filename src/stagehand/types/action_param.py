# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["ActionParam"]


class ActionParam(TypedDict, total=False):
    arguments: Required[SequenceNotStr[str]]
    """Arguments for the method"""

    description: Required[str]
    """Human-readable description of the action"""

    method: Required[str]
    """Method to execute (e.g., "click", "fill")"""

    selector: Required[str]
    """CSS or XPath selector for the element"""

    backend_node_id: Annotated[int, PropertyInfo(alias="backendNodeId")]
    """CDP backend node ID"""
