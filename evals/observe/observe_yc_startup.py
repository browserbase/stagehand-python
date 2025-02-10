import asyncio
from evals.init_stagehand import init_stagehand
from stagehand.schemas import ObserveOptions

async def observe_yc_startup(model_name: str, logger) -> dict:
    """
    This function evaluates the YC startups page by:
    
      1. Initializing Stagehand with the provided model name and logger.
      2. Navigating to "https://www.ycombinator.com/companies" and waiting for the page to reach network idle.
      3. Invoking the observe command to locate the container element housing startup information.
      4. Checking against candidate locators to determine if a matching element is found.
      
    Returns a dictionary containing:
      - _success (bool): True if a matching container element is found.
      - matchedLocator (Optional[str]): The candidate locator string that matched.
      - observations (list): The raw observations returned from the observe command.
      - debugUrl (str): Debug URL from the Stagehand initialization.
      - sessionUrl (str): Session URL from the Stagehand initialization.
      - logs (list): Logs collected via the provided logger.
    """
    # Initialize Stagehand and extract URLs from the initialization response
    stagehand, init_response = await init_stagehand(model_name, logger)
    debug_url = (
        init_response.get("debugUrl", {}).get("value")
        if isinstance(init_response.get("debugUrl"), dict)
        else init_response.get("debugUrl")
    )
    session_url = (
        init_response.get("sessionUrl", {}).get("value")
        if isinstance(init_response.get("sessionUrl"), dict)
        else init_response.get("sessionUrl")
    )
    
    # Navigate to the YC companies page and wait until network idle
    await stagehand.page.goto("https://www.ycombinator.com/companies")
    await stagehand.page.wait_for_load_state("networkidle")
    
    # Use the observe command with the appropriate instruction
    observations = await stagehand.page.observe(ObserveOptions(
        instruction="Find the container element that holds links to each of the startup companies. The companies each have a name, a description, and a link to their website."
    ))
    
    # If no observations were returned, mark eval as unsuccessful and return early.
    if not observations:
        await stagehand.close()
        return {
            "_success": False,
            "observations": observations,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else []
        }
    
    # Define candidate locators for the container element.
    possible_locators = [
        "div._section_1pgsr_163._results_1pgsr_343",
        "div._rightCol_1pgsr_592",
    ]
    
    possible_handles = []
    for locator_str in possible_locators:
        locator = stagehand.page.locator(locator_str)
        handle = await locator.element_handle()
        if handle:
            possible_handles.append((locator_str, handle))
    
    # Iterate over each observation to determine if it matches any of the candidate locators.
    found_match = False
    matched_locator = None
    for observation in observations:
        try:
            # Get the first element matching the observation's selector
            observation_locator = stagehand.page.locator(observation["selector"]).first
            observation_handle = await observation_locator.element_handle()
            if not observation_handle:
                continue

            # Compare this observation's element with candidate handles.
            for locator_str, candidate_handle in possible_handles:
                is_same_node = await observation_handle.evaluate(
                    "(node, otherNode) => node === otherNode", candidate_handle
                )
                if is_same_node:
                    found_match = True
                    matched_locator = locator_str
                    break

            if found_match:
                break
        except Exception as e:
            print(f"Warning: Failed to check observation with selector {observation.get('selector')}: {str(e)}")
            continue

    # Cleanup and close the Stagehand client.
    await stagehand.close()
    
    # Return the evaluation results.
    return {
        "_success": found_match,
        "matchedLocator": matched_locator,
        "observations": observations,
        "debugUrl": debug_url,
        "sessionUrl": session_url,
        "logs": logger.get_logs() if hasattr(logger, "get_logs") else []
    }
    
# For quick local testing
if __name__ == "__main__":
    import os
    import asyncio
    import logging
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
        result = await observe_yc_startup("gpt-4o-mini", logger)
        print("Result:", result)
        
    asyncio.run(main()) 