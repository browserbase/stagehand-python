import os
from stagehand import Stagehand, StagehandConfig


async def init_stagehand(model_name: str, logger, dom_settle_timeout_ms: int = 3000):
    """
    Initialize a Stagehand client with the given model name, logger, and DOM settle
    timeout using the modern StagehandConfig approach.

    Args:
        model_name (str): The name of the AI model to use.
        logger: A logger instance for logging errors and debug messages.
        dom_settle_timeout_ms (int): Milliseconds to wait for the DOM to settle.

    Returns:
        tuple: (stagehand, init_response) where init_response is a dict containing:
            - "debugUrl": Debug URL for the session (or None in LOCAL mode).
            - "sessionUrl": Session URL for the session (or None in LOCAL mode).
    """
    # Determine whether to use BROWSERBASE or LOCAL mode
    env_mode = (
        "BROWSERBASE"
        if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")
        else "LOCAL"
    )
    logger.info(f"Using environment mode: {env_mode}")

    # Build a unified configuration object for Stagehand
    config = StagehandConfig(
        env=env_mode,
        api_key=os.getenv("BROWSERBASE_API_KEY") if env_mode == "BROWSERBASE" else None,
        project_id=os.getenv("BROWSERBASE_PROJECT_ID") if env_mode == "BROWSERBASE" else None,
        headless=False,  # Set to False for debugging
        dom_settle_timeout_ms=dom_settle_timeout_ms,
        model_name=model_name,
        self_heal=True,
        wait_for_captcha_solves=True,
        system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")},
        verbose=2,  # Medium detail logs
    )

    # Create the Stagehand client using the configuration object
    stagehand = Stagehand(config)

    # Initialize the stagehand client
    logger.info("Initializing Stagehand...")
    await stagehand.init()
    logger.info(f"Stagehand initialized with session ID: {stagehand.session_id}")

    # For BROWSERBASE mode, construct debug and session URLs
    if env_mode == "BROWSERBASE" and stagehand.session_id:
        session_url = f"https://www.browserbase.com/sessions/{stagehand.session_id}"
        init_response = {"debugUrl": session_url, "sessionUrl": session_url}
        logger.info(f"Session URL: {session_url}")
    else:
        # For LOCAL mode, provide None values for the URLs
        init_response = {"debugUrl": None, "sessionUrl": None}
        logger.info("Running in LOCAL mode - no session URLs available")

    return stagehand, init_response
