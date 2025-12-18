# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["ActionParam"]


class ActionParam(TypedDict, total=False):
    """Action object returned by observe and used by act"""

    description: Required[str]
    """Human-readable description of the action"""

    selector: Required[str]
    """CSS selector or XPath for the element"""

    arguments: SequenceNotStr[str]
    """Arguments to pass to the method"""

    method: str
    """The method to execute (click, fill, etc.)"""
