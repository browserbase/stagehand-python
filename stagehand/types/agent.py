from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, RootModel


class AgentConfig(BaseModel):
    """
    Configuration for agent execution.

    Attributes:
        model (Optional[str]): The model name to use.
        instructions (Optional[str]): Custom instructions for the agent (system prompt).
        options (Optional[dict[str, Any]]): Additional provider-specific options.
    """

    model: Optional[str] = None
    instructions: Optional[str] = None
    options: Optional[dict[str, Any]] = None
    max_steps: Optional[int] = 20


class ClickAction(BaseModel):
    type: Literal["click"]
    x: int
    y: int
    button: Optional[Literal["left", "right", "middle", "back", "forward"]]


class DoubleClickAction(BaseModel):
    type: Literal["double_click", "doubleClick"]
    x: int
    y: int


class TypeAction(BaseModel):
    type: Literal["type"]
    text: str
    x: Optional[int] = None
    y: Optional[int] = None
    press_enter_after: Optional[bool] = False


class KeyPressAction(BaseModel):
    type: Literal["keypress"]
    keys: list[str]  # e.g., ["CONTROL", "A"]


class ScrollAction(BaseModel):
    type: Literal["scroll"]
    x: int
    y: int
    scroll_x: Optional[int]
    scroll_y: Optional[int]


class Point(BaseModel):
    x: int
    y: int


class DragAction(BaseModel):
    type: Literal["drag"]
    path: list[Point]


class MoveAction(BaseModel):
    type: Literal["move"]
    x: int
    y: int


class WaitAction(BaseModel):
    type: Literal["wait"]
    miliseconds: Optional[int] = 0
    # No specific args, implies a default wait time


class ScreenshotAction(BaseModel):
    type: Literal["screenshot"]
    # No specific args, screenshot is handled by client


class FunctionArguments(BaseModel):
    url: str
    # Add other function arguments as needed


class FunctionAction(BaseModel):
    type: Literal["function"]
    name: str
    arguments: Optional[FunctionArguments]


class KeyAction(BaseModel):  # From Anthropic
    type: Literal["key"]
    text: str


AgentActionType = RootModel[
    Union[
        ClickAction,
        DoubleClickAction,
        TypeAction,
        KeyPressAction,
        ScrollAction,
        DragAction,
        MoveAction,
        WaitAction,
        ScreenshotAction,
        FunctionAction,
        KeyAction,
    ]
]


class AgentAction(BaseModel):
    action_type: str
    reasoning: Optional[str] = None
    action: AgentActionType
    status: Optional[str] = None
    step: Optional[list[dict[str, Any]]] = None


class AgentUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    inference_time_ms: int


class AgentResult(BaseModel):
    actions: list[AgentActionType]
    message: Optional[str]
    usage: Optional[AgentUsage]
    completed: bool


class ActionExecutionResult(BaseModel):
    success: bool
    error: Optional[str]


class AgentClientOptions(BaseModel):
    api_key: Optional[str]
    base_url: Optional[str]
    model_name: Optional[str]  # For specific models like gpt-4, claude-2
    max_tokens: Optional[int]
    temperature: Optional[float]
    wait_between_actions: Optional[int]  # in milliseconds
    # other client-specific options


class AgentHandlerOptions(BaseModel):
    model_name: str  # e.g., "openai", "anthropic"
    client_options: Optional[AgentClientOptions]
    user_provided_instructions: Optional[str]
    # Add other handler options as needed


class AgentExecuteOptions(BaseModel):
    """
    Agent execution parameters.

    Attributes:
        instruction (str): The instruction to execute.
        max_steps (Optional[int]): Maximum number of steps the agent can take. Defaults to 15.
        auto_screenshot (Optional[bool]): Whether to automatically capture screenshots after each action. False will let the agent choose when to capture screenshots. Defaults to True.
        wait_between_actions (Optional[int]): Milliseconds to wait between actions.
        context (Optional[str]): Additional context for the agent.
    """

    instruction: str
    max_steps: Optional[int] = 15
    auto_screenshot: Optional[bool] = True
    wait_between_actions: Optional[int] = 1000
    context: Optional[str] = None


class EnvState(BaseModel):
    # The screenshot in PNG format.
    screenshot: bytes
    url: str
