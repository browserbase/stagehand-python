import asyncio

from evals.init_stagehand import init_stagehand


async def observe_taxes(model_name: str, logger) -> dict:
    """
    This function evaluates finding form inputs on a tax website by:

    1. Initializing Stagehand with the provided model name and logger.
    2. Navigating to a tax estimate website.
    3. Using observe to find all form input elements under the 'Income' section.
    4. Checking if one of the observed elements matches the expected target element.

    Returns a dictionary containing:
      - _success (bool): True if a matching input element is found.
      - expected (str): The expected inner text of the target element.
      - observations (list): The raw observations returned from the observe command.
      - debugUrl (str): Debug URL from the Stagehand initialization (can be None in LOCAL mode).
      - sessionUrl (str): Session URL from the Stagehand initialization (can be None in LOCAL mode).
      - logs (list): Logs collected via the provided logger.
    """
    stagehand = None
    try:
        # Initialize Stagehand and extract URLs from the initialization response
        stagehand, init_response = await init_stagehand(model_name, logger)
        debug_url = init_response.get("debugUrl")
        session_url = init_response.get("sessionUrl")

        # Navigate to the tax estimate website
        logger.info("Navigating to tax estimate website...")
        await stagehand.page.goto("https://file.1040.com/estimate/")

        # Use observe to find form inputs in the 'Income' section
        logger.info("Running observe operation...")
        observations = await stagehand.page.observe(
            "Find all the form input elements under the 'Income' section"
        )

        # If no observations were returned or too few were returned, mark eval as unsuccessful and return early
        if not observations:
            logger.error("No observations returned")
            return {
                "_success": False,
                "observations": observations,
                "debugUrl": debug_url,
                "sessionUrl": session_url,
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            }
        elif len(observations) < 13:
            logger.error(f"Too few observations returned: {len(observations)}")
            return {
                "_success": False,
                "observations": observations,
                "debugUrl": debug_url,
                "sessionUrl": session_url,
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            }

        # Define the expected locator for a specific input element
        expected_locator = "#tpWages"

        # Get the inner text of the expected element
        logger.info(
            f"Getting inner text of expected element with locator: {expected_locator}"
        )
        expected_result = await stagehand.page.locator(
            expected_locator
        ).first.inner_text()

        # Check if any observation matches the expected element
        found_match = False
        for observation in observations:
            try:
                # Get the inner text of the observed element
                observation_result = await stagehand.page.locator(
                    observation["selector"]
                ).first.inner_text()

                # Compare with the expected result
                if observation_result == expected_result:
                    found_match = True
                    logger.info(
                        f"Found matching element with selector: {observation['selector']}"
                    )
                    break
            except Exception as e:
                logger.error(
                    f"Failed to check observation with selector {observation.get('selector')}: {str(e)}"
                )
                continue

        # Return the evaluation results
        return {
            "_success": found_match,
            "expected": expected_result,
            "observations": observations,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
        
    except Exception as e:
        logger.error(f"Error in observe_taxes: {str(e)}")
        
        # More detailed error information
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        # Ensure we return a proper result structure even on exception
        return {
            "_success": False,
            "error": str(e),
            "error_traceback": traceback.format_exc(),
            "debugUrl": None,
            "sessionUrl": None,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
    finally:
        # Clean up and close the Stagehand client
        if stagehand:
            await stagehand.close()


# For quick local testing
if __name__ == "__main__":
    import logging
    import os

    # Ensure required env variables are set for testing
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
        result = await observe_taxes("gpt-4o-mini", logger)
        print("Result:", result)

    asyncio.run(main())
