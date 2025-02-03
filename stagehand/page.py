from typing import Optional, Dict, Any, Union
from playwright.async_api import Page
from pydantic import BaseModel

class StagehandPage:
    """Wrapper around Playwright Page that integrates with Stagehand server"""
    
    def __init__(self, page: Page, stagehand_client):
        self.page = page
        self._stagehand = stagehand_client
        
    async def goto(self, url: str, **kwargs):
        """Navigate to URL using Playwright directly"""
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
        Navigate to URL using Stagehand server
        
        Args:
            url: The URL to navigate to
            referer: Optional referer URL
            timeout: Optional navigation timeout in milliseconds
            wait_until: Optional wait until condition ('load'|'domcontentloaded'|'networkidle'|'commit')
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
    
    async def act(
        self, 
        action: str, 
        *, 
        use_vision: Optional[Union[bool, str]] = None,
        variables: Optional[Dict[str, str]] = None
    ):
        """
        Execute AI action via Stagehand server
        
        Args:
            action: The action instruction for the AI
            use_vision: Optional boolean or "fallback" to control vision usage
            variables: Optional variables to substitute in the action
        """
        payload = {"action": action}
        if use_vision is not None:
            payload["useVision"] = use_vision
        if variables is not None:
            payload["variables"] = variables
            
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("act", payload)
        return result
        
    async def observe(
        self,
        instruction: Optional[str] = None,
        use_vision: Optional[bool] = None,
        use_accessibility_tree: Optional[bool] = None
    ):
        """
        Make AI observation via Stagehand server

        Args:
            instruction: Optional instruction to guide the observation
            use_vision: Optional boolean to control vision usage
            use_accessibility_tree: Optional boolean to control accessibility tree usage
        """
        payload = {}
        if instruction is not None:
            payload["instruction"] = instruction
        if use_vision is not None:
            payload["useVision"] = use_vision
        if use_accessibility_tree is not None:
            payload["useAccessibilityTree"] = use_accessibility_tree
            
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("observe", payload)
        return result
        
    async def extract(
        self,
        instruction: str,
        schema: Union[Dict[str, Any], type(BaseModel)],
        *,
        use_text_extract: Optional[bool] = None,
        **kwargs
    ):
        """
        Extract data using AI via Stagehand server
        
        Args:
            instruction: The instruction for what data to extract
            schema: JSON schema as dict or Pydantic model class defining the structure
            use_text_extract: Optional boolean to control text extraction mode
            **kwargs: Additional arguments to pass to the server
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            schema_definition = schema.schema()
        elif isinstance(schema, dict):
            schema_definition = schema
        else:
            raise ValueError("schema must be a dict or Pydantic model class")
            
        payload = {
            "instruction": instruction,
            "schemaDefinition": schema_definition
        }
        
        if use_text_extract is not None:
            payload["useTextExtract"] = use_text_extract
            
        payload.update(kwargs)
        
        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("extract", payload)
        return result

    # Forward other Page methods to underlying Playwright page
    # TODO - add a lock for all page actions?
    def __getattr__(self, name):
        return getattr(self.page, name)