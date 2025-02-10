from typing import Optional, Dict, Any
from playwright.async_api import Page
from pydantic import BaseModel

# (Make sure to import the new options models when needed)
from .schemas import ActOptions, ObserveOptions, ExtractOptions

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
        
    async def goto(self, url: str, **kwargs):
        """
        Navigate to the given URL using Playwright directly.
        
        Args:
            url (str): The URL to navigate to.
            **kwargs: Additional keyword arguments passed to Playwright's page.goto.
            
        Returns:
            The result of Playwright's page.goto method.
        """
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            return await self.page.goto(url, **kwargs)

    async def navigate(
        self, 
        url: str, 
        *, 
        referer: Optional[str] = None,
        timeout: Optional[int] = None, 
        wait_until: Optional[str] = None
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
            options["waitUntil"] = wait_until
            
        payload = {"url": url}
        if options:
            payload["options"] = options

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("navigate", payload)
        return result
    
    async def act(self, options: ActOptions) -> Any:
        """
        Execute an AI action via the Stagehand server.
        
        Args:
            options (ActOptions): A Pydantic model encapsulating the action.
                See `stagehand.schemas.ActOptions` for details on expected fields.
            
        Returns:
            Any: The result from the Stagehand server's action execution.
        """
        payload = options.dict(exclude_none=True)
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("act", payload)
        return result
        
    async def observe(self, options: ObserveOptions) -> Any:
        """
        Make an AI observation via the Stagehand server.
        
        Args:
            options (ObserveOptions): A Pydantic model encapsulating the observation instruction.
                See `stagehand.schemas.ObserveOptions` for details on expected fields.
            
        Returns:
            Any: The result from the Stagehand server's observation execution.
        """
        payload = options.dict(exclude_none=True)
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("observe", payload)
        return result
        
    async def extract(self, options: ExtractOptions) -> Any:
        """
        Extract data using AI via the Stagehand server.
        
        Expects an ExtractOptions Pydantic object that includes a JSON schema (or Pydantic model)
        for validation.
        
        Args:
            options (ExtractOptions): The extraction options describing what to extract and how.
                See `stagehand.schemas.ExtractOptions` for details on expected fields.
            
        Returns:
            Any: The result from the Stagehand server's extraction execution.
        """
        payload = options.dict(exclude_none=True)
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("extract", payload)
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