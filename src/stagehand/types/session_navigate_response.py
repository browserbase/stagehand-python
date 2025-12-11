# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SessionNavigateResponse"]


class SessionNavigateResponse(BaseModel):
    """Navigation response (may be null)"""

    ok: Optional[bool] = None

    status: Optional[int] = None

    url: Optional[str] = None
