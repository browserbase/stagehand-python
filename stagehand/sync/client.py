import json
import logging
from typing import Any, Callable, Optional

import requests
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

from ..base import StagehandBase
from ..config import StagehandConfig
from ..schemas import AgentConfig
from ..utils import (
    StagehandLogger,
    convert_dict_keys_to_camel_case,
    default_log_handler,
)
from .agent import SyncAgent
from .context import SyncStagehandContext
from .page import SyncStagehandPage

logger = logging.getLogger(__name__)


class Stagehand(StagehandBase):
    """
    Synchronous implementation of the Stagehand client.
    """

    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        server_url: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[Callable[[dict[str, Any]], Any]] = default_log_handler,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        timeout_settings: Optional[float] = None,
        model_client_options: Optional[dict[str, Any]] = None,
        stream_response: Optional[bool] = None,
        use_rich_logging: bool = True,
        **kwargs: Any,
    ):
        super().__init__(
            config=config,
            server_url=server_url,
            model_api_key=model_api_key,
            on_log=None,
            verbose=verbose,
            model_name=model_name,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
            timeout_settings=timeout_settings,
            stream_response=stream_response,
            model_client_options=model_client_options,
            **kwargs,
        )

        # Initialize the centralized logger with the specified verbosity
        self.logger = StagehandLogger(
            verbose=self.verbose, external_logger=on_log, use_rich=use_rich_logging
        )

        self._client: Optional[requests.Session] = None
        self._playwright = None
        self._browser = None
        self._context = None
        self._playwright_page = None
        self.page: Optional[SyncStagehandPage] = None
        # self.context: Optional[SyncStagehandContext] = None
        self.model_client_options = model_client_options
        self.streamed_response = True  # Default to True for streamed responses

        self._initialized = False
        self._closed = False

        if self.session_id:
            if not self.browserbase_api_key:
                raise ValueError(
                    "browserbase_api_key is required (or set BROWSERBASE_API_KEY in env)."
                )
            if not self.browserbase_project_id:
                raise ValueError(
                    "browserbase_project_id is required (or set BROWSERBASE_PROJECT_ID in env)."
                )

    def __enter__(self):
        self.logger.debug("Entering StagehandSync context manager (__enter__)...")
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug("Exiting StagehandSync context manager (__exit__)...")
        self.close()

    def init(self):
        """
        Initialize the Stagehand client synchronously.
        """
        if self._initialized:
            self.logger.debug("Stagehand is already initialized; skipping init()")
            return

        self.logger.debug("Initializing Stagehand...")

        if not self._client:
            self._client = requests.Session()

        # Create session if we don't have one
        if not self.session_id:
            self._create_session()
            self.logger.debug(f"Created new session: {self.session_id}")

        # Start Playwright and connect to remote
        self.logger.debug("Starting Playwright...")
        self._playwright = sync_playwright().start()

        bb = Browserbase(api_key=self.browserbase_api_key)
        try:
            session = bb.sessions.retrieve(self.session_id)
            connect_url = session.connectUrl
        except Exception as e:
            self.logger.error(f"Error retrieving session: {str(e)}")
            raise
        connect_url = session.connectUrl

        self.logger.debug(f"Connecting to remote browser at: {connect_url}")
        self._browser = self._playwright.chromium.connect_over_cdp(connect_url)
        self.logger.debug(f"Connected to remote browser: {self._browser}")

        # Access or create a context
        existing_contexts = self._browser.contexts
        self.logger.debug(f"Existing contexts: {len(existing_contexts)}")
        if existing_contexts:
            self._context = existing_contexts[0]
        else:
            self.logger.debug("Creating a new context...")
            self._context = self._browser.new_context()

        # Wrap the context with StagehandContext to ensure custom script injection
        self.stagehand_context = SyncStagehandContext.init(self._context, self)

        # Use context to get or create a page
        existing_pages = self._context.pages
        self.logger.debug(f"Existing pages: {len(existing_pages)}")
        if existing_pages:
            self.logger.debug("Using existing page via StagehandContext")
            self._playwright_page = existing_pages[0]
            self.page = self.stagehand_context.get_stagehand_page(self._playwright_page)
        else:
            self.logger.debug("Creating a new page via StagehandContext")
            self.page = self.stagehand_context.new_page()
            self._playwright_page = self.page.page

        self._initialized = True

    def agent(self, agent_config: AgentConfig) -> SyncAgent:
        """
        Create a synchronous agent instance configured with the provided options.

        Args:
            agent_config (AgentConfig): Configuration for the agent instance.
                                          Provider must be specified or inferrable from the model.

        Returns:
            AgentSync: A configured synchronous Agent instance ready to execute tasks.
        """
        if not self._initialized:
            raise RuntimeError(
                "StagehandSync must be initialized with init() before creating an agent."
            )

        self.logger.debug(f"Creating Agent instance with config: {agent_config}")
        # Pass the required config directly to the Agent constructor
        return SyncAgent(self, agent_config=agent_config)

    def close(self):
        """
        Clean up resources synchronously.
        """
        if self._closed:
            return

        self.logger.debug("Closing resources...")

        # End the session on the server if we have a session ID
        if self.session_id:
            try:
                self.logger.debug(f"Ending session {self.session_id} on the server...")
                self._execute("end", {"sessionId": self.session_id})
                self.logger.debug(f"Session {self.session_id} ended successfully")
            except Exception as e:
                self.logger.error(f"Error ending session: {str(e)}")

        if self._playwright:
            self.logger.debug("Stopping Playwright...")
            self._playwright.stop()
            self._playwright = None

        if self._client:
            self.logger.debug("Closing the HTTP client...")
            self._client.close()
            self._client = None

        self._closed = True

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
            "browserbaseSessionCreateParams": {
                "browserSettings": {
                    "blockAds": True,
                    "viewport": {
                        "width": 1024,
                        "height": 768,
                    },
                },
            },
        }

        # Add the new parameters if they have values
        if hasattr(self, "self_heal") and self.self_heal is not None:
            payload["selfHeal"] = self.self_heal

        if (
            hasattr(self, "wait_for_captcha_solves")
            and self.wait_for_captcha_solves is not None
        ):
            payload["waitForCaptchaSolves"] = self.wait_for_captcha_solves

        if hasattr(self, "system_prompt") and self.system_prompt:
            payload["systemPrompt"] = self.system_prompt

        if hasattr(self, "model_client_options") and self.model_client_options:
            payload["modelClientOptions"] = self.model_client_options

        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "x-model-api-key": self.model_api_key,
            "Content-Type": "application/json",
            "x-language": "python",
        }

        resp = self._client.post(
            f"{self.server_url}/sessions/start",
            json=payload,
            headers=headers,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to create session: {resp.text}")
        data = resp.json()
        self.logger.debug(f"Session created: {data}")
        if not data.get("success") or "sessionId" not in data.get("data", {}):
            raise RuntimeError(f"Invalid response format: {resp.text}")
        self.session_id = data["data"]["sessionId"]

    def _execute(self, method: str, payload: dict[str, Any]) -> Any:
        """
        Execute a command synchronously.
        """
        headers = {
            "x-bb-api-key": self.browserbase_api_key,
            "x-bb-project-id": self.browserbase_project_id,
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "x-stream-response": "true",
        }
        if self.model_api_key:
            headers["x-model-api-key"] = self.model_api_key

        # Convert snake_case keys to camelCase for the API
        modified_payload = convert_dict_keys_to_camel_case(payload)

        url = f"{self.server_url}/sessions/{self.session_id}/{method}"
        self.logger.debug(f"\n==== EXECUTING {method.upper()} ====")
        self.logger.debug(f"URL: {url}")
        self.logger.debug(f"Payload: {modified_payload}")
        self.logger.debug(f"Headers: {headers}")

        try:
            if not self.streamed_response:
                # For non-streaming responses, just return the final result
                response = self._client.post(
                    url, json=modified_payload, headers=headers
                )
                if response.status_code != 200:
                    error_message = response.text
                    self.logger.error(
                        f"[HTTP ERROR] Status {response.status_code}: {error_message}"
                    )
                    return None

                return response.json()  # Return the raw response as the result

            # Handle streaming response
            self.logger.debug("Starting to process streaming response...")
            response = self._client.post(
                url, json=modified_payload, headers=headers, stream=True
            )
            if response.status_code != 200:
                error_message = response.text
                self.logger.error(
                    f"[HTTP ERROR] Status {response.status_code}: {error_message}"
                )
                return None

            result = None
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
                        if status == "error":
                            error_msg = message.get("data", {}).get(
                                "error", "Unknown error"
                            )
                            self.logger.error(f"[ERROR] {error_msg}")
                            raise RuntimeError(f"Server returned error: {error_msg}")
                        elif status == "finished":
                            result = message.get("data", {}).get("result")
                            self.logger.debug(
                                "[SYSTEM] Operation completed successfully"
                            )
                            return result
                    elif msg_type == "log":
                        # Process log message using _handle_log
                        self._handle_log(message.get("data", {}))
                    else:
                        # Log any other message types
                        self.logger.debug(f"[UNKNOWN] Message type: {msg_type}")
                except json.JSONDecodeError:
                    self.logger.warning(f"Could not parse line as JSON: {line}")
                    continue
        except Exception as e:
            self.logger.error(f"[EXCEPTION] {str(e)}")
            raise

        return result

    def _handle_log(self, log_data: dict[str, Any]):
        """
        Handle a log message from the server.
        First attempts to use the on_log callback, then falls back to formatting the log locally.
        """
        try:
            # Call user-provided callback with original data if available
            if self.on_log:
                self.on_log(log_data)
                return  # Early return after on_log to prevent double logging

            # Extract message, category, and level info
            message = log_data.get("message", "")
            category = log_data.get("category", "")
            level_str = log_data.get("level", "info")
            auxiliary = log_data.get("auxiliary", {})

            # Map level strings to internal levels
            level_map = {
                "debug": 3,
                "info": 1,
                "warning": 2,
                "error": 0,
            }

            # Convert string level to int if needed
            if isinstance(level_str, str):
                internal_level = level_map.get(level_str.lower(), 1)
            else:
                internal_level = min(level_str, 3)  # Ensure level is between 0-3

            # Handle the case where message itself might be a JSON-like object
            if isinstance(message, dict):
                # If message is a dict, just pass it directly to the logger
                formatted_message = message
            elif isinstance(message, str) and (
                message.startswith("{") and ":" in message
            ):
                # If message looks like JSON but isn't a dict yet, it will be handled by _format_fastify_log
                formatted_message = message
            else:
                # Regular message
                formatted_message = message

            # Log using the structured logger
            self.logger.log(
                formatted_message,
                level=internal_level,
                category=category,
                auxiliary=auxiliary,
            )

        except Exception as e:
            self.logger.error(f"Error processing log message: {str(e)}")

    def _log(
        self, message: str, level: int = 1, category: str = None, auxiliary: dict = None
    ):
        """
        Enhanced logging method that uses the StagehandLogger.

        Args:
            message: The message to log
            level: Verbosity level (0=error, 1=info, 2=detailed, 3=debug)
            category: Optional category for the message
            auxiliary: Optional auxiliary data to include
        """
        # Use the structured logger
        self.logger.log(message, level=level, category=category, auxiliary=auxiliary)
