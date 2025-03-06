import os
import time
import logging
import json
from typing import Any, Dict, Optional, Callable

import requests
from playwright.sync_api import sync_playwright

from ..base import StagehandBase
from ..config import StagehandConfig
from .page import SyncStagehandPage
from ..utils import default_log_handler, convert_dict_keys_to_camel_case

logger = logging.getLogger(__name__)

class Stagehand(StagehandBase):
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
        on_log: Optional[Callable[[Dict[str, Any]], Any]] = default_log_handler,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        debug_dom: Optional[bool] = None,
        timeout_settings: Optional[float] = None,
        model_client_options: Optional[Dict[str, Any]] = None,
        stream_response: Optional[bool] = None,
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
            stream_response=stream_response,
        )
        self._client: Optional[requests.Session] = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._playwright_page = None
        self.model_client_options = model_client_options
        self.streamed_response = True  # Default to True for streamed responses

    def init(self):
        """
        Initialize the Stagehand client synchronously.
        """
        if self._initialized:
            self._log("Stagehand is already initialized; skipping init()", level=3)
            return

        self._log("Initializing Stagehand...", level=3)

        if not self._client:
            self._client = requests.Session()

        # Check server health
        self._check_server_health()

        # Create session if we don't have one
        if not self.session_id:
            self._create_session()
            self._log(f"Created new session: {self.session_id}", level=3)

        # Start Playwright and connect to remote
        self._log("Starting Playwright...", level=3)
        self._playwright = sync_playwright().start()

        connect_url = (
            f"wss://connect.browserbase.com?apiKey={self.browserbase_api_key}"
            f"&sessionId={self.session_id}"
        )
        self._log(f"Connecting to remote browser at: {connect_url}", level=3)
        self._browser = self._playwright.chromium.connect_over_cdp(connect_url)
        self._log(f"Connected to remote browser: {self._browser}", level=3)

        # Access or create a context
        existing_contexts = self._browser.contexts
        self._log(f"Existing contexts: {len(existing_contexts)}", level=3)
        if existing_contexts:
            self._context = existing_contexts[0]
        else:
            self._log("Creating a new context...", level=3)
            self._context = self._browser.new_context()

        # Access or create a page
        existing_pages = self._context.pages
        self._log(f"Existing pages: {len(existing_pages)}", level=3)
        if existing_pages:
            self._log("Using existing page", level=3)
            self._playwright_page = existing_pages[0]
        else:
            self._log("Creating a new page...", level=3)
            self._playwright_page = self._context.new_page()

        # Wrap with SyncStagehandPage
        self._log("Wrapping Playwright page in SyncStagehandPage", level=3)
        self.page = SyncStagehandPage(self._playwright_page, self)

        self._initialized = True

    def close(self):
        """
        Clean up resources synchronously.
        """
        if self._closed:
            return

        self._log("Closing resources...", level=3)

        # End the session on the server if we have a session ID
        if self.session_id:
            try:
                self._log(f"Ending session {self.session_id} on the server...", level=3)
                headers = {
                    "x-bb-api-key": self.browserbase_api_key,
                    "x-bb-project-id": self.browserbase_project_id,
                    "Content-Type": "application/json",
                }
                self._execute("end", {"sessionId": self.session_id})
                self._log(f"Session {self.session_id} ended successfully", level=3)
            except Exception as e:
                self._log(f"Error ending session: {str(e)}", level=3)

        if self._playwright:
            self._log("Stopping Playwright...", level=3)
            self._playwright.stop()
            self._playwright = None

        if self._client:
            self._log("Closing the HTTP client...", level=3)
            self._client.close()
            self._client = None

        self._closed = True

    def _check_server_health(self, timeout: int = 10):
        """
        Check server health synchronously with exponential backoff.
        """
        start = time.time()
        attempt = 0
        while True:
            try:
                headers = {
                    "x-bb-api-key": self.browserbase_api_key,
                }
                resp = self._client.get(f"{self.server_url}/healthcheck", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "ok":
                        self._log("Healthcheck passed. Server is running.", level=3)
                        return
            except Exception as e:
                self._log(f"Healthcheck error: {str(e)}", level=3)

            if time.time() - start > timeout:
                raise TimeoutError(f"Server not responding after {timeout} seconds.")

            wait_time = min(2 ** attempt * 0.5, 5.0)
            time.sleep(wait_time)
            attempt += 1

    def _create_session(self):
        """
        Create a new session synchronously.
        """
        if not self.browserbase_api_key:
            raise ValueError("browserbase_api_key is required to create a session.")
        if not self.browserbase_project_id:
            raise ValueError("browserbase_project_id is required to create a session.")
        if not self.model_api_key:
            raise ValueError("model_api_key is required to create a session.")

        payload = {
            "modelName": self.model_name,
            "domSettleTimeoutMs": self.dom_settle_timeout_ms,
            "verbose": self.verbose,
            "debugDom": self.debug_dom,
        }
        
        if self.model_client_options:
            payload["modelClientOptions"] = self.model_client_options

        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "x-model-api-key": self.model_api_key,
            "Content-Type": "application/json",
        }

        resp = self._client.post(
            f"{self.server_url}/sessions/start",
            json=payload,
            headers=headers,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to create session: {resp.text}")
        data = resp.json()
        self._log(f"Session created: {data}", level=3)
        if not data.get("success") or "sessionId" not in data.get("data", {}):
            raise RuntimeError(f"Invalid response format: {resp.text}")
        self.session_id = data["data"]["sessionId"]

    def _execute(self, method: str, payload: Dict[str, Any]) -> Any:
        """
        Execute a command synchronously.
        """
        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "x-stream-response": str(self.streamed_response).lower(),
        }
        if self.model_api_key:
            headers["x-model-api-key"] = self.model_api_key

        modified_payload = dict(payload)
        if self.model_client_options and "modelClientOptions" not in modified_payload:
            modified_payload["modelClientOptions"] = self.model_client_options
        
        # Convert snake_case keys to camelCase for the API
        modified_payload = convert_dict_keys_to_camel_case(modified_payload)
        
        url = f"{self.server_url}/sessions/{self.session_id}/{method}"
        self._log(f"\n==== EXECUTING {method.upper()} ====", level=3)
        self._log(f"URL: {url}", level=3)
        self._log(f"Payload: {modified_payload}", level=3)
        self._log(f"Headers: {headers}", level=3)
        
        try:
            if not self.streamed_response:
                # For non-streaming responses, just return the final result
                response = self._client.post(url, json=modified_payload, headers=headers)
                if response.status_code != 200:
                    error_message = response.text
                    self._log(f"Error: {error_message}", level=3)
                    return None
                
                return response.json()  # Return the raw response as the result

            # Handle streaming response
            self._log("Starting to process streaming response...", level=3)
            response = self._client.post(url, json=modified_payload, headers=headers, stream=True)
            if response.status_code != 200:
                error_message = response.text
                self._log(f"Error: {error_message}", level=3)
                return None

            for line in response.iter_lines(decode_unicode=True):
                if not line.strip():
                    continue

                try:
                    if line.startswith("data: "):
                        line = line[6:]

                    message = json.loads(line)
                    msg_type = message.get("type")

                    if msg_type == "system":
                        status = message.get("data", {}).get("status")
                        if status == "finished":
                            result = message.get("data", {}).get("result")
                            self._log(f"FINISHED WITH RESULT: {result}", level=3)
                            return result
                    elif msg_type == "log":
                        log_msg = message.get("data", {}).get("message", "")
                        self._log(log_msg, level=3)
                        if self.on_log:
                            # For sync implementation, we just log the message directly
                            self._log(f"Log message: {log_msg}", level=3)
                    else:
                        self._log(f"Unknown message type: {msg_type}", level=3)
                        if self.on_log:
                            self._log(f"Unknown message: {message}", level=3)

                except json.JSONDecodeError:
                    self._log(f"Could not parse line as JSON: {line}", level=3)
                    continue
        except Exception as e:
            self._log(f"EXCEPTION IN _EXECUTE: {str(e)}")
            raise

        self._log("==== ERROR: No 'finished' message received ====", level=3)
        raise RuntimeError("Server connection closed without sending 'finished' message")