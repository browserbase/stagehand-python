from typing import Optional, Union

from playwright.async_api import CDPSession, Page
from pydantic import BaseModel

from stagehand.handlers.act_handler import ActHandler
from stagehand.handlers.extract_handler import ExtractHandler
from stagehand.handlers.observe_handler import ObserveHandler

from .schemas import (
    DEFAULT_EXTRACT_SCHEMA,
    ActOptions,
    ActResult,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
)

_INJECTION_SCRIPT = None


class StagehandPage:
    """Wrapper around Playwright Page that integrates with Stagehand server"""

    _cdp_client: Optional[CDPSession] = None

    def __init__(self, page: Page, stagehand_client):
        """
        Initialize a StagehandPage instance.

        Args:
            page (Page): The underlying Playwright page.
            stagehand_client: The client used to interface with the Stagehand server.
        """
        self._page = page
        self._stagehand = stagehand_client

    async def ensure_injection(self):
        """Ensure custom injection scripts are present on the page using domScripts.js."""
        exists_before = await self._page.evaluate(
            "typeof window.getScrollableElementXpaths === 'function'"
        )
        if not exists_before:
            global _INJECTION_SCRIPT
            if _INJECTION_SCRIPT is None:
                import os

                script_path = os.path.join(os.path.dirname(__file__), "domScripts.js")
                try:
                    with open(script_path) as f:
                        _INJECTION_SCRIPT = f.read()
                except Exception as e:
                    self._stagehand.logger.error(f"Error reading domScripts.js: {e}")
                    _INJECTION_SCRIPT = "/* fallback injection script */"
            # Inject the script into the current page context
            await self._page.evaluate(_INJECTION_SCRIPT)
            # Ensure that the script is injected on future navigations
            await self._page.add_init_script(_INJECTION_SCRIPT)

    async def goto(
        self,
        url: str,
        *,
        referer: Optional[str] = None,
        timeout: Optional[int] = None,
        wait_until: Optional[str] = None,
    ):
        """
        Navigate to URL using the Stagehand server.

        Args:
            url (str): The URL to navigate to.
            referer (Optional[str]): Optional referer URL.
            timeout (Optional[int]): Optional navigation timeout in milliseconds.
            wait_until (Optional[str]): Optional wait condition; one of ('load', 'domcontentloaded', 'networkidle', 'commit').

        Returns:
            The result from the Stagehand server's navigation execution.
        """
        if self._stagehand.env == "LOCAL":
            await self._page.goto(
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

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("navigate", payload)
        return result

    async def act(self, options: Union[str, ActOptions, ObserveResult]) -> ActResult:
        """
        Execute an AI action via the Stagehand server.

        Args:
            options (Union[str, ActOptions, ObserveResult]):
                - A string with the action command to be executed by the AI
                - An ActOptions object encapsulating the action command and optional parameters
                - An ObserveResult with selector and method fields for direct execution without LLM

                When an ObserveResult with both 'selector' and 'method' fields is provided,
                the SDK will directly execute the action against the selector using the method
                and arguments provided, bypassing the LLM processing.

        Returns:
            ActResult: The result from the Stagehand server's action execution.
        """
        await self.ensure_injection()
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

        # TODO: Temporary until we move api based logic to client
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
            result = await self._act_handler.act(payload)
            return result

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("act", payload)
        if isinstance(result, dict):
            return ActResult(**result)
        return result

    async def observe(
        self, options: Union[str, ObserveOptions] = None
    ) -> list[ObserveResult]:
        """
        Make an AI observation via the Stagehand server.

        Args:
            options (Union[str, ObserveOptions]): Either a string with the observation instruction
                or a Pydantic model encapsulating the observation instruction.
                See `stagehand.schemas.ObserveOptions` for details on expected fields.

        Returns:
            list[ObserveResult]: A list of observation results from the Stagehand server.
        """
        await self.ensure_injection()

        # Convert string to ObserveOptions if needed
        if isinstance(options, str):
            options = ObserveOptions(instruction=options)
        # Handle None by creating an empty options object
        elif options is None:
            options = ObserveOptions()

        # Otherwise use API implementation
        payload = options.model_dump(exclude_none=True, by_alias=True)
        # If in LOCAL mode, use local implementation
        if self._stagehand.env == "LOCAL":
            self._stagehand.logger.debug(
                "observe", category="observe", auxiliary=payload
            )
            # If we don't have an observe handler yet, create one
            # TODO: revisit passing user_provided_instructions
            if not hasattr(self, "_observe_handler"):
                self._observe_handler = ObserveHandler(self, self._stagehand, "")

            # Call local observe implementation
            result = await self._observe_handler.observe(
                options,
                from_act=False,
            )

            return result

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("observe", payload)

        # Convert raw result to list of ObserveResult models
        if isinstance(result, list):
            return [ObserveResult(**item) for item in result]
        elif isinstance(result, dict):
            # If single dict, wrap in list
            return [ObserveResult(**result)]
        return []

    async def extract(
        self, options: Union[str, ExtractOptions, None] = None
    ) -> ExtractResult:
        # TODO update args
        """
        Extract data using AI via the Stagehand server.

        Args:
            options (Union[str, ExtractOptions], optional): The extraction options describing what to extract and how.
                This can be either a string with an instruction or an ExtractOptions object.
                If None, extracts the entire page content.
                See `stagehand.schemas.ExtractOptions` for details on expected fields.

        Returns:
            ExtractResult: Depending on the type of the schema provided, the result will be a Pydantic model or JSON representation of the extracted data.
        """
        await self.ensure_injection()

        # Otherwise use API implementation
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

        # If in LOCAL mode, use local implementation
        if self._stagehand.env == "LOCAL":
            # If we don't have an extract handler yet, create one
            if not hasattr(self, "_extract_handler"):
                self._extract_handler = ExtractHandler(
                    self, self._stagehand, self._stagehand.system_prompt
                )

            # Allow for no options to extract the entire page
            if options is None:
                # Call local extract implementation with no options
                result = await self._extract_handler.extract(
                    None,
                    None,  # Explicitly pass None for schema if no options
                )
                return result

            # Convert string to ExtractOptions if needed
            if isinstance(options, str):
                options = ExtractOptions(instruction=options)

            # Determine the schema to pass to the handler
            schema_to_pass_to_handler = None
            if (
                hasattr(options, "schema_definition")
                and options.schema_definition != DEFAULT_EXTRACT_SCHEMA
            ):
                if isinstance(options.schema_definition, type) and issubclass(
                    options.schema_definition, BaseModel
                ):
                    # Case 1: Pydantic model class
                    schema_to_pass_to_handler = options.schema_definition
                elif isinstance(options.schema_definition, dict):
                    # TODO: revisit this case to pass the json_schema since litellm has a bug when passing it directly
                    # Case 2: Dictionary
                    # Assume it's a direct JSON schema dictionary
                    schema_to_pass_to_handler = options.schema_definition

            # Call local extract implementation
            result = await self._extract_handler.extract(
                options,
                schema_to_pass_to_handler,
            )
            return result.data

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("extract", payload)
        if isinstance(result, dict):
            return ExtractResult(**result)
        return result

    async def screenshot(self, options: Optional[dict] = None) -> str:
        """
        Take a screenshot of the current page via the Stagehand server.

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

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("screenshot", payload)

        return result

    # Method to get or initialize the persistent CDP client
    async def get_cdp_client(self) -> CDPSession:
        """Gets the persistent CDP client, initializing it if necessary."""
        # Check only if the client is None, rely on send_cdp's exception handling for disconnections
        if self._cdp_client is None:
            try:
                self._stagehand.logger.debug("Creating new persistent CDP session.")
                self._cdp_client = await self._page.context.new_cdp_session(self._page)
            except Exception as e:
                self._stagehand.logger.error(f"Failed to create CDP session: {e}")
                raise  # Re-raise the exception
        return self._cdp_client

    # Modified send_cdp to use the persistent client
    async def send_cdp(self, method: str, params: Optional[dict] = None) -> dict:
        """Sends a CDP command using the persistent session."""
        client = await self.get_cdp_client()
        try:
            # Type assertion might be needed depending on playwright version/typing
            result = await client.send(method, params or {})
        except Exception as e:
            self._stagehand.logger.error(f"CDP command '{method}' failed: {e}")
            # Handle specific errors if needed (e.g., session closed)
            if "Target closed" in str(e) or "Session closed" in str(e):
                # Attempt to reset the client if the session closed unexpectedly
                self._cdp_client = None
                client = await self.get_cdp_client()  # Try creating a new one
                result = await client.send(method, params or {})
            else:
                raise  # Re-raise other errors
        return result

    # Method to enable a specific CDP domain
    async def enable_cdp_domain(self, domain: str):
        """Enables a specific CDP domain."""
        try:
            await self.send_cdp(f"{domain}.enable")
        except Exception as e:
            self._stagehand.logger.warning(
                f"Failed to enable CDP domain '{domain}': {e}"
            )

    # Method to disable a specific CDP domain
    async def disable_cdp_domain(self, domain: str):
        """Disables a specific CDP domain."""
        try:
            await self.send_cdp(f"{domain}.disable")
        except Exception:
            # Ignore errors during disable, often happens during cleanup
            pass

    # Method to detach the persistent CDP client
    async def detach_cdp_client(self):
        """Detaches the persistent CDP client if it exists."""
        if self._cdp_client and self._cdp_client.is_connected():
            try:
                await self._cdp_client.detach()
                self._cdp_client = None
            except Exception as e:
                self._stagehand.logger.warning(f"Error detaching CDP client: {e}")
        self._cdp_client = None

    async def _wait_for_settled_dom(self, timeout_ms: int = None):
        """
        Wait for the DOM to settle (stop changing) before proceeding.

        Args:
            timeout_ms (int, optional): Maximum time to wait in milliseconds.
                If None, uses the stagehand client's dom_settle_timeout_ms.
        """
        try:
            timeout = timeout_ms or getattr(
                self._stagehand, "dom_settle_timeout_ms", 30000
            )
            import asyncio

            # Wait for domcontentloaded first
            await self._page.wait_for_load_state("domcontentloaded")

            # Create a timeout promise that resolves after the specified time
            timeout_task = asyncio.create_task(asyncio.sleep(timeout / 1000))

            # Try to check if the DOM has settled
            try:
                # Create a task for evaluating the DOM settling
                eval_task = asyncio.create_task(
                    self._page.evaluate(
                        """
                        () => {
                            return new Promise((resolve) => {
                                if (typeof window.waitForDomSettle === 'function') {
                                    window.waitForDomSettle().then(resolve);
                                } else {
                                    console.warn('waitForDomSettle is not defined, considering DOM as settled');
                                    resolve();
                                }
                            });
                        }
                    """
                    )
                )

                # Create tasks for other ways to determine page readiness
                dom_task = asyncio.create_task(
                    self._page.wait_for_load_state("domcontentloaded")
                )
                body_task = asyncio.create_task(self._page.wait_for_selector("body"))

                # Wait for the first task to complete
                done, pending = await asyncio.wait(
                    [eval_task, dom_task, body_task, timeout_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Cancel any pending tasks
                for task in pending:
                    task.cancel()

                # If the timeout was hit, log a warning
                if timeout_task in done:
                    self._stagehand.logger.warning(
                        "DOM settle timeout exceeded, continuing anyway",
                        extra={"timeout_ms": timeout},
                    )

            except Exception as e:
                self._stagehand.logger.warning(f"Error waiting for DOM to settle: {e}")

        except Exception as e:
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
