import asyncio

from evals.init_stagehand import init_stagehand


async def observe_search_results(model_name: str, logger) -> dict:
    """
    This function evaluates observing search results on Google by:

    1. Initializing Stagehand with the provided model name and logger.
    2. Navigating to Google.
    3. Performing a search for "stagehand browser automation".
    4. Using observe to find all search result links.
    5. Validating that multiple search results are found.

    Returns a dictionary containing:
      - _success (bool): True if search results are found.
      - search_results_count (int): Number of search results found.
      - observations (list): The raw observations returned from the observe command.
      - debugUrl (str): Debug URL from the Stagehand initialization.
      - sessionUrl (str): Session URL from the Stagehand initialization.
      - logs (list): Logs collected via the provided logger.
    """
    stagehand = None
    try:
        # Initialize Stagehand
        stagehand, init_response = await init_stagehand(model_name, logger)
        debug_url = init_response.get("debugUrl")
        session_url = init_response.get("sessionUrl")

        # Navigate to Google
        logger.info("Navigating to Google...")
        await stagehand.page.goto("https://google.com/")

        # Perform a search
        logger.info("Performing search for 'stagehand browser automation'...")
        await stagehand.page.act("search for stagehand browser automation")
        await stagehand.page.keyboard.press("Enter")
        
        # Wait for results to load
        await asyncio.sleep(3)

        # Use observe to find search result links
        logger.info("Observing search results...")
        observations = await stagehand.page.observe(
            "Find all the main search result links (not ads or related links)"
        )

        # Validate results
        if not observations:
            logger.error("No search results observed")
            return {
                "_success": False,
                "search_results_count": 0,
                "observations": observations,
                "debugUrl": debug_url,
                "sessionUrl": session_url,
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            }

        # We expect to find at least 5 search results
        expected_min_results = 5
        found_results = len(observations)
        success = found_results >= expected_min_results

        logger.info(f"Found {found_results} search results (expected >= {expected_min_results})")

        return {
            "_success": success,
            "search_results_count": found_results,
            "observations": observations,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
        
    except Exception as e:
        logger.error(f"Error in observe_search_results: {str(e)}")
        
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        return {
            "_success": False,
            "error": str(e),
            "error_traceback": traceback.format_exc(),
            "debugUrl": debug_url if 'debug_url' in locals() else None,
            "sessionUrl": session_url if 'session_url' in locals() else None,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
    finally:
        if stagehand:
            await stagehand.close()


# For quick local testing
if __name__ == "__main__":
    import logging
    import os

    os.environ.setdefault("OPENAI_API_KEY", os.getenv("MODEL_API_KEY", ""))
    logging.basicConfig(level=logging.INFO)

    class SimpleLogger:
        def __init__(self):
            self._logs = []

        def info(self, message):
            self._logs.append(message)
            print("INFO:", message)

        def error(self, message):
            self._logs.append(message)
            print("ERROR:", message)

        def get_logs(self):
            return self._logs

    async def main():
        logger = SimpleLogger()
        result = await observe_search_results("gpt-4o-mini", logger)
        print("Result:", result)

    asyncio.run(main()) 