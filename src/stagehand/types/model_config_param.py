# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "ModelConfigParam",
    "ProviderOptions",
    "ProviderOptionsBedrockAPIKeyProviderOptions",
    "ProviderOptionsBedrockAwsCredentialsProviderOptions",
    "ProviderOptionsGoogleVertexProviderOptions",
    "ProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptions",
    "ProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptionsCredentials",
]


class ProviderOptionsBedrockAPIKeyProviderOptions(TypedDict, total=False):
    region: Required[str]
    """AWS region for Amazon Bedrock"""


class ProviderOptionsBedrockAwsCredentialsProviderOptions(TypedDict, total=False):
    access_key_id: Required[Annotated[str, PropertyInfo(alias="accessKeyId")]]
    """AWS access key ID for Bedrock"""

    region: Required[str]
    """AWS region for Amazon Bedrock"""

    secret_access_key: Required[Annotated[str, PropertyInfo(alias="secretAccessKey")]]
    """AWS secret access key for Bedrock"""

    session_token: Annotated[str, PropertyInfo(alias="sessionToken")]
    """Optional AWS session token for temporary credentials"""


class ProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptionsCredentials(TypedDict, total=False):
    auth_provider_x509_cert_url: str

    auth_uri: str

    client_email: str

    client_id: str

    client_x509_cert_url: str

    private_key: str

    private_key_id: str

    project_id: str

    token_uri: str

    type: str

    universe_domain: str


class ProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptions(TypedDict, total=False):
    """Optional Google auth options for Vertex AI"""

    credentials: ProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptionsCredentials


class ProviderOptionsGoogleVertexProviderOptions(TypedDict, total=False):
    google_auth_options: Annotated[
        ProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptions, PropertyInfo(alias="googleAuthOptions")
    ]
    """Optional Google auth options for Vertex AI"""

    headers: Dict[str, str]
    """Custom headers for Vertex AI requests"""

    location: str
    """Google Cloud location for Vertex AI"""

    project: str
    """Google Cloud project ID for Vertex AI"""


ProviderOptions: TypeAlias = Union[
    ProviderOptionsBedrockAPIKeyProviderOptions,
    ProviderOptionsBedrockAwsCredentialsProviderOptions,
    ProviderOptionsGoogleVertexProviderOptions,
]


class ModelConfigParam(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers for the model provider"""

    provider: Literal["openai", "anthropic", "google", "microsoft", "bedrock"]
    """AI provider for the model (or provide a baseURL endpoint instead)"""

    provider_options: Annotated[ProviderOptions, PropertyInfo(alias="providerOptions")]
    """Provider-specific options passed through to the AI SDK provider constructor.

    For Bedrock: { region, accessKeyId, secretAccessKey, sessionToken }. For Vertex:
    { project, location, googleAuthOptions }.
    """

    skip_api_key_fallback: Annotated[bool, PropertyInfo(alias="skipApiKeyFallback")]
    """When true, hosted sessions will not copy x-model-api-key into model.apiKey.

    Use this when auth is carried through providerOptions instead of an API key.
    """
