from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union
from playwright.async_api import Page

from .config import StagehandConfig
from .page import StagehandPage
from .utils import default_log_handler
import os
import time
import logging

logger = logging.getLogger(__name__)


class StagehandBase(ABC):
    """
    Base class for Stagehand client implementations.
    Defines the common interface and functionality for both sync and async versions.
    """
    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[Callable[[Dict[str, Any]], Any]] = default_log_handler,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        debug_dom: Optional[bool] = None,
        timeout_settings: Optional[float] = None,
        stream_response: Optional[bool] = None,
        model_client_options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Stagehand client with common configuration.
        """
        self.server_url = server_url or os.getenv("STAGEHAND_SERVER_URL")

        if config:
            self.browserbase_api_key = config.api_key or browserbase_api_key or os.getenv("BROWSERBASE_API_KEY")
            self.browserbase_project_id = config.project_id or browserbase_project_id or os.getenv("BROWSERBASE_PROJECT_ID")
            self.session_id = config.browserbase_session_id or session_id
            self.model_name = config.model_name or model_name
            self.dom_settle_timeout_ms = config.dom_settle_timeout_ms or dom_settle_timeout_ms
            self.debug_dom = config.debug_dom if config.debug_dom is not None else debug_dom
        else:
            self.browserbase_api_key = browserbase_api_key or os.getenv("BROWSERBASE_API_KEY")
            self.browserbase_project_id = browserbase_project_id or os.getenv("BROWSERBASE_PROJECT_ID")
            self.session_id = session_id
            self.model_name = model_name
            self.dom_settle_timeout_ms = dom_settle_timeout_ms
            self.debug_dom = debug_dom

        # Handle model-related settings directly
        self.model_api_key = model_api_key or os.getenv("MODEL_API_KEY")
        self.model_client_options = model_client_options or {}
        if self.model_api_key and "apiKey" not in self.model_client_options:
            self.model_client_options["apiKey"] = self.model_api_key

        # Handle streaming response setting directly
        self.streamed_response = stream_response if stream_response is not None else True

        self.on_log = on_log
        self.verbose = verbose
        self.timeout_settings = timeout_settings or 180.0

        self._initialized = False
        self._closed = False
        self.page: Optional[StagehandPage] = None

        # Validate essential fields if session_id was provided
        if self.session_id:
            if not self.browserbase_api_key:
                raise ValueError("browserbase_api_key is required (or set BROWSERBASE_API_KEY in env).")
            if not self.browserbase_project_id:
                raise ValueError("browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env).")

    @abstractmethod
    def init(self):
        """
        Initialize the Stagehand client.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Clean up resources.
        Must be implemented by subclasses.
        """
        pass

    def _log(self, message: str, level: int = 1):
        """
        Internal logging helper that maps verbosity to logging levels.
        """
        if self.verbose >= level:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            formatted_msg = f"{timestamp}::[stagehand] {message}"
            if level == 1:
                logger.info(formatted_msg)
            elif level == 2:
                logger.warning(formatted_msg)
            else:
                logger.debug(formatted_msg) 