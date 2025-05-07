from typing import Any, Optional

from pydantic import BaseModel, Field


class ObserveElementSchema(BaseModel):
    element_id: int
    description: str = Field(
        ..., description="A description of the observed element and its purpose."
    )
    method: str
    arguments: list[str]


class ObserveInferenceSchema(BaseModel):
    elements: list[ObserveElementSchema]


class ActOptions(BaseModel):
    """
    Options for the 'act' command.

    Attributes:
        action (str): The action command to be executed by the AI.
        variables (Optional[dict[str, str]]): Key-value pairs for variable substitution.
        model_name (Optional[str]): The model to use for processing.
        dom_settle_timeout_ms (Optional[int]): Additional time for DOM to settle after an action.
        timeout_ms (Optional[int]): Timeout for the action in milliseconds.
    """

    action: str = Field(..., description="The action command to be executed by the AI.")
    variables: Optional[dict[str, str]] = None
    model_name: Optional[str] = None
    dom_settle_timeout_ms: Optional[int] = None
    timeout_ms: Optional[int] = None
    model_client_options: Optional[dict[str, Any]] = None


class ActResult(BaseModel):
    """
    Result of the 'act' command.

    Attributes:
        success (bool): Whether the action was successful.
        message (str): Message from the AI about the action.
        action (str): The action command that was executed.
    """

    success: bool = Field(..., description="Whether the action was successful.")
    message: str = Field(..., description="Message from the AI about the action.")
    action: str = Field(description="The action command that was executed.")


class ObserveOptions(BaseModel):
    """
    Options for the 'observe' command.

    Attributes:
        instruction (str): Instruction detailing what the AI should observe.
        model_name (Optional[AvailableModel]): The model to use for processing.
        draw_overlay (Optional[bool]): Whether to draw an overlay on observed elements.
        dom_settle_timeout_ms (Optional[int]): Additional time for DOM to settle before observation.
    """

    instruction: str = Field(
        ..., description="Instruction detailing what the AI should observe."
    )
    model_name: Optional[str] = None
    draw_overlay: Optional[bool] = None
    dom_settle_timeout_ms: Optional[int] = None
    model_client_options: Optional[dict[str, Any]] = None


class ObserveResult(BaseModel):
    """
    Result of the 'observe' command.

    Attributes:
        selector (str): The selector of the observed element.
        description (str): The description of the observed element.
        backend_node_id (Optional[int]): The backend node ID.
        method (Optional[str]): The method to execute.
        arguments (Optional[list[str]]): The arguments for the method.
    """

    selector: str = Field(..., description="The selector of the observed element.")
    description: str = Field(
        ..., description="The description of the observed element."
    )
    backend_node_id: Optional[int] = None
    method: Optional[str] = None
    arguments: Optional[list[str]] = None

    def __getitem__(self, key):
        """
        Enable dictionary-style access to attributes.
        This allows usage like result["selector"] in addition to result.selector
        """
        return getattr(self, key)
