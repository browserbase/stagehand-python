import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Any, Callable, Optional

from .config import StagehandConfig
from .page import StagehandPage
from .utils import default_log_handler, make_serializable

logger = logging.getLogger(__name__)


class StagehandBase(ABC):
    """
    Base class for Stagehand client implementations.
    Defines the common interface and functionality for both sync and async versions.
    """

    def __init__(
        self,
        config: Optional["StagehandConfig"] = None,
        server_url: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[
            Callable[[dict[str, Any]], Awaitable[None]]
        ] = default_log_handler,
        timeout_settings: Optional[Any] = None,
        stream_response: Optional[bool] = None,
        model_client_options: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        """
        Initialize the Stagehand client with configuration.

        Configuration can be provided via a StagehandConfig object, keyword arguments,
        or environment variables. Keyword arguments override values in the config object,
        and environment variables are used as fallbacks.

        Args:
            config (Optional[StagehandConfig]): Configuration object.
            server_url (Optional[str]): URL of the Stagehand server. Falls back to STAGEHAND_API_URL env var.
            model_api_key (Optional[str]): Model provider API key. Falls back to MODEL_API_KEY env var.
            on_log (Optional[Callable]): Callback for log events.
            timeout_settings (Optional[Any]): Request timeout in seconds. Defaults to 180.0.
            stream_response (Optional[bool]): Whether to stream responses. Defaults to True.
            model_client_options (Optional[dict]): Options for the model client.
            **kwargs: Additional configuration options corresponding to StagehandConfig fields.
        """
        # Initialize config from provided object or kwargs
        if config:
            # Create a dictionary from the config object, excluding unset fields
            config_dict = config.model_dump(exclude_unset=True)
            # Update with kwargs, giving kwargs precedence
            config_dict.update(kwargs)
            # Create the final config object
            final_config = StagehandConfig(**config_dict)
        else:
            final_config = StagehandConfig(**kwargs)

        # Assign validated config values to self
        self.config = final_config
        self.session_id = self.config.browserbase_session_id
        self.model_name = self.config.model_name
        self.dom_settle_timeout_ms = self.config.dom_settle_timeout_ms
        self.self_heal = self.config.self_heal
        self.wait_for_captcha_solves = self.config.wait_for_captcha_solves
        self.system_prompt = self.config.system_prompt
        self.browserbase_session_create_params = make_serializable(
            self.config.browserbase_session_create_params
        )
        self.enable_caching = self.config.enable_caching
        self.verbose = self.config.verbose

        # Handle non-config parameters and environment variable fallbacks
        self.server_url = server_url or os.getenv("STAGEHAND_API_URL")
        self.browserbase_api_key = self.config.api_key or os.getenv(
            "BROWSERBASE_API_KEY"
        )
        self.browserbase_project_id = self.config.project_id or os.getenv(
            "BROWSERBASE_PROJECT_ID"
        )
        self.model_api_key = model_api_key or os.getenv("MODEL_API_KEY")

        # Handle other direct parameters
        self.on_log = on_log
        self.timeout_settings = timeout_settings or 180.0
        self.model_client_options = model_client_options or {}
        if self.model_api_key and "apiKey" not in self.model_client_options:
            self.model_client_options["apiKey"] = self.model_api_key
        self.streamed_response = (
            stream_response if stream_response is not None else True
        )

        self._initialized = False
        self._closed = False
        self.page: Optional[StagehandPage] = None

        # Validate essential fields if session_id was provided or directly set
        if self.session_id:
            if not self.browserbase_api_key:
                raise ValueError(
                    "browserbase_api_key is required (or set BROWSERBASE_API_KEY in env)."
                )
            if not self.browserbase_project_id:
                raise ValueError(
                    "browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env)."
                )

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
