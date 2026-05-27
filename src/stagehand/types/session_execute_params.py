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
    "AgentConfigExecutionModelGenericModelConfigObject",
    "AgentConfigModel",
    "AgentConfigModelVertexModelConfigObject",
    "AgentConfigModelVertexModelConfigObjectAuth",
    "AgentConfigModelVertexModelConfigObjectAuthCredentials",
    "AgentConfigModelVertexModelConfigObjectProviderOptions",
    "AgentConfigModelVertexModelConfigObjectProviderOptionsVertex",
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


class AgentConfigExecutionModelGenericModelConfigObject(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""

    provider: Literal["openai", "anthropic", "google", "microsoft", "bedrock"]
    """AI provider for the model (or provide a baseURL endpoint instead)"""


AgentConfigExecutionModel: TypeAlias = Union[
    AgentConfigExecutionModelVertexModelConfigObject, AgentConfigExecutionModelGenericModelConfigObject, str
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


class AgentConfigModelGenericModelConfigObject(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name string with provider prefix (e.g., 'openai/gpt-5-nano')"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers sent with every request to the model provider"""

    provider: Literal["openai", "anthropic", "google", "microsoft", "bedrock"]
    """AI provider for the model (or provide a baseURL endpoint instead)"""


AgentConfigModel: TypeAlias = Union[
    AgentConfigModelVertexModelConfigObject, AgentConfigModelGenericModelConfigObject, str
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
