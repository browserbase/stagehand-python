# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from datetime import datetime
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

    self_heal: Annotated[bool, PropertyInfo(alias="selfHeal")]
    """Enable self-healing for failed actions"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Custom system prompt for AI operations"""

    verbose: Literal[0, 1, 2]
    """Logging verbosity level (0=quiet, 1=normal, 2=debug)"""

    wait_for_captcha_solves: Annotated[bool, PropertyInfo(alias="waitForCaptchaSolves")]
    """Wait for captcha solves (deprecated, v2 only)"""

    x_sent_at: Annotated[Union[str, datetime], PropertyInfo(alias="x-sent-at", format="iso8601")]
    """ISO timestamp when request was sent"""

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

    context: BrowserbaseSessionCreateParamsBrowserSettingsContext

    extension_id: Annotated[str, PropertyInfo(alias="extensionId")]

    fingerprint: BrowserbaseSessionCreateParamsBrowserSettingsFingerprint

    log_session: Annotated[bool, PropertyInfo(alias="logSession")]

    record_session: Annotated[bool, PropertyInfo(alias="recordSession")]

    solve_captchas: Annotated[bool, PropertyInfo(alias="solveCaptchas")]

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
