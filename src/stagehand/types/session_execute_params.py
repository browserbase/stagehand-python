# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SessionExecuteParamsBase",
    "AgentConfig",
    "AgentConfigExecutionModel",
    "AgentConfigExecutionModelVertexModelConfigObject",
    "AgentConfigExecutionModelVertexModelConfigObjectAuth",
    "AgentConfigExecutionModelVertexModelConfigObjectAuthCredentials",
    "AgentConfigExecutionModelVertexModelConfigObjectProviderOptions",
    "AgentConfigExecutionModelVertexModelConfigObjectProviderOptionsVertex",
    "AgentConfigExecutionModelAzureEntraModelConfigObject",
    "AgentConfigExecutionModelAzureEntraModelConfigObjectAuth",
    "AgentConfigExecutionModelAzureEntraModelConfigObjectProviderOptions",
    "AgentConfigExecutionModelAzureEntraModelConfigObjectProviderOptionsAzure",
    "AgentConfigExecutionModelAzureAPIKeyModelConfigObject",
    "AgentConfigExecutionModelAzureAPIKeyModelConfigObjectProviderOptions",
    "AgentConfigExecutionModelAzureAPIKeyModelConfigObjectProviderOptionsAzure",
    "AgentConfigExecutionModelGenericModelConfigObject",
    "AgentConfigModel",
    "AgentConfigModelVertexModelConfigObject",
    "AgentConfigModelVertexModelConfigObjectAuth",
    "AgentConfigModelVertexModelConfigObjectAuthCredentials",
    "AgentConfigModelVertexModelConfigObjectProviderOptions",
    "AgentConfigModelVertexModelConfigObjectProviderOptionsVertex",
    "AgentConfigModelAzureEntraModelConfigObject",
    "AgentConfigModelAzureEntraModelConfigObjectAuth",
    "AgentConfigModelAzureEntraModelConfigObjectProviderOptions",
    "AgentConfigModelAzureEntraModelConfigObjectProviderOptionsAzure",
    "AgentConfigModelAzureAPIKeyModelConfigObject",
    "AgentConfigModelAzureAPIKeyModelConfigObjectProviderOptions",
    "AgentConfigModelAzureAPIKeyModelConfigObjectProviderOptionsAzure",
    "AgentConfigModelGenericModelConfigObject",
    "ExecuteOptions",
    "ExecuteOptionsVariables",
    "ExecuteOptionsVariablesUnionMember3",
    "SessionExecuteParamsNonStreaming",
    "SessionExecuteParamsStreaming",
]


class SessionExecuteParamsBase(TypedDict, total=False):
    agent_config: Required[Annotated[AgentConfig, PropertyInfo(alias="agentConfig")]]

    execute_options: Required[Annotated[ExecuteOptions, PropertyInfo(alias="executeOptions")]]

    frame_id: Annotated[Optional[str], PropertyInfo(alias="frameId")]
    """Target frame ID for the agent"""

    should_cache: Annotated[bool, PropertyInfo(alias="shouldCache")]
    """If true, the server captures a cache entry and returns it to the client"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


class AgentConfigExecutionModelVertexModelConfigObjectAuthCredentials(TypedDict, total=False):
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


class AgentConfigExecutionModelVertexModelConfigObjectAuth(TypedDict, total=False):
    """Vertex provider authentication configuration"""

    credentials: Required[AgentConfigExecutionModelVertexModelConfigObjectAuthCredentials]
    """Google Cloud service account credentials"""

    type: Required[Literal["googleServiceAccount"]]
    """Use inline Google Cloud service account credentials for provider authentication"""

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Google Cloud project ID used by google-auth-library"""

    scopes: Union[str, SequenceNotStr[str]]
    """Google auth scopes for the desired API request"""

    universe_domain: Annotated[str, PropertyInfo(alias="universeDomain")]
    """Google Cloud universe domain"""


class AgentConfigExecutionModelVertexModelConfigObjectProviderOptionsVertex(TypedDict, total=False):
    """Vertex AI provider-specific settings"""

    location: Required[str]
    """Google Cloud location for Vertex AI models"""

    project: Required[str]
    """Google Cloud project ID for Vertex AI models"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the Vertex AI provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the Vertex AI provider"""


class AgentConfigExecutionModelVertexModelConfigObjectProviderOptions(TypedDict, total=False):
    """Vertex provider-specific model configuration"""

    vertex: Required[AgentConfigExecutionModelVertexModelConfigObjectProviderOptionsVertex]
    """Vertex AI provider-specific settings"""


