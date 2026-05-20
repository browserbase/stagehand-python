# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["ModelConfigParam", "GoogleAuthOptions", "GoogleAuthOptionsCredentials"]


class GoogleAuthOptionsCredentials(TypedDict, total=False):
    """Google Cloud service account credentials"""

    client_email: Required[str]

    private_key: Required[str]

    auth_provider_x509_cert_url: str

    auth_uri: str

    client_id: str

    client_x509_cert_url: str

    private_key_id: str

    project_id: str

    token_uri: str

    type: Literal["service_account"]

    universe_domain: str


class GoogleAuthOptions(TypedDict, total=False):
    """google-auth-library options used to authenticate Vertex AI models"""

    credentials: GoogleAuthOptionsCredentials
    """Google Cloud service account credentials"""

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Google Cloud project ID used by google-auth-library"""

    scopes: Union[str, SequenceNotStr[str]]
    """Google auth scopes for the desired API request"""

    universe_domain: Annotated[str, PropertyInfo(alias="universeDomain")]
    """Google Cloud universe domain"""


class ModelConfigParam(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    google_auth_options: Annotated[GoogleAuthOptions, PropertyInfo(alias="googleAuthOptions")]
    """google-auth-library options used to authenticate Vertex AI models"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""

    location: str
    """Google Cloud location for Vertex AI models"""

    project: str
    """Google Cloud project ID for Vertex AI models"""

    provider: Literal["openai", "anthropic", "google", "microsoft", "bedrock", "vertex"]
    """AI provider for the model (or provide a baseURL endpoint instead)"""
