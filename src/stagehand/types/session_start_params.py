# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SessionStartParams",
    "Browser",
    "BrowserLaunchOptions",
    "BrowserLaunchOptionsProxy",
    "BrowserLaunchOptionsViewport",
    "BrowserbaseSessionCreateParams",
    "BrowserbaseSessionCreateParamsBrowserSettings",
    "BrowserbaseSessionCreateParamsBrowserSettingsContext",
    "BrowserbaseSessionCreateParamsBrowserSettingsFingerprint",
    "BrowserbaseSessionCreateParamsBrowserSettingsFingerprintScreen",
    "BrowserbaseSessionCreateParamsBrowserSettingsViewport",
    "BrowserbaseSessionCreateParamsProxiesProxyConfigList",
    "BrowserbaseSessionCreateParamsProxiesProxyConfigListBrowserbaseProxyConfig",
    "BrowserbaseSessionCreateParamsProxiesProxyConfigListBrowserbaseProxyConfigGeolocation",
    "BrowserbaseSessionCreateParamsProxiesProxyConfigListExternalProxyConfig",
    "ModelClientOptions",
    "ModelClientOptionsBedrockAPIKeyModelClientOptions",
    "ModelClientOptionsBedrockAPIKeyModelClientOptionsProviderOptions",
    "ModelClientOptionsBedrockAwsCredentialsModelClientOptions",
    "ModelClientOptionsBedrockAwsCredentialsModelClientOptionsProviderOptions",
    "ModelClientOptionsGenericModelClientOptions",
    "ModelClientOptionsGenericModelClientOptionsProviderOptions",
    "ModelClientOptionsGenericModelClientOptionsProviderOptionsBedrockAPIKeyProviderOptions",
    "ModelClientOptionsGenericModelClientOptionsProviderOptionsBedrockAwsCredentialsProviderOptions",
    "ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptions",
    "ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptions",
    "ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptionsCredentials",
]


