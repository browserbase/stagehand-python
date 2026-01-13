# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["SessionEndResponse"]


class SessionEndResponse(BaseModel):
    success: bool
    """Indicates whether the request was successful"""
