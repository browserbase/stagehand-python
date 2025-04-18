from typing import Optional, Union

from playwright.async_api import Page

from .schemas import (
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

    def __init__(self, page: Page, stagehand_client):
        """
        Initialize a StagehandPage instance.

        Args:
            page (Page): The underlying Playwright page.
            stagehand_client: The client used to interface with the Stagehand server.
        """
        self.page = page
        self._stagehand = stagehand_client

    async def ensure_injection(self):
        """Ensure custom injection scripts are present on the page using domScripts.js."""
        exists_before = await self.page.evaluate(
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
            await self.page.evaluate(_INJECTION_SCRIPT)
            # Ensure that the script is injected on future navigations
            await self.page.add_init_script(_INJECTION_SCRIPT)

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

    async def act(self, action_or_result: Union[str, ObserveResult], **kwargs) -> ActResult:
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
                self._stagehand.logger.warning(
                    "Additional keyword arguments provided to 'act' when using an ObserveResult are ignored."
                )
            payload = action_or_result.model_dump(exclude_none=True, by_alias=True)
        # If it's a string, construct ActOptions using the string and kwargs
        elif isinstance(action_or_result, str):
            options = ActOptions(action=action_or_result, **kwargs)
            payload = options.model_dump(exclude_none=True, by_alias=True)
        else:
            raise TypeError(
                "First argument to 'act' must be a string (action) or an ObserveResult."
            )

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("act", payload)
        if isinstance(result, dict):
            return ActResult(**result)
        # Ensure we always return an ActResult or raise an error before
        # This line might be reached if _execute returns something unexpected
        # Depending on error handling within _execute, consider raising here
        # For now, returning the raw result if it's not a dict
        return result # Or potentially raise an error if result is not a dict

    async def observe(self, instruction: str, **kwargs) -> list[ObserveResult]:
        """
        Make an AI observation via the Stagehand server.

        Args:
            instruction (str): The observation instruction for the AI.
            **kwargs: Additional options corresponding to fields in ObserveOptions
                      (e.g., model_name, only_visible, return_action).

        Returns:
            list[ObserveResult]: A list of observation results from the Stagehand server.
        """
        await self.ensure_injection()

        # Construct ObserveOptions using the instruction and kwargs
        options = ObserveOptions(instruction=instruction, **kwargs)
        payload = options.model_dump(exclude_none=True, by_alias=True)

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
        self._stagehand.logger.warning(f"Unexpected result type from observe: {type(result)}")
        return []

    async def extract(self, instruction: Optional[str] = None, **kwargs) -> ExtractResult:
        """
        Extract data using AI via the Stagehand server.

        Args:
            instruction (Optional[str]): Instruction specifying what data to extract.
                                         If None, attempts to extract the entire page content
                                         based on other kwargs (e.g., schema_definition).
            **kwargs: Additional options corresponding to fields in ExtractOptions
                      (e.g., schema_definition, model_name, use_text_extract).

        Returns:
            ExtractResult: The result from the Stagehand server's extraction execution.
                          The structure depends on the provided schema_definition.
        """
        await self.ensure_injection()

        # Construct ExtractOptions using the instruction (if provided) and kwargs
        if instruction is not None:
            options = ExtractOptions(instruction=instruction, **kwargs)
        else:
            # Allow extraction without instruction if other options (like schema) are provided
            options = ExtractOptions(**kwargs) # schema_definition might be in kwargs

        payload = options.model_dump(exclude_none=True, by_alias=True)

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("extract", payload)

        # Attempt to parse the result using the base ExtractResult,
        # which allows extra fields based on the dynamic schema.
        if isinstance(result, dict):
            # Pydantic will validate against known fields + allow extras if configured
            try:
                # Note: We don't know the exact return structure here,
                # ExtractResult allows extra fields.
                # The user needs to access data based on their schema.
                return ExtractResult(**result)
            except Exception as e:
                self._stagehand.logger.error(f"Failed to parse extract result: {e}")
                # Return raw dict if parsing fails, or raise? Returning dict for now.
                return result # type: ignore
        # Handle unexpected return types
        self._stagehand.logger.warning(f"Unexpected result type from extract: {type(result)}")
        # Return raw result if not dict or raise error
        return result # type: ignore

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
        payload = options or {}

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("screenshot", payload)

        return result

    # Forward other Page methods to underlying Playwright page
    def __getattr__(self, name):
        """
        Forward attribute lookups to the underlying Playwright page.

        Args:
            name (str): Name of the attribute to access.

        Returns:
            The attribute from the underlying Playwright page.
        """
        self._stagehand.logger.debug(f"Getting attribute: {name}")
        return getattr(self.page, name)
