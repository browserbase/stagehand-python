from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union
from .config import StagehandConfig
from .page import StagehandPage

class BaseStagehand(ABC):
    """
    Base class for Stagehand clients that defines the common interface
    and shared functionality for both sync and async implementations.
    """
    
    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[Callable[[Dict[str, Any]], Union[None, Any]]] = None,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        debug_dom: Optional[bool] = None,
        timeout_settings: Optional[Any] = None,
        model_client_options: Optional[Dict[str, Any]] = None,
    ):
        self.config = config or StagehandConfig()
        self.server_url = server_url or self.config.server_url
        self.session_id = session_id
        self.browserbase_api_key = browserbase_api_key or self.config.browserbase_api_key
        self.browserbase_project_id = browserbase_project_id or self.config.browserbase_project_id
        self.model_api_key = model_api_key or self.config.model_api_key
        self.on_log = on_log
        self.verbose = verbose
        self.model_name = model_name or self.config.model_name
        self.dom_settle_timeout_ms = dom_settle_timeout_ms or self.config.dom_settle_timeout_ms
        self.debug_dom = debug_dom if debug_dom is not None else self.config.debug_dom
        self.timeout_settings = timeout_settings or self.config.timeout_settings
        self.model_client_options = model_client_options or self.config.model_client_options

    @abstractmethod
    def init(self):
        """Initialize the client and create a session if needed."""
        pass

    @abstractmethod
    def close(self):
        """Close the client and cleanup resources."""
        pass

    @abstractmethod
    def _check_server_health(self, timeout: int = 10):
        """Check if the server is healthy and responding."""
        pass

    @abstractmethod
    def _create_session(self):
        """Create a new session with the server."""
        pass

    @abstractmethod
    def _execute(self, method: str, payload: Dict[str, Any]) -> Any:
        """Execute a command on the server."""
        pass

    @abstractmethod
    def _handle_log(self, msg: Dict[str, Any]):
        """Handle log messages from the server."""
        pass

    def _log(self, message: str, level: int = 1):
        """Log a message if verbose level is sufficient."""
        if self.verbose >= level:
            print(f"[Stagehand] {message}") 