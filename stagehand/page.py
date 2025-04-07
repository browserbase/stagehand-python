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

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("act", payload)
        if isinstance(result, dict):
            return ActResult(**result)
        return result

    async def observe(self, options: Union[str, ObserveOptions]) -> list[ObserveResult]:
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

        payload = options.model_dump(exclude_none=True, by_alias=True)
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
        self, options: Union[str, ExtractOptions] = None
    ) -> ExtractResult:
        """
        Extract data using AI via the Stagehand server.

        Args:
            options (Union[str, ExtractOptions], optional): The extraction options describing what to extract and how.
                This can be either a string with an instruction or an ExtractOptions object.
                If None, extracts the entire page content.
                See `stagehand.schemas.ExtractOptions` for details on expected fields.

        Returns:
            ExtractResult: The result from the Stagehand server's extraction execution.
        """
        await self.ensure_injection()
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
