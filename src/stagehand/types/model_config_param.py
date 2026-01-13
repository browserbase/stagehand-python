# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["ModelConfigParam", "ModelConfigObject"]


class ModelConfigObject(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string (e.g., 'openai/gpt-5-nano', 'anthropic/claude-4.5-opus')"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    provider: Literal["openai", "anthropic", "google", "microsoft"]
    """AI provider for the model (or provide a baseURL endpoint instead)"""


ModelConfigParam: TypeAlias = Union[str, ModelConfigObject]
