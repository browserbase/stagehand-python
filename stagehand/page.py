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
from .types import DefaultExtractSchema

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

    # TODO try catch here
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

    async def act(
        self, action_or_result: Union[str, ObserveResult], **kwargs
    ) -> ActResult:
        """
        Execute an AI action or a pre-observed action via the Stagehand server.

        Args:
            action_or_result (Union[str, ObserveResult]):
                - A string with the action command to be executed by the AI.
                - An ObserveResult containing selector and method for direct execution.
            **kwargs: Additional options corresponding to fields in ActOptions
                      (e.g., model_name, timeout_ms). These are ignored if
                      action_or_result is an ObserveResult.

        Returns:
            ActResult: The result from the Stagehand server's action execution.
        """
        await self.ensure_injection()

        payload: dict
        # Check if it's an ObserveResult for direct execution
        if isinstance(action_or_result, ObserveResult):
            if kwargs:
                self._stagehand.logger.debug(
                    "Additional keyword arguments provided to 'act' when using an ObserveResult are ignored."
                )
            payload = action_or_result.model_dump(exclude_none=True, by_alias=True)
        # If it's a string, construct ActOptions using the string and kwargs
        elif isinstance(action_or_result, str):
            options = ActOptions(action=action_or_result, **kwargs)
            payload = options.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(action_or_result, ActOptions):
            payload = action_or_result.model_dump(exclude_none=True, by_alias=True)
        else:
            raise TypeError(
                "Invalid arguments for 'act'. Expected str, ObserveResult, or ActOptions."
            )

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
        self,
        options_or_instruction: Union[str, ObserveOptions, None] = None,
        **kwargs,
    ) -> list[ObserveResult]:
        """
        Make an AI observation via the Stagehand server.

        Args:
            options_or_instruction (Union[str, ObserveOptions, None]):
                - A string with the observation instruction for the AI.
                - An ObserveOptions object.
                - None to use default options.
            **kwargs: Additional options corresponding to fields in ObserveOptions
                      (e.g., model_name, only_visible, return_action).

        Returns:
            list[ObserveResult]: A list of observation results from the Stagehand server.
        """
        await self.ensure_injection()

        options_dict = {}

        if isinstance(options_or_instruction, ObserveOptions):
            # Already a pydantic object – take it as is.
            options_obj = options_or_instruction
        else:
            if isinstance(options_or_instruction, str):
                options_dict["instruction"] = options_or_instruction

            # Merge any explicit keyword arguments (highest priority)
            options_dict.update(kwargs)

            if not options_dict:
                raise TypeError("No instruction provided for observe.")

            try:
                options_obj = ObserveOptions(**options_dict)
            except Exception as e:
                raise TypeError(f"Invalid observe options: {e}") from e

        # Serialized payload for server / local handlers
        payload = options_obj.model_dump(exclude_none=True, by_alias=True)

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
                options_obj,
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
            # If single dict, wrap in list (should ideally be list from server)
            return [ObserveResult(**result)]
        # Handle unexpected return types
        self._stagehand.logger.info(
            f"Unexpected result type from observe: {type(result)}"
        )
        return []

    async def extract(
        self,
        options_or_instruction: Union[str, ExtractOptions, None] = None,
        *,
        schema: Optional[type[BaseModel]] = None,
        **kwargs,
    ) -> ExtractResult:
        """
        Extract data using AI via the Stagehand server.

        Args:
            options_or_instruction (Union[str, ExtractOptions, None]):
                - A string with the instruction specifying what data to extract.
                - An ExtractOptions object.
                - None to extract the entire page content.
            schema (Optional[Union[type[BaseModel], None]]):
                A Pydantic model class that defines the structure
                of the expected extracted data.
            **kwargs: Additional options corresponding to fields in ExtractOptions
                      (e.g., model_name, use_text_extract, selector, dom_settle_timeout_ms).

        Returns:
            ExtractResult: Depending on the type of the schema provided, the result will be a Pydantic model or JSON representation of the extracted data.
        """
        await self.ensure_injection()

        options_dict = {}

        if isinstance(options_or_instruction, ExtractOptions):
            options_obj = options_or_instruction
        else:
            if isinstance(options_or_instruction, str):
                options_dict["instruction"] = options_or_instruction

            # Merge keyword overrides (highest priority)
            options_dict.update(kwargs)

            # Ensure schema_definition is only set once (explicit arg precedence)
            if schema is not None:
                options_dict["schema_definition"] = schema

            if options_dict:
                try:
                    options_obj = ExtractOptions(**options_dict)
                except Exception as e:
                    raise TypeError(f"Invalid extract options: {e}") from e
            else:
                # No options_dict provided and no ExtractOptions given: full page extract.
                options_obj = None

        # If we started with an existing ExtractOptions instance and the caller
        # explicitly provided a schema, override it
        if (
            schema is not None
            and isinstance(options_obj, ExtractOptions)
            and options_obj.schema_definition != schema
        ):
            options_obj = options_obj.model_copy(update={"schema_definition": schema})

        if options_obj is None:
            payload = {}
        else:
            payload = options_obj.model_dump(exclude_none=True, by_alias=True)

        # Determine the schema to pass to the handler
        schema_to_validate_with = None
        if (
            options_obj is not None
            and options_obj.schema_definition is not None
            and options_obj.schema_definition != DEFAULT_EXTRACT_SCHEMA
        ):
            if isinstance(options_obj.schema_definition, type) and issubclass(
                options_obj.schema_definition, BaseModel
            ):
                # Case 1: Pydantic model class
                schema_to_validate_with = options_obj.schema_definition
            elif isinstance(options_obj.schema_definition, dict):
                # TODO: revisit this case to pass the json_schema since litellm has a bug when passing it directly
                # Case 2: Dictionary
                # Assume it's a direct JSON schema dictionary
                schema_to_validate_with = options_obj.schema_definition
        else:
            schema_to_validate_with = DefaultExtractSchema

        # If in LOCAL mode, use local implementation
        if self._stagehand.env == "LOCAL":
            # If we don't have an extract handler yet, create one
            if not hasattr(self, "_extract_handler"):
                self._extract_handler = ExtractHandler(
                    self, self._stagehand, self._stagehand.system_prompt
                )

            # Allow for no options to extract the entire page
            if options_obj is None:
                # Call local extract implementation with no options
                result = await self._extract_handler.extract(
                    None,
                    None,  # Explicitly pass None for schema if no options
                )
                return result

            # Call local extract implementation
            result = await self._extract_handler.extract(
                options_obj,
                schema_to_validate_with,
            )
            return result.data

        # Use API
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result_dict = await self._stagehand._execute("extract", payload)

        if isinstance(result_dict, dict):
            # Pydantic will validate against known fields + allow extras if configured
            processed_data_payload = result_dict
            if schema_to_validate_with and isinstance(processed_data_payload, dict):
                try:
                    validated_model = schema_to_validate_with.model_validate(
                        processed_data_payload
                    )
                    processed_data_payload = (
                        validated_model  # Payload is now the Pydantic model instance
                    )
                except Exception as e:
                    self._stagehand.logger.error(
                        f"Failed to validate extracted data against schema {schema_to_validate_with.__name__}: {e}. Keeping raw data dict in .data field."
                    )
            return ExtractResult(data=processed_data_payload).data
        # Handle unexpected return types
        self._stagehand.logger.info(
            f"Unexpected result type from extract: {type(result_dict)}"
        )
        return result_dict

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
            self._stagehand.logger.info(
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
            self._stagehand.logger.debug(
                f"CDP command '{method}' failed: {e}. Attempting to reconnect..."
            )
            # Try to reconnect
            await self._ensure_cdp_session()
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
            self._stagehand.logger.debug(f"Failed to enable CDP domain '{domain}': {e}")

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
                self._stagehand.logger.debug(f"Error detaching CDP client: {e}")
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
                    self._stagehand.logger.debug(
                        "DOM settle timeout exceeded, continuing anyway",
                        extra={"timeout_ms": timeout},
                    )

            except Exception as e:
                self._stagehand.logger.debug(f"Error waiting for DOM to settle: {e}")

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
