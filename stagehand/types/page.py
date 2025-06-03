from typing import Any, Optional, Union

from pydantic import BaseModel, Field


# Ignore linting error for this class name since it's used as a constant
# ruff: noqa: N801
class DefaultExtractSchema(BaseModel):
    extraction: str


class ObserveElementSchema(BaseModel):
    element_id: int
    description: str = Field(
        ..., description="A description of the observed element and its purpose."
    )
    method: str
    arguments: list[str]


class ObserveInferenceSchema(BaseModel):
    elements: list[ObserveElementSchema]


class MetadataSchema(BaseModel):
    completed: bool
    progress: str


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


class ExtractOptions(BaseModel):
    """
    Options for the 'extract' command.

    Attributes:
        instruction (str): Instruction specifying what data to extract using AI.
        model_name (Optional[AvailableModel]): The model to use for processing.
        selector (Optional[str]): CSS selector to limit extraction to.
        schema_definition (Union[dict[str, Any], type[BaseModel]]): A JSON schema or Pydantic model that defines the structure of the expected data.
            Note: If passing a Pydantic model, invoke its .model_json_schema() method to ensure the schema is JSON serializable.
        use_text_extract (Optional[bool]): Whether to use text-based extraction.
        dom_settle_timeout_ms (Optional[int]): Additional time for DOM to settle before extraction.
    """

    instruction: str = Field(
        ..., description="Instruction specifying what data to extract using AI."
    )
    model_name: Optional[str] = None
    selector: Optional[str] = None
    # IMPORTANT: If using a Pydantic model for schema_definition, please call its .model_json_schema() method
    # to convert it to a JSON serializable dictionary before sending it with the extract command.
    schema_definition: Union[dict[str, Any], type[BaseModel]] = Field(
        default=DefaultExtractSchema,
        description="A JSON schema or Pydantic model that defines the structure of the expected data.",
    )
    use_text_extract: Optional[bool] = None
    dom_settle_timeout_ms: Optional[int] = None
    model_client_options: Optional[dict[Any, Any]] = None


class ExtractResult(BaseModel):
    """
    Result of the 'extract' command.

    The 'data' field will contain the Pydantic model instance if a schema was provided
    and validation was successful, otherwise it may contain the raw extracted dictionary.
    """

    data: Optional[Any] = None

    def __getitem__(self, key):
        """
        Enable dictionary-style access to attributes.
        This allows usage like result["selector"] in addition to result.selector
        """
        return getattr(self, key)
