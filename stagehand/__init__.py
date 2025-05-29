from .agent import Agent
from .async_client import Stagehand
from .sync_client import Stagehand as SyncStagehand
from .config import StagehandConfig
from .handlers.observe_handler import ObserveHandler
from .metrics import StagehandFunctionName, StagehandMetrics
from .page import StagehandPage
from .schemas import (
    ActOptions,
    ActResult,
    AgentConfig,
    AgentExecuteOptions,
    AgentExecuteResult,
    AgentProvider,
    AvailableModel,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
)
from .utils import configure_logging

__version__ = "0.0.1" #for pypi "stagehand"

__all__ = [
    "Stagehand",         # Async client (default)
    "SyncStagehand",     # Sync client
    "StagehandConfig",
    "StagehandPage",
    "Agent",
    "configure_logging",
    "ActOptions",
    "ActResult",
    "AvailableModel",
    "ExtractOptions",
    "ExtractResult",
    "ObserveOptions",
    "ObserveResult",
    "AgentConfig",
    "AgentExecuteOptions",
    "AgentExecuteResult",
    "AgentProvider",
    "ObserveHandler",
    "StagehandFunctionName",
    "StagehandMetrics",
]
