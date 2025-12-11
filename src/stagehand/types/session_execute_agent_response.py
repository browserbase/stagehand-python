# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["SessionExecuteAgentResponse"]


class SessionExecuteAgentResponse(BaseModel):
    message: Optional[str] = None
    """Final message from the agent"""

    steps: Optional[List[object]] = None
    """Steps taken by the agent"""
