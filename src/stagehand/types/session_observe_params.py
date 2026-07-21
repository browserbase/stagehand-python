# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SessionObserveParamsBase",
    "Options",
    "OptionsModel",
    "OptionsModelVertexModelConfigObject",
    "OptionsModelVertexModelConfigObjectAuth",
    "OptionsModelVertexModelConfigObjectAuthCredentials",
    "OptionsModelVertexModelConfigObjectProviderOptions",
    "OptionsModelVertexModelConfigObjectProviderOptionsVertex",
    "OptionsModelAzureEntraModelConfigObject",
    "OptionsModelAzureEntraModelConfigObjectAuth",
    "OptionsModelAzureEntraModelConfigObjectProviderOptions",
    "OptionsModelAzureEntraModelConfigObjectProviderOptionsAzure",
    "OptionsModelAzureAPIKeyModelConfigObject",
    "OptionsModelAzureAPIKeyModelConfigObjectProviderOptions",
    "OptionsModelAzureAPIKeyModelConfigObjectProviderOptionsAzure",
    "OptionsModelGenericModelConfigObject",
    "OptionsVariables",
    "OptionsVariablesUnionMember3",
    "SessionObserveParamsNonStreaming",
    "SessionObserveParamsStreaming",
]


class SessionObserveParamsBase(TypedDict, total=False):
    frame_id: Annotated[Optional[str], PropertyInfo(alias="frameId")]
    """Target frame ID for the observation"""

    instruction: str
    """Natural language instruction for what actions to find"""

    options: Options

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


class OptionsModelVertexModelConfigObjectAuthCredentials(TypedDict, total=False):
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


class OptionsModelVertexModelConfigObjectAuth(TypedDict, total=False):
    """Vertex provider authentication configuration"""

    credentials: Required[OptionsModelVertexModelConfigObjectAuthCredentials]
    """Google Cloud service account credentials"""

    type: Required[Literal["googleServiceAccount"]]
    """Use inline Google Cloud service account credentials for provider authentication"""

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Google Cloud project ID used by google-auth-library"""

    scopes: Union[str, SequenceNotStr[str]]
    """Google auth scopes for the desired API request"""

    universe_domain: Annotated[str, PropertyInfo(alias="universeDomain")]
    """Google Cloud universe domain"""


class OptionsModelVertexModelConfigObjectProviderOptionsVertex(TypedDict, total=False):
    """Vertex AI provider-specific settings"""

    location: Required[str]
    """Google Cloud location for Vertex AI models"""

    project: Required[str]
    """Google Cloud project ID for Vertex AI models"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the Vertex AI provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the Vertex AI provider"""


class OptionsModelVertexModelConfigObjectProviderOptions(TypedDict, total=False):
    """Vertex provider-specific model configuration"""

    vertex: Required[OptionsModelVertexModelConfigObjectProviderOptionsVertex]
    """Vertex AI provider-specific settings"""


