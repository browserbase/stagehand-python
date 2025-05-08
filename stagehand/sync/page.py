from typing import Optional, Union

from playwright.sync_api import CDPSession, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from stagehand.sync.handlers.act_handler import ActHandler
from stagehand.sync.handlers.observe_handler import ObserveHandler

from ..schemas import (
    ActOptions,
    ActResult,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
)

_INJECTION_SCRIPT = None


class SyncStagehandPage:
    """Synchronous wrapper around Playwright Page that integrates with Stagehand
    server"""

    _cdp_client: Optional[CDPSession] = None

    def __init__(self, page: Page, stagehand_client):
        """
                Initialize a SyncStagehandPage instance.

                Args:
                    page (Page): The underlying Playwright page.
                    stagehand_client: The sync client used to interface with the Stagehand
        server.
        """
        self._page = page
        self._stagehand = stagehand_client

    def ensure_injection(self):
        """Ensure custom injection scripts are present on the page using domScripts.js."""
        exists_before = self._page.evaluate(
            "typeof window.getScrollableElementXpaths === 'function'"
        )
        if not exists_before:
            global _INJECTION_SCRIPT
            if _INJECTION_SCRIPT is None:
                import os

                script_path = os.path.join(
                    os.path.dirname(__file__), "..", "domScripts.js"
                )
                try:
                    with open(script_path) as f:
                        _INJECTION_SCRIPT = f.read()
                except Exception as e:
                    self._stagehand.logger.error(f"Error reading domScripts.js: {e}")
                    _INJECTION_SCRIPT = "/* fallback injection script */"
            # Inject the script into the current page context
            self._page.evaluate(_INJECTION_SCRIPT)
            # Ensure that the script is injected on future navigations
            self._page.add_init_script(_INJECTION_SCRIPT)

    def goto(
        self,
        url: str,
        *,
        referer: Optional[str] = None,
        timeout: Optional[int] = None,
        wait_until: Optional[str] = None,
    ):
        """
                Navigate to URL using the Stagehand server synchronously.

                Args:
                    url (str): The URL to navigate to.
                    referer (Optional[str]): Optional referer URL.
                    timeout (Optional[int]): Optional navigation timeout in milliseconds.
                    wait_until (Optional[str]): Optional wait condition; one of ('load',
        'domcontentloaded', 'networkidle', 'commit').

                Returns:
                    The result from the Stagehand server's navigation execution.
        """
        if self._stagehand.env == "LOCAL":
            self._page.goto(
                url, referer=referer, timeout=timeout, wait_until=wait_until
            )
            return
        options = {}
        if referer is not None:
            options["referer"] = referer
        if timeout is not None:
            options["timeout"] = timeout
        if wait_until is not None:
            options["wait_until"] = wait_until
            options["waitUntil"] = wait_until

        payload = {"url": url}
        if options:
            payload["options"] = options

        result = self._stagehand._execute("navigate", payload)
        return result

    def act(self, options: Union[str, ActOptions, ObserveResult]) -> ActResult:
        """
                Execute an AI action via the Stagehand server synchronously.

                Args:
                    options (Union[str, ActOptions, ObserveResult]):
                        - A string with the action command to be executed by the AI
                        - An ActOptions object encapsulating the action command and optional
        parameters
                        - An ObserveResult with selector and method fields for direct execution
        without LLM

                Returns:
                    ActResult: The result from the Stagehand server's action execution.
        """
        self.ensure_injection()
        # Check if options is an ObserveResult with both selector and method
        if (
            isinstance(options, ObserveResult)
            and hasattr(options, "selector")
            and hasattr(options, "method")
        ):
            # For ObserveResult, we directly pass it to the server which will
            # execute the method against the selector
            payload = options.model_dump(exclude_none=True, by_alias=True)
        # Convert string to ActOptions if needed
        elif isinstance(options, str):
            options = ActOptions(action=options)
            payload = options.model_dump(exclude_none=True, by_alias=True)
        # Otherwise, it should be an ActOptions object
        else:
            payload = options.model_dump(exclude_none=True, by_alias=True)

        if self._stagehand.env == "LOCAL":
            # TODO: revisit passing user_provided_instructions
            if not hasattr(self, "_observe_handler"):
                # TODO: revisit handlers initialization on page creation
                self._observe_handler = ObserveHandler(self, self._stagehand, "")
            if not hasattr(self, "_act_handler"):
                self._act_handler = ActHandler(
                    self, self._stagehand, "", self._stagehand.self_heal
                )
            self._stagehand.logger.debug("act", category="act", auxiliary=payload)
            result = self._act_handler.act(payload)
            return result

        result = self._stagehand._execute("act", payload)
        if isinstance(result, dict):
            return ActResult(**result)
        return result

    def observe(self, options: Union[str, ObserveOptions]) -> list[ObserveResult]:
        """
                Make an AI observation via the Stagehand server synchronously.

                Args:
                    options (Union[str, ObserveOptions]): Either a string with the observation
        instruction
                        or a Pydantic model encapsulating the observation instruction.

                Returns:
                    list[ObserveResult]: A list of observation results from the Stagehand
        server.
        """
        self.ensure_injection()
        # Convert string to ObserveOptions if needed
        if isinstance(options, str):
            options = ObserveOptions(instruction=options)

        if self._stagehand.env == "LOCAL":
            # Create request ID
            import uuid

            request_id = str(uuid.uuid4())

            # If we don't have an observe handler yet, create one
            # TODO: revisit passing user_provided_instructions
            if not hasattr(self, "_observe_handler"):
                self._observe_handler = ObserveHandler(self, self._stagehand, "")

            # Call local observe implementation
            result = self._observe_handler.observe(
                options,
                request_id,
            )
            return result

        payload = options.model_dump(exclude_none=True, by_alias=True)
        result = self._stagehand._execute("observe", payload)

        # Convert raw result to list of ObserveResult models
        if isinstance(result, list):
            return [ObserveResult(**item) for item in result]
        elif isinstance(result, dict):
            # If single dict, wrap in list
            return [ObserveResult(**result)]
        return []

    def extract(self, options: Union[str, ExtractOptions] = None) -> ExtractResult:
        """
        Extract data using AI via the Stagehand server synchronously.

        Args:
            options (Union[str, ExtractOptions], optional): The extraction options describing
                what to extract and how. This can be either a string with an instruction or
                an ExtractOptions object. If None, extracts the entire page content.

        Returns:
            ExtractResult: The result from the Stagehand server's extraction execution.
        """
        self.ensure_injection()
        if self._stagehand.env == "LOCAL":
            self._stagehand.logger.warning(
                "Local execution of extract is not implemented"
            )
            return None
        # Allow for no options to extract the entire page
        if options is None:
            payload = {}
        # Convert string to ExtractOptions if needed
        elif isinstance(options, str):
            options = ExtractOptions(instruction=options)
            payload = options.model_dump(exclude_none=True, by_alias=True)
        # Otherwise, it should be an ExtractOptions object
        else:
            payload = options.model_dump(exclude_none=True, by_alias=True)

        result = self._stagehand._execute("extract", payload)
        if isinstance(result, dict):
            return ExtractResult(**result)
        return result

    def screenshot(self, options: Optional[dict] = None) -> str:
        """
        Take a screenshot of the current page via the Stagehand server synchronously.

        Args:
            options (Optional[dict]): Optional screenshot options.
                May include:
                - type: "png" or "jpeg" (default: "png")
                - fullPage: whether to take a full page screenshot (default: False)
                - quality: for jpeg only, 0-100 (default: 80)
                - clip: viewport clip rectangle
                - omitBackground: whether to hide default white background (default: False)

        Returns:
            str: Base64-encoded screenshot data.
        """
        if self._stagehand.env == "LOCAL":
            self._stagehand.logger.warning(
                "Local execution of screenshot is not implemented"
            )
            return None
        payload = options or {}

        result = self._stagehand._execute("screenshot", payload)

        return result

    # Method to get or initialize the persistent CDP client
    def get_cdp_client(self) -> CDPSession:
        """Gets the persistent CDP client, initializing it if necessary."""
        # Check only if the client is None, rely on send_cdp's exception handling for disconnections
        if self._cdp_client is None:
            try:
                self._stagehand.logger.debug("Creating new persistent CDP session.")
                self._cdp_client = self._page.context.new_cdp_session(self._page)
            except Exception as e:
                self._stagehand.logger.error(f"Failed to create CDP session: {e}")
                raise  # Re-raise the exception
        return self._cdp_client

    # Modified send_cdp to use the persistent client
    def send_cdp(self, method: str, params: Optional[dict] = None) -> dict:
        """Sends a CDP command using the persistent session."""
        client = self.get_cdp_client()
        try:
            result = client.send(method, params or {})
        except Exception as e:
            self._stagehand.logger.error(f"CDP command '{method}' failed: {e}")
            # Handle specific errors if needed (e.g., session closed)
            if "Target closed" in str(e) or "Session closed" in str(e):
                # Attempt to reset the client if the session closed unexpectedly
                self._cdp_client = None
                client = self.get_cdp_client()  # Try creating a new one
                result = client.send(method, params or {})
            else:
                raise  # Re-raise other errors
        return result

    # Method to enable a specific CDP domain
    def enable_cdp_domain(self, domain: str):
        """Enables a specific CDP domain."""
        try:
            self.send_cdp(f"{domain}.enable")
        except Exception as e:
            self._stagehand.logger.warning(
                f"Failed to enable CDP domain '{domain}': {e}"
            )

    # Method to disable a specific CDP domain
    def disable_cdp_domain(self, domain: str):
        """Disables a specific CDP domain."""
        try:
            self.send_cdp(f"{domain}.disable")
        except Exception:
            # Ignore errors during disable, often happens during cleanup
            pass

    # Method to detach the persistent CDP client
    def detach_cdp_client(self):
        """Detaches the persistent CDP client if it exists."""
        if self._cdp_client and self._cdp_client.is_connected():
            try:
                self._cdp_client.detach()
                self._cdp_client = None
            except Exception as e:
                self._stagehand.logger.warning(f"Error detaching CDP client: {e}")
        self._cdp_client = None

    def _wait_for_settled_dom(self, timeout_ms: int = None):
        """
        Wait for the DOM to settle (stop changing) before proceeding.

        Args:
            timeout_ms (int, optional): Maximum time to wait in milliseconds.
                If None, uses the stagehand client's dom_settle_timeout_ms.
        """
        try:
            effective_timeout = timeout_ms or getattr(
                self._stagehand, "dom_settle_timeout_ms", 30000  # Default 30s
            )

            # Wait for initial page readiness signals
            self._page.wait_for_load_state(
                "domcontentloaded", timeout=effective_timeout
            )
            self._page.wait_for_selector("body", timeout=effective_timeout)

            # Set default timeout for the evaluate call, as it doesn't take a direct timeout arg
            # This is a side effect on the page object.
            # Playwright Page doesn't have a direct getter for its own default_timeout.
            # It inherits from context, or uses a playwright-wide default (30s).
            # We will set it and proceed.
            self._page.set_default_timeout(effective_timeout)

            try:
                js_script_for_evaluate = """
                () => {
                    return new Promise((resolve, reject) => {
                        if (typeof window.waitForDomSettle === 'function') {
                            window.waitForDomSettle().then(resolve).catch(e => {
                                console.warn('waitForDomSettle promise rejected in page context:', e);
                                reject(e); // Propagate rejection so Playwright's evaluate can catch it
                            });
                        } else {
                            console.warn('waitForDomSettle is not defined in page context, considering DOM as settled');
                            resolve(); // Resolve immediately if function not present
                        }
                    });
                }
                """
                self._page.evaluate(js_script_for_evaluate)
            finally:
                # Attempt to restore a sensible default timeout if possible.
                # If original_page_default_timeout was None or 0 (no timeout), Playwright uses 30s.
                # For simplicity, if we don't have a reliable original value, we might reset to Playwright's own default.
                # However, set_default_timeout(0) means no timeout. The actual default is 30000ms.
                # This part is tricky without a get_default_timeout().
                # For now, we'll leave the timeout as set, assuming dom_settle_timeout_ms is acceptable.
                # If a more robust restoration is needed, Stagehand client could store initial context timeout.
                pass

        except PlaywrightTimeoutError:
            self._stagehand.logger.warning(
                "DOM settle operation timed out, continuing anyway.",
                extra={"timeout_ms": effective_timeout},
            )
        except Exception as e:
            # Log other errors that might occur
            self._stagehand.logger.error(f"Error in _wait_for_settled_dom: {e}")

    # Forward other Page methods to underlying Playwright page
    def __getattr__(self, name):
        """
        Forward attribute lookups to the underlying Playwright page.

        Args:
            name (str): Name of the attribute to access.

        Returns:
            The attribute from the underlying Playwright page.
        """
        # self._stagehand.logger.debug(f"Getting attribute: {name}")
        return getattr(self._page, name)
