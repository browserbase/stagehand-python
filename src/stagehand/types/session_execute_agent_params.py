# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = ["SessionExecuteAgentParams", "AgentConfig", "AgentConfigModel", "ExecuteOptions"]


class SessionExecuteAgentParams(TypedDict, total=False):
    agent_config: Required[Annotated[AgentConfig, PropertyInfo(alias="agentConfig")]]

    execute_options: Required[Annotated[ExecuteOptions, PropertyInfo(alias="executeOptions")]]

    frame_id: Annotated[str, PropertyInfo(alias="frameId")]

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]


AgentConfigModel: TypeAlias = Union[str, ModelConfigParam]


class AgentConfig(TypedDict, total=False):
    cua: bool
    """Enable Computer Use Agent mode"""

    model: AgentConfigModel

    provider: Literal["openai", "anthropic", "google"]

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]


class ExecuteOptions(TypedDict, total=False):
    instruction: Required[str]
    """Task for the agent to complete"""

    highlight_cursor: Annotated[bool, PropertyInfo(alias="highlightCursor")]
    """Visually highlight the cursor during actions"""

    max_steps: Annotated[int, PropertyInfo(alias="maxSteps")]
    """Maximum number of steps the agent can take"""