class OptionsModelVertexModelConfigObject(TypedDict, total=False):
    auth: Required[OptionsModelVertexModelConfigObjectAuth]
    """Vertex provider authentication configuration"""

    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["vertex"]]
    """Vertex AI model provider"""

    provider_options: Required[
        Annotated[OptionsModelVertexModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")]
    ]
    """Vertex provider-specific model configuration"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class OptionsModelAzureEntraModelConfigObjectAuth(TypedDict, total=False):
    """Azure provider authentication configuration"""

    token: Required[str]
    """Microsoft Entra ID bearer token for Azure OpenAI"""

    type: Required[Literal["azureEntraId"]]
    """Use a Microsoft Entra ID bearer token for authentication"""


class OptionsModelAzureEntraModelConfigObjectProviderOptionsAzure(TypedDict, total=False):
    """Azure OpenAI provider-specific settings"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """Azure OpenAI API version"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the Azure OpenAI provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the Azure OpenAI provider"""

    resource_name: Annotated[str, PropertyInfo(alias="resourceName")]
    """Azure OpenAI resource name"""

    use_deployment_based_urls: Annotated[bool, PropertyInfo(alias="useDeploymentBasedUrls")]
    """Whether to use deployment-based Azure OpenAI URLs"""


class OptionsModelAzureEntraModelConfigObjectProviderOptions(TypedDict, total=False):
    """Azure provider-specific model configuration"""

    azure: Required[OptionsModelAzureEntraModelConfigObjectProviderOptionsAzure]
    """Azure OpenAI provider-specific settings"""


class OptionsModelAzureEntraModelConfigObject(TypedDict, total=False):
    auth: Required[OptionsModelAzureEntraModelConfigObjectAuth]
    """Azure provider authentication configuration"""

    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["azure"]]
    """Azure OpenAI model provider"""

    provider_options: Required[
        Annotated[OptionsModelAzureEntraModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")]
    ]
    """Azure provider-specific model configuration"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class OptionsModelAzureAPIKeyModelConfigObjectProviderOptionsAzure(TypedDict, total=False):
    """Azure OpenAI provider-specific settings"""

    api_version: Annotated[str, PropertyInfo(alias="apiVersion")]
    """Azure OpenAI API version"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the Azure OpenAI provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the Azure OpenAI provider"""

    resource_name: Annotated[str, PropertyInfo(alias="resourceName")]
    """Azure OpenAI resource name"""

    use_deployment_based_urls: Annotated[bool, PropertyInfo(alias="useDeploymentBasedUrls")]
    """Whether to use deployment-based Azure OpenAI URLs"""


class OptionsModelAzureAPIKeyModelConfigObjectProviderOptions(TypedDict, total=False):
    """Azure provider-specific model configuration"""

    azure: Required[OptionsModelAzureAPIKeyModelConfigObjectProviderOptionsAzure]
    """Azure OpenAI provider-specific settings"""


class OptionsModelAzureAPIKeyModelConfigObject(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["azure"]]
    """Azure OpenAI model provider"""

    provider_options: Required[
        Annotated[OptionsModelAzureAPIKeyModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")]
    ]
    """Azure provider-specific model configuration"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class OptionsModelGenericModelConfigObject(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""

    openai_endpoint_format: Annotated[Literal["responses", "chat"], PropertyInfo(alias="openaiEndpointFormat")]
    """Wire format used by an OpenAI-compatible endpoint.

    Defaults to the Responses API; use chat for Chat Completions-only endpoints.
    """

    provider: Literal["openai", "anthropic", "google", "microsoft", "bedrock"]
    """AI provider for the model (or provide a baseURL endpoint instead)"""


OptionsModel: TypeAlias = Union[
    OptionsModelVertexModelConfigObject,
    OptionsModelAzureEntraModelConfigObject,
    OptionsModelAzureAPIKeyModelConfigObject,
    OptionsModelGenericModelConfigObject,
    str,
]


class OptionsVariablesUnionMember3(TypedDict, total=False):
    value: Required[Union[str, float, bool]]

    description: str


OptionsVariables: TypeAlias = Union[str, float, bool, OptionsVariablesUnionMember3]


class Options(TypedDict, total=False):
    ignore_selectors: Annotated[SequenceNotStr[str], PropertyInfo(alias="ignoreSelectors")]
    """Selectors for elements and subtrees that should be excluded from observation"""

    model: OptionsModel
    """Model configuration object or model name string (e.g., 'openai/gpt-5-nano')"""

    selector: str
    """CSS selector to scope observation to a specific element"""

    timeout: float
    """Timeout in ms for the observation"""

    variables: Dict[str, OptionsVariables]
    """
    Variables whose names are exposed to the model so observe() returns
    %variableName% placeholders in suggested action arguments instead of literal
    values. Accepts flat primitives or { value, description? } objects.
    """


class SessionObserveParamsNonStreaming(SessionObserveParamsBase, total=False):
    stream_response: Annotated[Literal[False], PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""


class SessionObserveParamsStreaming(SessionObserveParamsBase):
    stream_response: Required[Annotated[Literal[True], PropertyInfo(alias="streamResponse")]]
    """Whether to stream the response via SSE"""


SessionObserveParams = Union[SessionObserveParamsNonStreaming, SessionObserveParamsStreaming]