class AgentConfigExecutionModelVertexModelConfigObject(TypedDict, total=False):
    auth: Required[AgentConfigExecutionModelVertexModelConfigObjectAuth]
    """Vertex provider authentication configuration"""

    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["vertex"]]
    """Vertex AI model provider"""

    provider_options: Required[
        Annotated[
            AgentConfigExecutionModelVertexModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")
        ]
    ]
    """Vertex provider-specific model configuration"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class AgentConfigExecutionModelAzureEntraModelConfigObjectAuth(TypedDict, total=False):
    """Azure provider authentication configuration"""

    token: Required[str]
    """Microsoft Entra ID bearer token for Azure OpenAI"""

    type: Required[Literal["azureEntraId"]]
    """Use a Microsoft Entra ID bearer token for authentication"""


class AgentConfigExecutionModelAzureEntraModelConfigObjectProviderOptionsAzure(TypedDict, total=False):
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


class AgentConfigExecutionModelAzureEntraModelConfigObjectProviderOptions(TypedDict, total=False):
    """Azure provider-specific model configuration"""

    azure: Required[AgentConfigExecutionModelAzureEntraModelConfigObjectProviderOptionsAzure]
    """Azure OpenAI provider-specific settings"""


class AgentConfigExecutionModelAzureEntraModelConfigObject(TypedDict, total=False):
    auth: Required[AgentConfigExecutionModelAzureEntraModelConfigObjectAuth]
    """Azure provider authentication configuration"""

    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["azure"]]
    """Azure OpenAI model provider"""

    provider_options: Required[
        Annotated[
            AgentConfigExecutionModelAzureEntraModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")
        ]
    ]
    """Azure provider-specific model configuration"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class AgentConfigExecutionModelAzureAPIKeyModelConfigObjectProviderOptionsAzure(TypedDict, total=False):
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


class AgentConfigExecutionModelAzureAPIKeyModelConfigObjectProviderOptions(TypedDict, total=False):
    """Azure provider-specific model configuration"""

    azure: Required[AgentConfigExecutionModelAzureAPIKeyModelConfigObjectProviderOptionsAzure]
    """Azure OpenAI provider-specific settings"""


class AgentConfigExecutionModelAzureAPIKeyModelConfigObject(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["azure"]]
    """Azure OpenAI model provider"""

    provider_options: Required[
        Annotated[
            AgentConfigExecutionModelAzureAPIKeyModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")
        ]
    ]
    """Azure provider-specific model configuration"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class AgentConfigExecutionModelGenericModelConfigObject(TypedDict, total=False):
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


AgentConfigExecutionModel: TypeAlias = Union[
    AgentConfigExecutionModelVertexModelConfigObject,
    AgentConfigExecutionModelAzureEntraModelConfigObject,
    AgentConfigExecutionModelAzureAPIKeyModelConfigObject,
    AgentConfigExecutionModelGenericModelConfigObject,
    str,
]


class AgentConfigModelVertexModelConfigObjectAuthCredentials(TypedDict, total=False):
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


class AgentConfigModelVertexModelConfigObjectAuth(TypedDict, total=False):
    """Vertex provider authentication configuration"""

    credentials: Required[AgentConfigModelVertexModelConfigObjectAuthCredentials]
    """Google Cloud service account credentials"""

    type: Required[Literal["googleServiceAccount"]]
    """Use inline Google Cloud service account credentials for provider authentication"""

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Google Cloud project ID used by google-auth-library"""

    scopes: Union[str, SequenceNotStr[str]]
    """Google auth scopes for the desired API request"""

    universe_domain: Annotated[str, PropertyInfo(alias="universeDomain")]
    """Google Cloud universe domain"""


class AgentConfigModelVertexModelConfigObjectProviderOptionsVertex(TypedDict, total=False):
    """Vertex AI provider-specific settings"""

    location: Required[str]
    """Google Cloud location for Vertex AI models"""

    project: Required[str]
    """Google Cloud project ID for Vertex AI models"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the Vertex AI provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the Vertex AI provider"""


class AgentConfigModelVertexModelConfigObjectProviderOptions(TypedDict, total=False):
    """Vertex provider-specific model configuration"""

    vertex: Required[AgentConfigModelVertexModelConfigObjectProviderOptionsVertex]
    """Vertex AI provider-specific settings"""


