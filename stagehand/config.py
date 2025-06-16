from typing import Any, Callable, Literal, Optional

from browserbase.types import SessionCreateParams as BrowserbaseSessionCreateParams
from pydantic import BaseModel, ConfigDict, Field

from stagehand.schemas import AvailableModel


class StagehandConfig(BaseModel):
    """
    Configuration for the Stagehand client.

    Attributes:
        env (str): Environment type. 'BROWSERBASE' for remote usage
        api_key (Optional[str]): BrowserbaseAPI key for authentication.
        project_id (Optional[str]): Browserbase Project identifier.
        api_url (Optional[str]): Stagehand API URL.
        browserbase_session_create_params (Optional[BrowserbaseSessionCreateParams]): Browserbase session create params.
        browserbase_session_id (Optional[str]): Session ID for resuming Browserbase sessions.
        model_name (Optional[str]): Name of the model to use.
        model_api_key (Optional[str]): Model API key.
        logger (Optional[Callable[[Any], None]]): Custom logging function.
        verbose (Optional[int]): Verbosity level for logs (1=minimal, 2=medium, 3=detailed).
        use_rich_logging (bool): Whether to use Rich for colorized logging.
        dom_settle_timeout_ms (Optional[int]): Timeout for DOM to settle (in milliseconds).
        enable_caching (Optional[bool]): Enable caching functionality.
        self_heal (Optional[bool]): Enable self-healing functionality.
        wait_for_captcha_solves (Optional[bool]): Whether to wait for CAPTCHA to be solved.
        act_timeout_ms (Optional[int]): Timeout for act commands (in milliseconds).
        headless (bool): Run browser in headless mode
        system_prompt (Optional[str]): System prompt to use for LLM interactions.
        local_browser_launch_options (Optional[dict[str, Any]]): Local browser launch options.
    """

    env: Literal["BROWSERBASE", "LOCAL"] = "BROWSERBASE"
    api_key: Optional[str] = Field(
        None, alias="apiKey", description="Browserbase API key for authentication"
    )
    project_id: Optional[str] = Field(
        None, alias="projectId", description="Browserbase project ID"
    )
    api_url: Optional[str] = Field(
        "https://api.stagehand.browserbase.com/v1",
        alias="apiUrl",
        description="Stagehand API URL",
    )  # might add a default value here
    model_api_key: Optional[str] = Field(
        None, alias="modelApiKey", description="Model API key"
    )
    verbose: Optional[int] = Field(
        1,
        description="Verbosity level for logs: 0=minimal (ERROR), 1=medium (INFO), 2=detailed (DEBUG)",
    )
    logger: Optional[Callable[[Any], None]] = Field(
        None, description="Custom logging function"
    )
    use_rich_logging: Optional[bool] = Field(
        True, description="Whether to use Rich for colorized logging"
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
        {},
        alias="localBrowserLaunchOptions",
        description="Local browser launch options",
    )
    use_api: Optional[bool] = Field(
        True,
        alias=None,
        description="Whether to use the Stagehand API",
    )
    experimental: Optional[bool] = Field(
        False,
        alias=None,
        description="Whether to use experimental features",
    )

    model_config = ConfigDict(populate_by_name=True)

    def with_overrides(self, **overrides) -> "StagehandConfig":
        """
        Create a new config instance with the specified overrides.

        Args:
            **overrides: Key-value pairs to override in the config

        Returns:
            StagehandConfig: New config instance with overrides applied
        """
        config_dict = self.model_dump()
        config_dict.update(overrides)
        return StagehandConfig(**config_dict)


# Default configuration instance
default_config = StagehandConfig()
