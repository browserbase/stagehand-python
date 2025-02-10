from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union, Type

class ActOptions(BaseModel):
    """
    Options for the 'act' command.

    Attributes:
        action (str): The action command to be executed by the AI.
        useVision: Optional[Union[bool, str]] = None
        variables: Optional[Dict[str, str]] = None
    """
    action: str = Field(..., description="The action command to be executed by the AI.")
    useVision: Optional[Union[bool, str]] = None
    variables: Optional[Dict[str, str]] = None

class ObserveOptions(BaseModel):
    """
    Options for the 'observe' command.

    Attributes:
        instruction (str): Instruction detailing what the AI should observe.
        useVision: Optional[bool] = None
        onlyVisible: Optional[bool] = None
    """
    instruction: str = Field(..., description="Instruction detailing what the AI should observe.")
    useVision: Optional[bool] = None
    onlyVisible: Optional[bool] = None

class ExtractOptions(BaseModel):
    """
    Options for the 'extract' command.

    Attributes:
        instruction (str): Instruction specifying what data to extract using AI.
        schemaDefinition (Union[Dict[str, Any], Type[BaseModel]]): A JSON schema or Pydantic model that defines the structure of the expected data.
            Note: If passing a Pydantic model, invoke its .model_json_schema() method to ensure the schema is JSON serializable.
        useTextExtract: Optional[bool] = None
    """
    instruction: str = Field(..., description="Instruction specifying what data to extract using AI.")
    # IMPORTANT: If using a Pydantic model for schemaDefinition, please call its .model_json_schema() method
    # to convert it to a JSON serializable dictionary before sending it with the extract command.
    schemaDefinition: Union[Dict[str, Any], Type[BaseModel]] = Field(
        None, 
        description="A JSON schema or Pydantic model that defines the structure of the expected data."
    )
    useTextExtract: Optional[bool] = None

    class Config:
        arbitrary_types_allowed = True 