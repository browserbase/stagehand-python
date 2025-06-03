"""Stagehand - Browser automation with AI"""

from .agent import Agent
from .client import Stagehand
from .config import StagehandConfig
from .handlers.observe_handler import ObserveHandler
from .llm import LLMClient
from .logging import LogConfig, configure_logging, get_logger
from .metrics import StagehandFunctionName, StagehandMetrics
from .page import StagehandPage
from .schemas import (
    ActOptions,
    ActResult,
    AgentConfig,
    AgentExecuteOptions,
    AgentExecuteResult,
    AgentProvider,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
)

__version__ = "0.1.0"

__all__ = [
    "Stagehand",
    "StagehandConfig",
    "StagehandPage",
    "Agent",
    "AgentConfig",
    "AgentExecuteOptions",
    "AgentExecuteResult",
    "AgentProvider",
    "ActOptions",
    "ActResult",
    "ExtractOptions",
    "ExtractResult",
    "ObserveOptions",
    "ObserveResult",
    "ObserveHandler",
    "LLMClient",
    "configure_logging",
    "StagehandFunctionName",
    "StagehandMetrics",
    "LogConfig",
    "get_logger",
]
