from typing import List, Optional, Union

from playwright.sync_api import Page

from ..schemas import (
    ActOptions,
    ActResult,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
)


class SyncStagehandPage:
    """Synchronous wrapper around Playwright Page that integrates with Stagehand server"""

    def __init__(self, page: Page, stagehand_client):
        """
        Initialize a SyncStagehandPage instance.

        Args:
            page (Page): The underlying Playwright page.
            stagehand_client: The sync client used to interface with the Stagehand server.
        """
        self.page = page
        self._stagehand = stagehand_client

    def goto(
        self,
        url: str,
        *,
        referer: Optional[str] = None,
        timeout: Optional[int] = None,
        wait_until: Optional[str] = None
    ):
        """
        Navigate to URL using the Stagehand server synchronously.

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

        result = self._stagehand._execute("navigate", payload)
        return result

    def act(self, options: Union[str, ActOptions, ObserveResult]) -> ActResult:
        """
        Execute an AI action via the Stagehand server synchronously.

        Args:
            options (Union[str, ActOptions, ObserveResult]):
                - A string with the action command to be executed by the AI
                - An ActOptions object encapsulating the action command and optional parameters
                - An ObserveResult with selector and method fields for direct execution without LLM

        Returns:
            ActResult: The result from the Stagehand server's action execution.
        """
        # Check if options is an ObserveResult with both selector and method
        if isinstance(options, ObserveResult) and hasattr(options, "selector") and hasattr(options, "method"):
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

        result = self._stagehand._execute("act", payload)
        if isinstance(result, dict):
            return ActResult(**result)
        return result

    def observe(self, options: Union[str, ObserveOptions]) -> List[ObserveResult]:
        """
        Make an AI observation via the Stagehand server synchronously.

        Args:
            options (Union[str, ObserveOptions]): Either a string with the observation instruction
                or a Pydantic model encapsulating the observation instruction.

        Returns:
            List[ObserveResult]: A list of observation results from the Stagehand server.
        """
        # Convert string to ObserveOptions if needed
        if isinstance(options, str):
            options = ObserveOptions(instruction=options)

        payload = options.model_dump(exclude_none=True, by_alias=True)
        result = self._stagehand._execute("observe", payload)

        # Convert raw result to list of ObserveResult models
        if isinstance(result, list):
            return [ObserveResult(**item) for item in result]
        elif isinstance(result, dict):
            # If single dict, wrap in list
            return [ObserveResult(**result)]
        return []

    def extract(self, options: Union[str, ExtractOptions]) -> ExtractResult:
        """
        Extract data using AI via the Stagehand server synchronously.

        Args:
            options (Union[str, ExtractOptions]): The extraction options describing what to extract and how.

        Returns:
            ExtractResult: The result from the Stagehand server's extraction execution.
        """
        # Convert string to ExtractOptions if needed
        if isinstance(options, str):
            options = ExtractOptions(instruction=options)

        payload = options.model_dump(exclude_none=True, by_alias=True)
        result = self._stagehand._execute("extract", payload)
        if isinstance(result, dict):
            return ExtractResult(**result)
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
        return getattr(self.page, name) 