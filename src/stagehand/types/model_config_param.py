# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ModelConfigParam"]


class ModelConfigParam(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    access_key_id: Annotated[str, PropertyInfo(alias="accessKeyId")]
    """AWS access key ID for Bedrock"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: dict[str, str]
    """Additional headers for the model provider"""

    provider: Literal["openai", "anthropic", "google", "microsoft", "bedrock"]
    """AI provider for the model (or provide a baseURL endpoint instead)"""

    region: str
    """AWS region for Bedrock"""

    secret_access_key: Annotated[str, PropertyInfo(alias="secretAccessKey")]
    """AWS secret access key for Bedrock"""

    session_token: Annotated[str, PropertyInfo(alias="sessionToken")]
    """AWS session token for Bedrock"""
