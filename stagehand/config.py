from typing import Any, Callable, Optional

from browserbase.types import SessionCreateParams as BrowserbaseSessionCreateParams
from pydantic import BaseModel, ConfigDict, Field

from stagehand.schemas import AvailableModel


class StagehandConfig(BaseModel):
    """
    Configuration for the Stagehand client.

    Attributes:
        env (str): Environment type. 'BROWSERBASE' for remote usage
        api_key (Optional[str]): API key for authentication.
        project_id (Optional[str]): Project identifier.
        headless (bool): Run browser in headless mode.
        logger (Optional[Callable[[Any], None]]): Custom logging function.
        dom_settle_timeout_ms (Optional[int]): Timeout for DOM to settle (in milliseconds).
        enable_caching (Optional[bool]): Enable caching functionality.
        browserbase_session_id (Optional[str]): Session ID for resuming Browserbase sessions.
        model_name (Optional[str]): Name of the model to use.
        self_heal (Optional[bool]): Enable self-healing functionality.
        wait_for_captcha_solves (Optional[bool]): Whether to wait for CAPTCHA to be solved.
        act_timeout_ms (Optional[int]): Timeout for act commands (in milliseconds).
        system_prompt (Optional[str]): System prompt to use for LLM interactions.
        verbose (Optional[int]): Verbosity level for logs (1=minimal, 2=medium, 3=detailed).
        local_browser_launch_options (Optional[dict[str, Any]]): Local browser launch options.
    """

    env: str = "BROWSERBASE"
    api_key: Optional[str] = Field(
        None, alias="apiKey", description="Browserbase API key for authentication"
    )
    project_id: Optional[str] = Field(
        None, alias="projectId", description="Browserbase project ID"
    )
    verbose: Optional[int] = Field(
        1,
        description="Verbosity level for logs: 1=minimal (INFO), 2=medium (WARNING), 3=detailed (DEBUG)",
    )
    logger: Optional[Callable[[Any], None]] = Field(
        None, description="Custom logging function"
    )
    dom_settle_timeout_ms: Optional[int] = Field(
        3000,
        alias="domSettleTimeoutMs",
        description="Timeout for DOM to settle (in ms)",
    )
    browserbase_session_create_params: Optional[BrowserbaseSessionCreateParams] = Field(
        None,
        alias="browserbaseSessionCreateParams",
        description="Browserbase session create params",
    )
    enable_caching: Optional[bool] = Field(
        False, alias="enableCaching", description="Enable caching functionality"
    )
    browserbase_session_id: Optional[str] = Field(
        None,
        alias="browserbaseSessionID",
        description="Session ID for resuming Browserbase sessions",
    )
    model_name: Optional[str] = Field(
        AvailableModel.GPT_4O, alias="modelName", description="Name of the model to use"
    )
    self_heal: Optional[bool] = Field(
        True, alias="selfHeal", description="Enable self-healing functionality"
    )
    wait_for_captcha_solves: Optional[bool] = Field(
        False,
        alias="waitForCaptchaSolves",
        description="Whether to wait for CAPTCHA to be solved",
    )
    system_prompt: Optional[str] = Field(
        None,
        alias="systemPrompt",
        description="System prompt to use for LLM interactions",
    )
    local_browser_launch_options: Optional[dict[str, Any]] = Field(
        None,
        alias="localBrowserLaunchOptions",
        description="Local browser launch options",
    )

    model_config = ConfigDict(populate_by_name=True)
