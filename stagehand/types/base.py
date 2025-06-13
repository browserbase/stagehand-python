from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

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


class AgentProvider(str, Enum):
    """Supported agent providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic" 