import asyncio
import functools
import inspect
from typing import Any, Callable, Literal, Optional

from .config import StagehandConfig
from .async_client import Stagehand as AsyncStagehand


class SyncWrapper:
    """Base wrapper class for async objects, converting their methods to sync."""
    
    def __init__(self, async_obj, loop):
        self._async_obj = async_obj
        self._loop = loop
    
    def __getattr__(self, name):
        attr = getattr(self._async_obj, name)
        
        if inspect.iscoroutinefunction(attr):
            @functools.wraps(attr)
            def wrapper(*args, **kwargs):
                return self._loop.run_until_complete(attr(*args, **kwargs))
            return wrapper
            
        return attr


class Stagehand:
    """
    Synchronous facade for Stagehand that delegates to the async implementation.
    Provides a blocking interface for all async methods.
    """

    def __init__(
        self,
        config: Optional[StagehandConfig] = None,
        server_url: Optional[str] = None,
        session_id: Optional[str] = None,
        browserbase_api_key: Optional[str] = None,
        browserbase_project_id: Optional[str] = None,
        model_api_key: Optional[str] = None,
        on_log: Optional[Callable[[dict[str, Any]], Any]] = None,
        verbose: int = 1,
        model_name: Optional[str] = None,
        dom_settle_timeout_ms: Optional[int] = None,
        timeout_settings: Optional[float] = None,
        model_client_options: Optional[dict[str, Any]] = None,
        stream_response: Optional[bool] = None,
        self_heal: Optional[bool] = None,
        wait_for_captcha_solves: Optional[bool] = None,
        system_prompt: Optional[str] = None,
        use_rich_logging: bool = True,
        env: Literal["BROWSERBASE", "LOCAL"] = None,
        local_browser_launch_options: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the synchronous Stagehand client wrapper.
        All parameters are passed directly to the async implementation.
        """
        # Create new event loop for this instance
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        # Create the async implementation with all the parameters
        self._async_client = AsyncStagehand(
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
            timeout_settings=timeout_settings,
            model_client_options=model_client_options,
            stream_response=stream_response,
            self_heal=self_heal,
            wait_for_captcha_solves=wait_for_captcha_solves,
            system_prompt=system_prompt,
            use_rich_logging=use_rich_logging,
            env=env,
            local_browser_launch_options=local_browser_launch_options,
        )
        
        # Set up properties to access nested objects like page and context
        self.page = None
        self.agent = None
        self.context = None
        self.llm = None
        self.metrics = self._async_client.metrics
        self.logger = self._async_client.logger
        
    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the async client.
        If the attribute is a coroutine function, wrap it to run in the event loop.
        """
        attr = getattr(self._async_client, name)
        
        # If it's a coroutine function, wrap it to run synchronously
        if inspect.iscoroutinefunction(attr):
            @functools.wraps(attr)
            def wrapper(*args, **kwargs):
                return self._loop.run_until_complete(attr(*args, **kwargs))
            return wrapper
        
        # For non-coroutine attributes, return them directly
        return attr
    
    def __enter__(self):
        """Context manager entry - initialize the client."""
        self.init()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close the client and event loop."""
        self.close()
        
    def init(self):
        """Initialize the client synchronously."""
        if not hasattr(self._async_client, '_initialized') or not self._async_client._initialized:
            result = self._loop.run_until_complete(self._async_client.init())
            
            # Wrap async attributes with synchronous wrappers
            if hasattr(self._async_client, 'page') and self._async_client.page:
                self.page = SyncWrapper(self._async_client.page, self._loop)
            if hasattr(self._async_client, 'agent') and self._async_client.agent:
                self.agent = SyncWrapper(self._async_client.agent, self._loop)
            if hasattr(self._async_client, 'context') and self._async_client.context:
                self.context = SyncWrapper(self._async_client.context, self._loop)
            if hasattr(self._async_client, 'llm') and self._async_client.llm:
                self.llm = SyncWrapper(self._async_client.llm, self._loop)
                
            # Copy properties that don't need wrapping
            for attr_name in ['session_id', 'browserbase_api_key', 'browserbase_project_id', 'env']:
                if hasattr(self._async_client, attr_name):
                    setattr(self, attr_name, getattr(self._async_client, attr_name))
                
            return result
            
    def close(self):
        """Close the client and event loop synchronously."""
        if not hasattr(self._async_client, '_closed') or not self._async_client._closed:
            try:
                result = self._loop.run_until_complete(self._async_client.close())
                
                # Clean up event loop
                self._loop.close()
                return result
            except RuntimeError:
                # Handle case where loop is already closed
                pass 