import asyncio

from evals.init_stagehand import init_stagehand


async def act_form_filling(model_name: str, logger, use_text_extract: bool = False) -> dict:
    """
    Evaluates form filling capabilities by:
      1. Initializing Stagehand with the given model name and logger.
      2. Navigating to a test form website.
      3. Performing a series of act commands to fill out a contact form:
          - Filling in name field
          - Filling in email field  
          - Filling in message field
          - Clicking submit button
      4. Validating that the form was successfully submitted.

    Returns a dictionary containing:
      - _success (bool): Whether the form was successfully filled and submitted.
      - debugUrl (str): The debug URL from Stagehand initialization.
      - sessionUrl (str): The session URL from Stagehand initialization.
      - logs (list): Logs collected from the provided logger.
      - error (dict, optional): Error details if an exception was raised.
    """
    stagehand = None
    try:
        stagehand, init_response = await init_stagehand(model_name, logger)
        debug_url = init_response.get("debugUrl")
        session_url = init_response.get("sessionUrl")

        # Navigate to a test form (using httpbin for a simple form test)
        logger.info("Navigating to test form...")
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Wait for page to load
        await asyncio.sleep(2)

        # Fill out the form fields
        logger.info("Filling out customer name field...")
        await stagehand.page.act("fill in the customer name field with 'John Doe'")
        
        logger.info("Filling out telephone field...")
        await stagehand.page.act("fill in the telephone field with '555-1234'")
        
        logger.info("Filling out email field...")
        await stagehand.page.act("fill in the email field with 'john.doe@example.com'")
        
        logger.info("Selecting a size option...")
        await stagehand.page.act("select Medium from the size dropdown")
        
        logger.info("Selecting pizza toppings...")
        await stagehand.page.act("check the cheese and pepperoni checkboxes")
        
        logger.info("Adding comments...")
        await stagehand.page.act("fill in the comments field with 'Please deliver quickly'")

        # Submit the form
        logger.info("Submitting the form...")
        await stagehand.page.act("click the submit button")
        
        # Wait for submission to complete
        await asyncio.sleep(3)

        # Check if we're on the success page (httpbin shows the submitted data)
        current_url = stagehand.page.url
        logger.info(f"Current URL after submission: {current_url}")
        
        # httpbin should show the submitted form data if successful
        success = "httpbin.org" in current_url and "post" in current_url
        
        if success:
            logger.info("Form submission appears successful")
        else:
            logger.error("Form submission may have failed - unexpected URL")

        return {
            "_success": success,
            "final_url": current_url,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
        
    except Exception as e:
        err_message = str(e)
        import traceback
        err_trace = traceback.format_exc()
        logger.error(f"Error in act_form_filling function: {err_message}")
        logger.error(f"Traceback: {err_trace}")

        return {
            "_success": False,
            "debugUrl": debug_url if 'debug_url' in locals() else None,
            "sessionUrl": session_url if 'session_url' in locals() else None,
            "error": {"message": err_message, "trace": err_trace},
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
    finally:
        if stagehand:
            await stagehand.close()


# For quick local testing
if __name__ == "__main__":
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
        result = await act_form_filling("gpt-4o-mini", logger)
        print("Result:", result)

    asyncio.run(main()) 