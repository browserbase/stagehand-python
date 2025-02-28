from typing import Any, Callable, Optional

from pydantic import BaseModel, Field

from stagehand.schemas import AvailableModel


class StagehandConfig(BaseModel):
    """
    Configuration for the Stagehand client.

    Attributes:
        env (str): Environment type. 'BROWSERBASE' for remote usage
        api_key (Optional[str]): API key for authentication.
        project_id (Optional[str]): Project identifier.
        debug_dom (bool): Enable DOM debugging features.
        headless (bool): Run browser in headless mode.
        logger (Optional[Callable[[Any], None]]): Custom logging function.
        dom_settle_timeout_ms (Optional[int]): Timeout for DOM to settle (in milliseconds).
        enable_caching (Optional[bool]): Enable caching functionality.
        browserbase_session_id (Optional[str]): Session ID for resuming Browserbase sessions.
        model_name (Optional[str]): Name of the model to use.
        self_heal (Optional[bool]): Enable self-healing functionality.
    """

    env: str = "BROWSERBASE"
    api_key: Optional[str] = Field(
        None, alias="apiKey", description="Browserbase API key for authentication"
    )
    project_id: Optional[str] = Field(
        None, alias="projectId", description="Browserbase project ID"
    )
    debug_dom: bool = Field(
        False, alias="debugDom", description="Enable DOM debugging features"
    )
    headless: bool = Field(True, description="Run browser in headless mode")
    logger: Optional[Callable[[Any], None]] = Field(
        None, description="Custom logging function"
    )
    dom_settle_timeout_ms: Optional[int] = Field(
        3000,
        alias="domSettleTimeoutMs",
        description="Timeout for DOM to settle (in ms)",
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

    class Config:
        populate_by_name = True
