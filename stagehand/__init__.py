from typing import Optional, Union, Dict, Any

from .async_client import AsyncStagehand
from .sync_client import SyncStagehand
from .config import StagehandConfig

def create_client(
    sync: bool = False,
    config: Optional[StagehandConfig] = None,
    **kwargs
) -> Union[AsyncStagehand, SyncStagehand]:
    """
    Factory function to create either a synchronous or asynchronous Stagehand client.
    
    Args:
        sync: If True, creates a synchronous client. If False, creates an asynchronous client.
        config: Optional StagehandConfig object to configure the client.
        **kwargs: Additional arguments to pass to the client constructor.
    
    Returns:
        Either a SyncStagehand or AsyncStagehand instance.
    """
    if sync:
        return SyncStagehand(config=config, **kwargs)
    return AsyncStagehand(config=config, **kwargs)

# For backward compatibility
Stagehand = AsyncStagehand

__all__ = ['create_client', 'AsyncStagehand', 'SyncStagehand', 'Stagehand']
