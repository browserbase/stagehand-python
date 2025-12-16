# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionStartParams"]


class SessionStartParams(TypedDict, total=False):
    browserbase_api_key: Required[Annotated[str, PropertyInfo(alias="BROWSERBASE_API_KEY")]]
    """API key for Browserbase Cloud"""

    browserbase_project_id: Required[Annotated[str, PropertyInfo(alias="BROWSERBASE_PROJECT_ID")]]
    """Project ID for Browserbase"""

    dom_settle_timeout: Annotated[int, PropertyInfo(alias="domSettleTimeout")]
    """Timeout in ms to wait for DOM to settle"""

    model: str
    """AI model to use for actions (must be prefixed with provider/)"""

    self_heal: Annotated[bool, PropertyInfo(alias="selfHeal")]
    """Enable self-healing for failed actions"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Custom system prompt for AI actions"""

    verbose: int
    """Logging verbosity level"""
