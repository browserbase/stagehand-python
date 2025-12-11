# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionStartParams", "LocalBrowserLaunchOptions"]


class SessionStartParams(TypedDict, total=False):
    env: Required[Literal["LOCAL", "BROWSERBASE"]]
    """Environment to run the browser in"""

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]
    """API key for Browserbase (required when env=BROWSERBASE)"""

    dom_settle_timeout: Annotated[int, PropertyInfo(alias="domSettleTimeout")]
    """Timeout in ms to wait for DOM to settle"""

    local_browser_launch_options: Annotated[LocalBrowserLaunchOptions, PropertyInfo(alias="localBrowserLaunchOptions")]
    """Options for local browser launch"""

    model: str
    """AI model to use for actions"""

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """Project ID for Browserbase (required when env=BROWSERBASE)"""

    self_heal: Annotated[bool, PropertyInfo(alias="selfHeal")]
    """Enable self-healing for failed actions"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Custom system prompt for AI actions"""

    verbose: int
    """Logging verbosity level"""


class LocalBrowserLaunchOptions(TypedDict, total=False):
    """Options for local browser launch"""

    headless: bool