class SessionStartParams(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]
    """Model name to use for AI operations"""

    act_timeout_ms: Annotated[float, PropertyInfo(alias="actTimeoutMs")]
    """Timeout in ms for act operations (deprecated, v2 only)"""

    browser: Browser

    browserbase_session_create_params: Annotated[
        BrowserbaseSessionCreateParams, PropertyInfo(alias="browserbaseSessionCreateParams")
    ]

    browserbase_session_id: Annotated[str, PropertyInfo(alias="browserbaseSessionID")]
    """Existing Browserbase session ID to resume"""

    dom_settle_timeout_ms: Annotated[float, PropertyInfo(alias="domSettleTimeoutMs")]
    """Timeout in ms to wait for DOM to settle"""

    experimental: bool

    model_client_options: Annotated[ModelClientOptions, PropertyInfo(alias="modelClientOptions")]
    """
    Optional provider-specific configuration for the session model (for example
    Bedrock region and credentials)
    """

    self_heal: Annotated[bool, PropertyInfo(alias="selfHeal")]
    """Enable self-healing for failed actions"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Custom system prompt for AI operations"""

    verbose: Literal[0, 1, 2]
    """Logging verbosity level (0=quiet, 1=normal, 2=debug)"""

    wait_for_captcha_solves: Annotated[bool, PropertyInfo(alias="waitForCaptchaSolves")]
    """Wait for captcha solves (deprecated, v2 only)"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


class BrowserLaunchOptionsProxy(TypedDict, total=False):
    server: Required[str]

    bypass: str

    password: str

    username: str


class BrowserLaunchOptionsViewport(TypedDict, total=False):
    height: Required[float]

    width: Required[float]


class BrowserLaunchOptions(TypedDict, total=False):
    accept_downloads: Annotated[bool, PropertyInfo(alias="acceptDownloads")]

    args: SequenceNotStr[str]

    cdp_headers: Annotated[Dict[str, str], PropertyInfo(alias="cdpHeaders")]

    cdp_url: Annotated[str, PropertyInfo(alias="cdpUrl")]

    chromium_sandbox: Annotated[bool, PropertyInfo(alias="chromiumSandbox")]

    connect_timeout_ms: Annotated[float, PropertyInfo(alias="connectTimeoutMs")]

    device_scale_factor: Annotated[float, PropertyInfo(alias="deviceScaleFactor")]

    devtools: bool

    downloads_path: Annotated[str, PropertyInfo(alias="downloadsPath")]

    executable_path: Annotated[str, PropertyInfo(alias="executablePath")]

    has_touch: Annotated[bool, PropertyInfo(alias="hasTouch")]

    headless: bool

    ignore_default_args: Annotated[Union[bool, SequenceNotStr[str]], PropertyInfo(alias="ignoreDefaultArgs")]

    ignore_https_errors: Annotated[bool, PropertyInfo(alias="ignoreHTTPSErrors")]

    locale: str

    port: float

    preserve_user_data_dir: Annotated[bool, PropertyInfo(alias="preserveUserDataDir")]

    proxy: BrowserLaunchOptionsProxy

    user_data_dir: Annotated[str, PropertyInfo(alias="userDataDir")]

    viewport: BrowserLaunchOptionsViewport


class Browser(TypedDict, total=False):
    cdp_url: Annotated[str, PropertyInfo(alias="cdpUrl")]
    """Chrome DevTools Protocol URL for connecting to existing browser"""

    launch_options: Annotated[BrowserLaunchOptions, PropertyInfo(alias="launchOptions")]

    type: Literal["local", "browserbase"]
    """Browser type to use"""


class BrowserbaseSessionCreateParamsBrowserSettingsContext(TypedDict, total=False):
    id: Required[str]

    persist: bool


class BrowserbaseSessionCreateParamsBrowserSettingsFingerprintScreen(TypedDict, total=False):
    max_height: Annotated[float, PropertyInfo(alias="maxHeight")]

    max_width: Annotated[float, PropertyInfo(alias="maxWidth")]

    min_height: Annotated[float, PropertyInfo(alias="minHeight")]

    min_width: Annotated[float, PropertyInfo(alias="minWidth")]


class BrowserbaseSessionCreateParamsBrowserSettingsFingerprint(TypedDict, total=False):
    browsers: List[Literal["chrome", "edge", "firefox", "safari"]]

    devices: List[Literal["desktop", "mobile"]]

    http_version: Annotated[Literal["1", "2"], PropertyInfo(alias="httpVersion")]

    locales: SequenceNotStr[str]

    operating_systems: Annotated[
        List[Literal["android", "ios", "linux", "macos", "windows"]], PropertyInfo(alias="operatingSystems")
    ]

    screen: BrowserbaseSessionCreateParamsBrowserSettingsFingerprintScreen


class BrowserbaseSessionCreateParamsBrowserSettingsViewport(TypedDict, total=False):
    height: float

    width: float


class BrowserbaseSessionCreateParamsBrowserSettings(TypedDict, total=False):
    advanced_stealth: Annotated[bool, PropertyInfo(alias="advancedStealth")]

    block_ads: Annotated[bool, PropertyInfo(alias="blockAds")]

    captcha_image_selector: Annotated[str, PropertyInfo(alias="captchaImageSelector")]

    captcha_input_selector: Annotated[str, PropertyInfo(alias="captchaInputSelector")]

    context: BrowserbaseSessionCreateParamsBrowserSettingsContext

    extension_id: Annotated[str, PropertyInfo(alias="extensionId")]

    fingerprint: BrowserbaseSessionCreateParamsBrowserSettingsFingerprint

    log_session: Annotated[bool, PropertyInfo(alias="logSession")]

    os: Literal["windows", "mac", "linux", "mobile", "tablet"]

    record_session: Annotated[bool, PropertyInfo(alias="recordSession")]

    solve_captchas: Annotated[bool, PropertyInfo(alias="solveCaptchas")]

    verified: bool

    viewport: BrowserbaseSessionCreateParamsBrowserSettingsViewport


class BrowserbaseSessionCreateParamsProxiesProxyConfigListBrowserbaseProxyConfigGeolocation(TypedDict, total=False):
    country: Required[str]

    city: str

    state: str


class BrowserbaseSessionCreateParamsProxiesProxyConfigListBrowserbaseProxyConfig(TypedDict, total=False):
    type: Required[Literal["browserbase"]]

    domain_pattern: Annotated[str, PropertyInfo(alias="domainPattern")]

    geolocation: BrowserbaseSessionCreateParamsProxiesProxyConfigListBrowserbaseProxyConfigGeolocation


class BrowserbaseSessionCreateParamsProxiesProxyConfigListExternalProxyConfig(TypedDict, total=False):
    server: Required[str]

    type: Required[Literal["external"]]

    domain_pattern: Annotated[str, PropertyInfo(alias="domainPattern")]

    password: str

    username: str


BrowserbaseSessionCreateParamsProxiesProxyConfigList: TypeAlias = Union[
    BrowserbaseSessionCreateParamsProxiesProxyConfigListBrowserbaseProxyConfig,
    BrowserbaseSessionCreateParamsProxiesProxyConfigListExternalProxyConfig,
]


class BrowserbaseSessionCreateParams(TypedDict, total=False):
    browser_settings: Annotated[BrowserbaseSessionCreateParamsBrowserSettings, PropertyInfo(alias="browserSettings")]

    extension_id: Annotated[str, PropertyInfo(alias="extensionId")]

    keep_alive: Annotated[bool, PropertyInfo(alias="keepAlive")]

    project_id: Annotated[str, PropertyInfo(alias="projectId")]

    proxies: Union[bool, Iterable[BrowserbaseSessionCreateParamsProxiesProxyConfigList]]

    region: Literal["us-west-2", "us-east-1", "eu-central-1", "ap-southeast-1"]

    timeout: float

    user_metadata: Annotated[Dict[str, object], PropertyInfo(alias="userMetadata")]


class ModelClientOptionsBedrockAPIKeyModelClientOptionsProviderOptions(TypedDict, total=False):
    region: Required[str]
    """AWS region for Amazon Bedrock"""


class ModelClientOptionsBedrockAPIKeyModelClientOptions(TypedDict, total=False):
    api_key: Required[Annotated[str, PropertyInfo(alias="apiKey")]]
    """Short-term Bedrock API key for bearer-token auth"""

    provider_options: Required[
        Annotated[
            ModelClientOptionsBedrockAPIKeyModelClientOptionsProviderOptions, PropertyInfo(alias="providerOptions")
        ]
    ]

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers for the model provider"""

    skip_api_key_fallback: Annotated[bool, PropertyInfo(alias="skipApiKeyFallback")]
    """When true, hosted sessions will not copy x-model-api-key into model.apiKey.

    Use this when auth is carried through providerOptions instead of an API key.
    """