class AgentConfigModelVertexModelConfigObject(TypedDict, total=False):
    auth: Required[AgentConfigModelVertexModelConfigObjectAuth]
    """Vertex provider authentication configuration"""

    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["vertex"]]
    """Vertex AI model provider"""

    provider_options: Required[
        Annotated[AgentConfigModelVertexModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")]
    ]
    """Vertex provider-specific model configuration"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class AgentConfigModelAzureEntraModelConfigObjectAuth(TypedDict, total=False):
    """Azure provider authentication configuration"""

    token: Required[str]
    """Microsoft Entra ID bearer token for Azure OpenAI"""

    type: Required[Literal["azureEntraId"]]
    """Use a Microsoft Entra ID bearer token for authentication"""


class AgentConfigModelAzureEntraModelConfigObjectProviderOptionsAzure(TypedDict, total=False):
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


class AgentConfigModelAzureEntraModelConfigObjectProviderOptions(TypedDict, total=False):
    """Azure provider-specific model configuration"""

    azure: Required[AgentConfigModelAzureEntraModelConfigObjectProviderOptionsAzure]
    """Azure OpenAI provider-specific settings"""


class AgentConfigModelAzureEntraModelConfigObject(TypedDict, total=False):
    auth: Required[AgentConfigModelAzureEntraModelConfigObjectAuth]
    """Azure provider authentication configuration"""

    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["azure"]]
    """Azure OpenAI model provider"""

    provider_options: Required[
        Annotated[AgentConfigModelAzureEntraModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")]
    ]
    """Azure provider-specific model configuration"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class AgentConfigModelAzureAPIKeyModelConfigObjectProviderOptionsAzure(TypedDict, total=False):
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


class AgentConfigModelAzureAPIKeyModelConfigObjectProviderOptions(TypedDict, total=False):
    """Azure provider-specific model configuration"""

    azure: Required[AgentConfigModelAzureAPIKeyModelConfigObjectProviderOptionsAzure]
    """Azure OpenAI provider-specific settings"""


class AgentConfigModelAzureAPIKeyModelConfigObject(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    provider: Required[Literal["azure"]]
    """Azure OpenAI model provider"""

    provider_options: Required[
        Annotated[AgentConfigModelAzureAPIKeyModelConfigObjectProviderOptions, PropertyInfo(alias="providerOptions")]
    ]
    """Azure provider-specific model configuration"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""


class AgentConfigModelGenericModelConfigObject(TypedDict, total=False):
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


AgentConfigModel: TypeAlias = Union[
    AgentConfigModelVertexModelConfigObject,
    AgentConfigModelAzureEntraModelConfigObject,
    AgentConfigModelAzureAPIKeyModelConfigObject,
    AgentConfigModelGenericModelConfigObject,
    str,
]


class AgentConfig(TypedDict, total=False):
    cua: bool
    """Deprecated.

    Use mode: 'cua' instead. If both are provided, mode takes precedence.
    """

    execution_model: Annotated[AgentConfigExecutionModel, PropertyInfo(alias="executionModel")]
    """
    Model configuration object or model name string (e.g., 'openai/gpt-5-nano') for
    tool execution (observe/act calls within agent tools). If not specified,
    inherits from the main model configuration.
    """

    mode: Literal["dom", "hybrid", "cua"]
    """Tool mode for the agent (dom, hybrid, cua). If set, overrides cua."""

    model: AgentConfigModel
    """Model configuration object or model name string (e.g., 'openai/gpt-5-nano')"""

    provider: Literal["openai", "anthropic", "google", "microsoft", "bedrock"]
    """AI provider for the agent (legacy, use model: openai/gpt-5-nano instead)"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Custom system prompt for the agent"""


class ExecuteOptionsVariablesUnionMember3(TypedDict, total=False):
    value: Required[Union[str, float, bool]]

    description: str


ExecuteOptionsVariables: TypeAlias = Union[str, float, bool, ExecuteOptionsVariablesUnionMember3]


class ExecuteOptions(TypedDict, total=False):
    instruction: Required[str]
    """Natural language instruction for the agent"""

    highlight_cursor: Annotated[bool, PropertyInfo(alias="highlightCursor")]
    """Whether to visually highlight the cursor during execution"""

    max_steps: Annotated[float, PropertyInfo(alias="maxSteps")]
    """Maximum number of steps the agent can take"""

    tool_timeout: Annotated[float, PropertyInfo(alias="toolTimeout")]
    """Timeout in milliseconds for each agent tool call"""

    use_search: Annotated[bool, PropertyInfo(alias="useSearch")]
    """Whether to enable the web search tool powered by Browserbase Search API"""

    variables: Dict[str, ExecuteOptionsVariables]
    """Variables available to the agent via %variableName% syntax in supported tools"""


class SessionExecuteParamsNonStreaming(SessionExecuteParamsBase, total=False):
    stream_response: Annotated[Literal[False], PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""


class SessionExecuteParamsStreaming(SessionExecuteParamsBase):
    stream_response: Required[Annotated[Literal[True], PropertyInfo(alias="streamResponse")]]
    """Whether to stream the response via SSE"""


SessionExecuteParams = Union[SessionExecuteParamsNonStreaming, SessionExecuteParamsStreaming]
