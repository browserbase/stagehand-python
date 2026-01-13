# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .model_config_param import ModelConfigParam

__all__ = [
    "SessionExecuteParamsBase",
    "AgentConfig",
    "ExecuteOptions",
    "SessionExecuteParamsNonStreaming",
    "SessionExecuteParamsStreaming",
]


class SessionExecuteParamsBase(TypedDict, total=False):
    agent_config: Required[Annotated[AgentConfig, PropertyInfo(alias="agentConfig")]]

    execute_options: Required[Annotated[ExecuteOptions, PropertyInfo(alias="executeOptions")]]

    frame_id: Annotated[str, PropertyInfo(alias="frameId")]
    """Target frame ID for the agent"""

    x_sent_at: Annotated[Union[str, datetime], PropertyInfo(alias="x-sent-at", format="iso8601")]
    """ISO timestamp when request was sent"""

    x_stream_response: Annotated[Literal["true", "false"], PropertyInfo(alias="x-stream-response")]
    """Whether to stream the response via SSE"""


class AgentConfig(TypedDict, total=False):
    cua: bool
    """Enable Computer Use Agent mode"""

    model: ModelConfigParam
    """
    Model name string with provider prefix (e.g., 'openai/gpt-5-nano',
    'anthropic/claude-4.5-opus')
    """

    provider: Literal["openai", "anthropic", "google", "microsoft"]
    """AI provider for the agent (legacy, use model: openai/gpt-5-nano instead)"""

    system_prompt: Annotated[str, PropertyInfo(alias="systemPrompt")]
    """Custom system prompt for the agent"""


class ExecuteOptions(TypedDict, total=False):
    instruction: Required[str]
    """Natural language instruction for the agent"""

    highlight_cursor: Annotated[bool, PropertyInfo(alias="highlightCursor")]
    """Whether to visually highlight the cursor during execution"""

    max_steps: Annotated[float, PropertyInfo(alias="maxSteps")]
    """Maximum number of steps the agent can take"""


class SessionExecuteParamsNonStreaming(SessionExecuteParamsBase, total=False):
    stream_response: Annotated[Literal[False], PropertyInfo(alias="streamResponse")]
    """Whether to stream the response via SSE"""


class SessionExecuteParamsStreaming(SessionExecuteParamsBase):
    stream_response: Required[Annotated[Literal[True], PropertyInfo(alias="streamResponse")]]
    """Whether to stream the response via SSE"""


SessionExecuteParams = Union[SessionExecuteParamsNonStreaming, SessionExecuteParamsStreaming]
