from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union

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
        schemaDefinition (Union[Dict[str, Any], type(BaseModel)]): A JSON schema or Pydantic model that defines the structure of the expected data.
        useTextExtract: Optional[bool] = None
    """
    instruction: str = Field(..., description="Instruction specifying what data to extract using AI.")
    schemaDefinition: Union[Dict[str, Any], type(BaseModel)] = Field(
        None, 
        description="A JSON schema or Pydantic model that defines the structure of the expected data."
    )
    useTextExtract: Optional[bool] = None 