class ModelClientOptionsBedrockAwsCredentialsModelClientOptionsProviderOptions(TypedDict, total=False):
    access_key_id: Required[Annotated[str, PropertyInfo(alias="accessKeyId")]]
    """AWS access key ID for Bedrock"""

    region: Required[str]
    """AWS region for Amazon Bedrock"""

    secret_access_key: Required[Annotated[str, PropertyInfo(alias="secretAccessKey")]]
    """AWS secret access key for Bedrock"""

    session_token: Annotated[str, PropertyInfo(alias="sessionToken")]
    """Optional AWS session token for temporary credentials"""


class ModelClientOptionsBedrockAwsCredentialsModelClientOptions(TypedDict, total=False):
    provider_options: Required[
        Annotated[
            ModelClientOptionsBedrockAwsCredentialsModelClientOptionsProviderOptions,
            PropertyInfo(alias="providerOptions"),
        ]
    ]

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers for the model provider"""

    skip_api_key_fallback: Annotated[bool, PropertyInfo(alias="skipApiKeyFallback")]
    """When true, hosted sessions will not copy x-model-api-key into model.apiKey.

    Use this when auth is carried through providerOptions instead of an API key.
    """


class ModelClientOptionsGenericModelClientOptionsProviderOptionsBedrockAPIKeyProviderOptions(TypedDict, total=False):
    region: Required[str]
    """AWS region for Amazon Bedrock"""


class ModelClientOptionsGenericModelClientOptionsProviderOptionsBedrockAwsCredentialsProviderOptions(
    TypedDict, total=False
):
    access_key_id: Required[Annotated[str, PropertyInfo(alias="accessKeyId")]]
    """AWS access key ID for Bedrock"""

    region: Required[str]
    """AWS region for Amazon Bedrock"""

    secret_access_key: Required[Annotated[str, PropertyInfo(alias="secretAccessKey")]]
    """AWS secret access key for Bedrock"""

    session_token: Annotated[str, PropertyInfo(alias="sessionToken")]
    """Optional AWS session token for temporary credentials"""


class ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptionsCredentials(
    TypedDict, total=False
):
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


class ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptions(
    TypedDict, total=False
):
    """Optional Google auth options for Vertex AI"""

    credentials: ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptionsCredentials


class ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptions(TypedDict, total=False):
    google_auth_options: Annotated[
        ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptionsGoogleAuthOptions,
        PropertyInfo(alias="googleAuthOptions"),
    ]
    """Optional Google auth options for Vertex AI"""

    headers: Dict[str, str]
    """Custom headers for Vertex AI requests"""

    location: str
    """Google Cloud location for Vertex AI"""

    project: str
    """Google Cloud project ID for Vertex AI"""


ModelClientOptionsGenericModelClientOptionsProviderOptions: TypeAlias = Union[
    ModelClientOptionsGenericModelClientOptionsProviderOptionsBedrockAPIKeyProviderOptions,
    ModelClientOptionsGenericModelClientOptionsProviderOptionsBedrockAwsCredentialsProviderOptions,
    ModelClientOptionsGenericModelClientOptionsProviderOptionsGoogleVertexProviderOptions,
]


class ModelClientOptionsGenericModelClientOptions(TypedDict, total=False):
    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for the model provider"""

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]
    """Base URL for the model provider"""

    headers: Dict[str, str]
    """Custom headers for the model provider"""

    provider_options: Annotated[
        ModelClientOptionsGenericModelClientOptionsProviderOptions, PropertyInfo(alias="providerOptions")
    ]
    """Provider-specific options passed through to the AI SDK provider constructor.

    For Bedrock: { region, accessKeyId, secretAccessKey, sessionToken }. For Vertex:
    { project, location, googleAuthOptions }.
    """

    skip_api_key_fallback: Annotated[bool, PropertyInfo(alias="skipApiKeyFallback")]
    """When true, hosted sessions will not copy x-model-api-key into model.apiKey.

    Use this when auth is carried through providerOptions instead of an API key.
    """


ModelClientOptions: TypeAlias = Union[
    ModelClientOptionsBedrockAPIKeyModelClientOptions,
    ModelClientOptionsBedrockAwsCredentialsModelClientOptions,
    ModelClientOptionsGenericModelClientOptions,
]
