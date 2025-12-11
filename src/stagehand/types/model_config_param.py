# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ModelConfigParam"]


class ModelConfigParam(TypedDict, total=False):
    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Custom base URL for API"""

    model: str
    """Model name"""

    provider: Literal["openai", "anthropic", "google"]
