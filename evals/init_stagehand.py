import os
import asyncio
from stagehand import Stagehand
from stagehand.config import StagehandConfig

async def init_stagehand(model_name: str, logger, dom_settle_timeout_ms: int = 3000):
    """
    Initialize a Stagehand client with the given model name, logger, and DOM settle timeout.
    
    This function creates a configuration from environment variables, initializes the Stagehand client,
    and returns a tuple of (stagehand, init_response). The init_response contains dummy debug and session URLs.
    
    Args:
        model_name (str): The name of the AI model to use.
        logger: A logger instance for logging errors and debug messages.
        dom_settle_timeout_ms (int): Milliseconds to wait for the DOM to settle.
        
    Returns:
        tuple: (stagehand, init_response) where init_response is a dict containing:
            - "debugUrl": A dummy URL for debugging.
            - "sessionUrl": A dummy URL for the session.
    """
    # Build a Stagehand configuration object using environment variables
    config = StagehandConfig(
        env="BROWSERBASE" if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID") else "LOCAL",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        debug_dom=True,
        headless=True,
        dom_settle_timeout_ms=dom_settle_timeout_ms,
        model_name=model_name,
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
    )

    # Create a Stagehand client with the configuration; server_url is taken from env
    stagehand = Stagehand(config=config, server_url=os.getenv("STAGEHAND_SERVER_URL"), verbose=2)
    await stagehand.init()

    # Create dummy debug and session URLs for demonstration purposes.
    debug_url = f"http://debug.stagehand/{stagehand.session_id}"
    session_url = f"http://session.stagehand/{stagehand.session_id}"

    return stagehand, {"debugUrl": debug_url, "sessionUrl": session_url}