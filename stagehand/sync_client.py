import json
import logging
from typing import Any, Callable, Dict, Optional

import httpx
from playwright.sync_api import sync_playwright

from .base import BaseStagehand
from .page import StagehandPage
from .utils import convert_dict_keys_to_camel_case

logger = logging.getLogger(__name__)

def default_sync_log_handler(msg: Dict[str, Any]) -> None:
    """Default synchronous log handler."""
    logger.info(json.dumps(msg, indent=2))

class SyncStagehand(BaseStagehand):
    """
    Synchronous implementation of the Stagehand client.
    """
    
    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[Callable[[Dict[str, Any]], None]] = default_sync_log_handler,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        debug_dom: Optional[bool] = None,
        httpx_client: Optional[httpx.Client] = None,
        timeout_settings: Optional[httpx.Timeout] = None,
        model_client_options: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            config=config,
            server_url=server_url,
            session_id=session_id,
            browserbase_api_key=browserbase_api_key,
            browserbase_project_id=browserbase_project_id,
            model_api_key=model_api_key,
            on_log=on_log,
            verbose=verbose,
            model_name=model_name,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
            debug_dom=debug_dom,
            timeout_settings=timeout_settings,
            model_client_options=model_client_options,
        )
        self.httpx_client = httpx_client
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        """Context manager entry."""
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def init(self):
        """Initialize the client and create a session if needed."""
        if not self.httpx_client:
            self.httpx_client = httpx.Client(timeout=self.timeout_settings)

        self._check_server_health()
        
        if not self.session_id:
            self._create_session()

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def close(self):
        """Close the client and cleanup resources."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        if self.httpx_client:
            self.httpx_client.close()

    def _check_server_health(self, timeout: int = 10):
        """Check if the server is healthy and responding."""
        try:
            response = self.httpx_client.get(f"{self.server_url}/health")
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Server health check failed: {str(e)}")

    def _create_session(self):
        """Create a new session with the server."""
        payload = {
            "browserbaseApiKey": self.browserbase_api_key,
            "browserbaseProjectId": self.browserbase_project_id,
            "modelApiKey": self.model_api_key,
            "modelName": self.model_name,
            "domSettleTimeoutMs": self.dom_settle_timeout_ms,
            "debugDom": self.debug_dom,
            "modelClientOptions": self.model_client_options,
        }
        
        response = self.httpx_client.post(
            f"{self.server_url}/sessions",
            json=convert_dict_keys_to_camel_case(payload)
        )
        response.raise_for_status()
        self.session_id = response.json()["sessionId"]

    def _execute(self, method: str, payload: Dict[str, Any]) -> Any:
        """Execute a command on the server."""
        response = self.httpx_client.post(
            f"{self.server_url}/sessions/{self.session_id}/execute",
            json={"method": method, "payload": convert_dict_keys_to_camel_case(payload)}
        )
        response.raise_for_status()
        return response.json()

    def _handle_log(self, msg: Dict[str, Any]):
        """Handle log messages from the server."""
        if self.on_log:
            self.on_log(msg) 