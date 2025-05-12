from dataclasses import dataclass
from enum import Enum


class StagehandFunctionName(str, Enum):
    """Function names for tracking metrics."""

    ACT = "act"
    EXTRACT = "extract"
    OBSERVE = "observe"
    AGENT = "agent"


@dataclass
class StagehandMetrics:
    """Metrics for token usage and inference time across different functions."""

    act_prompt_tokens: int = 0
    act_completion_tokens: int = 0
    act_inference_time_ms: int = 0

    extract_prompt_tokens: int = 0
    extract_completion_tokens: int = 0
    extract_inference_time_ms: int = 0

    observe_prompt_tokens: int = 0
    observe_completion_tokens: int = 0
    observe_inference_time_ms: int = 0

    agent_prompt_tokens: int = 0
    agent_completion_tokens: int = 0
    agent_inference_time_ms: int = 0

    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_inference_time_ms: int = 0
