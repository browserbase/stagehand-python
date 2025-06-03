from enum import Enum
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer

# Default extraction schema that matches the TypeScript version
DEFAULT_EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {"extraction": {"type": "string"}},
    "required": ["extraction"],
}


# TODO: Remove this
class AvailableModel(str, Enum):
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    CLAUDE_3_5_SONNET_LATEST = "claude-3-5-sonnet-latest"
    CLAUDE_3_7_SONNET_LATEST = "claude-3-7-sonnet-latest"
    COMPUTER_USE_PREVIEW = "computer-use-preview"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"


class StagehandBaseModel(BaseModel):
    """Base model for all Stagehand models with camelCase conversion support"""

    model_config = ConfigDict(
        populate_by_name=True,  # Allow accessing fields by their Python name
        alias_generator=lambda field_name: "".join(
            [field_name.split("_")[0]]
            + [word.capitalize() for word in field_name.split("_")[1:]]
        ),  # snake_case to camelCase
    )


class ActOptions(StagehandBaseModel):
    """
    Options for the 'act' command.

    Attributes:
        action (str): The action command to be executed by the AI.
        variables (Optional[dict[str, str]]): Key-value pairs for variable substitution.
        model_name (Optional[str]): The model to use for processing.
        slow_dom_based_act (Optional[bool]): Whether to use DOM-based action execution.
        dom_settle_timeout_ms (Optional[int]): Additional time for DOM to settle after an action.
        timeout_ms (Optional[int]): Timeout for the action in milliseconds.
    """

    action: str = Field(..., description="The action command to be executed by the AI.")
    variables: Optional[dict[str, str]] = None
    model_name: Optional[str] = None
    slow_dom_based_act: Optional[bool] = None
    dom_settle_timeout_ms: Optional[int] = None
    timeout_ms: Optional[int] = None
    model_client_options: Optional[dict[str, Any]] = None


class ActResult(StagehandBaseModel):
    """
    Result of the 'act' command.

    Attributes:
        success (bool): Whether the action was successful.
        message (str): Message from the AI about the action.
        action (str): The action command that was executed.
    """

    success: bool = Field(..., description="Whether the action was successful.")
    message: str = Field(..., description="Message from the AI about the action.")
    action: str = Field(..., description="The action command that was executed.")


class ExtractOptions(StagehandBaseModel):
    """
    Options for the 'extract' command.

    Attributes:
        instruction (str): Instruction specifying what data to extract using AI.
        model_name (Optional[str]): The model to use for processing.
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
        default=DEFAULT_EXTRACT_SCHEMA,
        description="A JSON schema or Pydantic model that defines the structure of the expected data.",
    )
    use_text_extract: Optional[bool] = None
    dom_settle_timeout_ms: Optional[int] = None
    model_client_options: Optional[dict[Any, Any]] = None

    @field_serializer("schema_definition")
    def serialize_schema_definition(
        self, schema_definition: Union[dict[str, Any], type[BaseModel]]
    ) -> dict[str, Any]:
        """Serialize schema_definition to a JSON schema if it's a Pydantic model"""
        if isinstance(schema_definition, type) and issubclass(
            schema_definition, BaseModel
        ):
            # Get the JSON schema using default ref_template ('#/$defs/{model}')
            schema = schema_definition.model_json_schema()

            defs_key = "$defs"
            if defs_key not in schema:
                defs_key = "definitions"
                if defs_key not in schema:
                    return schema

            definitions = schema.get(defs_key, {})
            if definitions:
                self._resolve_references(schema, definitions, f"#/{defs_key}/")
                schema.pop(defs_key, None)

            return schema

        elif isinstance(schema_definition, dict):
            return schema_definition

        raise TypeError("schema_definition must be a Pydantic model or a dict")

    def _resolve_references(self, obj: Any, definitions: dict, ref_prefix: str) -> None:
        """Recursively resolve $ref references in a schema using definitions."""
        if isinstance(obj, dict):
            if "$ref" in obj and obj["$ref"].startswith(ref_prefix):
                ref_name = obj["$ref"][len(ref_prefix) :]  # Get name after prefix
                if ref_name in definitions:
                    original_keys = {k: v for k, v in obj.items() if k != "$ref"}
                    resolved_definition = definitions[ref_name].copy()  # Use a copy
                    self._resolve_references(
                        resolved_definition, definitions, ref_prefix
                    )

                    obj.clear()
                    obj.update(resolved_definition)
                    obj.update(original_keys)
            else:
                # Recursively process all values in the dictionary
                for _, value in obj.items():
                    self._resolve_references(value, definitions, ref_prefix)

        elif isinstance(obj, list):
            # Process all items in the list
            for item in obj:
                self._resolve_references(item, definitions, ref_prefix)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ExtractResult(StagehandBaseModel):
    """
    Result of the 'extract' command.

    This is a generic model to hold extraction results of different types.
    The actual fields will depend on the schema provided in ExtractOptions.
    """

    # This class is intentionally left without fields so it can accept
    # any fields from the extraction result based on the schema

    model_config = ConfigDict(extra="allow")  # Allow any extra fields

    def __getitem__(self, key):
        """
        Enable dictionary-style access to attributes.
        This allows usage like result["selector"] in addition to result.selector
        """
        return getattr(self, key)


class ObserveOptions(StagehandBaseModel):
    """
    Options for the 'observe' command.

    Attributes:
        instruction (str): Instruction detailing what the AI should observe.
        model_name (Optional[str]): The model to use for processing.
        return_action (Optional[bool]): Whether to include action information in the result.
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


class ObserveResult(StagehandBaseModel):
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


class AgentProvider(str, Enum):
    """Supported agent providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AgentConfig(StagehandBaseModel):
    """
    Configuration for agent execution.

    Attributes:
        provider (Optional[AgentProvider]): The provider to use (openai or anthropic).
        model (Optional[str]): The model name to use.
        instructions (Optional[str]): Custom instructions for the agent.
        options (Optional[dict[str, Any]]): Additional provider-specific options.
    """

    provider: Optional[AgentProvider] = None
    model: Optional[str] = None
    instructions: Optional[str] = None
    options: Optional[dict[str, Any]] = None


class AgentExecuteOptions(StagehandBaseModel):
    """
    Options for agent execution.

    Attributes:
        instruction (str): The task instruction for the agent.
        max_steps (Optional[int]): Maximum number of steps the agent can take.
        auto_screenshot (Optional[bool]): Whether to automatically take screenshots between steps.
        wait_between_actions (Optional[int]): Milliseconds to wait between actions.
        context (Optional[str]): Additional context for the agent.
    """

    instruction: str = Field(..., description="The task instruction for the agent.")
    max_steps: Optional[int] = None
    auto_screenshot: Optional[bool] = None
    wait_between_actions: Optional[int] = None
    context: Optional[str] = None


class AgentExecuteResult(StagehandBaseModel):
    """
    Result of agent execution.

    Attributes:
        success (bool): Whether the execution was successful.
        actions (Optional[list[dict[str, Any]]]): Actions taken by the agent.
        message (Optional[str]): Final result message from the agent.
        completed (bool): Whether the agent has completed its task.
    """

    success: bool = Field(..., description="Whether the execution was successful.")
    actions: Optional[list[dict[str, Any]]] = None
    message: Optional[str] = None
    completed: bool = Field(
        False, description="Whether the agent has completed its task."
    )
