import os

from evals.utils import ensure_stagehand_config
from stagehand import Stagehand


async def init_stagehand(model_name: str, logger, dom_settle_timeout_ms: int = 3000):
    """
    Initialize a Stagehand client with the given model name, logger, and DOM settle
    timeout.

    This function creates a configuration from environment variables, initializes
    the Stagehand client, and returns a tuple of (stagehand, init_response).
    The init_response contains debug and session URLs if using BROWSERBASE, or
    None values if running in LOCAL mode.

    Args:
        model_name (str): The name of the AI model to use.
        logger: A logger instance for logging errors and debug messages.
        dom_settle_timeout_ms (int): Milliseconds to wait for the DOM to settle.

    Returns:
        tuple: (stagehand, init_response) where init_response is a dict containing:
            - "debugUrl": A dict with a "value" key for the debug URL (or None in LOCAL mode).
            - "sessionUrl": A dict with a "value" key for the session URL (or None in LOCAL mode).
    """
    # Determine whether to use BROWSERBASE or LOCAL mode
    env_mode = (
        "BROWSERBASE"
        if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")
        else "LOCAL"
    )
    logger.info(f"Using environment mode: {env_mode}")

    # For BROWSERBASE mode only: Add API key and project ID
    browserbase_api_key = (
        os.getenv("BROWSERBASE_API_KEY") if env_mode == "BROWSERBASE" else None
    )
    browserbase_project_id = (
        os.getenv("BROWSERBASE_PROJECT_ID") if env_mode == "BROWSERBASE" else None
    )

    # Define common parameters directly for the Stagehand constructor
    stagehand_params = {
        "env": env_mode,
        "verbose": 2,
        "on_log": lambda log: logger.info(f"Stagehand log: {log}"),
        "model_name": model_name,
        "dom_settle_timeout_ms": dom_settle_timeout_ms,
        "model_client_options": {
            "apiKey": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
        },
    }

    # Add browserbase-specific parameters if needed
    if env_mode == "BROWSERBASE":
        stagehand_params["browserbase_api_key"] = browserbase_api_key
        stagehand_params["browserbase_project_id"] = browserbase_project_id

        # Only include server_url for BROWSERBASE mode
        if os.getenv("STAGEHAND_SERVER_URL"):
            stagehand_params["server_url"] = os.getenv("STAGEHAND_SERVER_URL")
    else:  # LOCAL mode
        stagehand_params["local_browser_launch_options"] = {
            "headless": False,  # Set to False for debugging if needed
            "viewport": {"width": 1024, "height": 768},
        }

    # Create the Stagehand client with params directly
    stagehand = Stagehand(**stagehand_params)

    # Initialize the stagehand client
    await stagehand.init()

    # Ensure the stagehand instance has a config attribute
    stagehand = ensure_stagehand_config(stagehand)

    # For BROWSERBASE mode, construct debug and session URLs
    if env_mode == "BROWSERBASE" and stagehand.session_id:
        api_key = os.getenv("BROWSERBASE_API_KEY")
        url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={stagehand.session_id}"
        init_response = {"debugUrl": {"value": url}, "sessionUrl": {"value": url}}
    else:
        # For LOCAL mode, provide None values for the URLs
        init_response = {"debugUrl": {"value": None}, "sessionUrl": {"value": None}}

    return stagehand, init_response
