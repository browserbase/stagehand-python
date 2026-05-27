# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .action_param import ActionParam

__all__ = [
    "SessionActParamsBase",
    "Input",
    "Options",
    "OptionsModel",
    "OptionsModelVertexModelConfigObject",
    "OptionsModelVertexModelConfigObjectAuth",
    "OptionsModelVertexModelConfigObjectAuthCredentials",
    "OptionsModelVertexModelConfigObjectProviderOptions",
    "OptionsModelVertexModelConfigObjectProviderOptionsVertex",
    "OptionsModelGenericModelConfigObject",
    "OptionsVariables",
    "OptionsVariablesUnionMember3",
    "SessionActParamsNonStreaming",
    "SessionActParamsStreaming",
]


class SessionActParamsBase(TypedDict, total=False):
    input: Required[Input]
    """Natural language instruction or Action object"""

    frame_id: Annotated[Optional[str], PropertyInfo(alias="frameId")]
    """Target frame ID for the action"""

    options: Options

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


Input: TypeAlias = Union[str, ActionParam]


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


class OptionsModelGenericModelConfigObject(TypedDict, total=False):
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


OptionsModel: TypeAlias = Union[OptionsModelVertexModelConfigObject, OptionsModelGenericModelConfigObject, str]


class OptionsVariablesUnionMember3(TypedDict, total=False):
    value: Required[Union[str, float, bool]]

    description: str


OptionsVariables: TypeAlias = Union[str, float, bool, OptionsVariablesUnionMember3]


class Options(TypedDict, total=False):
    model: OptionsModel
    """Model configuration object or model name string (e.g., 'openai/gpt-5-nano')"""

    timeout: float
    """Timeout in ms for the action"""

    variables: Dict[str, OptionsVariables]
    """Variables to substitute in the action instruction.

    Accepts flat primitives or { value, description? } objects.
    """


class SessionActParamsNonStreaming(SessionActParamsBase, total=False):
    stream_response: Annotated[Literal[False], PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""


class SessionActParamsStreaming(SessionActParamsBase):
    stream_response: Required[Annotated[Literal[True], PropertyInfo(alias="streamResponse")]]
    """Whether to stream the response via SSE"""


SessionActParams = Union[SessionActParamsNonStreaming, SessionActParamsStreaming]
