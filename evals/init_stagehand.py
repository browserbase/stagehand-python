import os
import asyncio
from stagehand import Stagehand
from stagehand.config import StagehandConfig

async def init_stagehand(model_name: str, logger, dom_settle_timeout_ms: int = 3000):
    """
    Initialize a Stagehand client with the given model name, logger, and DOM settle timeout.
    
    This function creates a configuration from environment variables, initializes the Stagehand client,
    and returns a tuple of (stagehand, init_response). The init_response contains debug and session URLs.
    
    Args:
        model_name (str): The name of the AI model to use.
        logger: A logger instance for logging errors and debug messages.
        dom_settle_timeout_ms (int): Milliseconds to wait for the DOM to settle.
        
    Returns:
        tuple: (stagehand, init_response) where init_response is a dict containing:
            - "debugUrl": A dict with a "value" key for the debug URL.
            - "sessionUrl": A dict with a "value" key for the session URL.
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

    # Create a Stagehand client with the configuration; server_url is taken from environment variables.
    stagehand = Stagehand(config=config, server_url=os.getenv("STAGEHAND_SERVER_URL"), verbose=2)
    await stagehand.init()

    # Construct the URL from the session id using the new format.
    # For example:
    # "wss://connect.browserbase.com?apiKey=bb_live_1KG6TTh14CYTJdyNTLpnugz9kgk&sessionId=<session_id>"
    api_key = os.getenv("BROWSERBASE_API_KEY")
    url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={stagehand.session_id}"

    # Return both URLs as dictionaries with the "value" key.
    return stagehand, {"debugUrl": {"value": url}, "sessionUrl": {"value": url}}