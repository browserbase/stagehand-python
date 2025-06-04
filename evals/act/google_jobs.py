import asyncio
import traceback
from typing import Any, Optional, Dict

from pydantic import BaseModel

from evals.init_stagehand import init_stagehand


class Qualifications(BaseModel):
    degree: Optional[str] = None
    years_of_experience: Optional[float] = None  # Representing the number


class JobDetails(BaseModel):
    application_deadline: Optional[str] = None
    minimum_qualifications: Qualifications
    preferred_qualifications: Qualifications


def is_job_details_valid(details: Dict[str, Any] | JobDetails) -> bool:
    """
    Validates that the extracted job details are in the correct format.
    application_deadline is allowed to be None.
    For qualifications, degree and years_of_experience are allowed to be None.
    """
    if not details:
        return False
    
    # Convert Pydantic model to dict if needed
    if hasattr(details, "model_dump"):
        details_dict = details.model_dump()
    else:
        details_dict = details
    
    # application_deadline is allowed to be None
    # minimum_qualifications and preferred_qualifications must exist
    required_fields = ["minimum_qualifications", "preferred_qualifications"]
    for field in required_fields:
        if field not in details_dict or details_dict[field] is None:
            return False
    
    # For qualifications, check that they're dictionaries but allow None values
    for field in ["minimum_qualifications", "preferred_qualifications"]:
        if not isinstance(details_dict[field], dict):
            return False
        
        # Each qualification should have the expected structure
        quals = details_dict[field]
        if "degree" not in quals or "years_of_experience" not in quals:
            return False
            
        # Values can be None or proper types
        for k, v in quals.items():
            if v is not None and not isinstance(v, (str, int, float)):
                return False
    
    return True


async def google_jobs(model_name: str, logger, use_text_extract: bool = False) -> dict:
    """
    Evaluates a Google jobs flow by:
      1. Initializing Stagehand with the given model name and logger.
      2. Navigating to "https://www.google.com/".
      3. Performing a series of act commands representing UI interactions:
          - Clicking on the about page
          - Clicking on the careers page
          - Inputting "data scientist" into the role field
          - Inputting "new york city" into the location field
          - Clicking on the search button
          - Clicking on the first job link
      4. Extracting job posting details using an AI-driven extraction schema.

    The extraction schema requires:
      - application_deadline: The opening date until which applications are accepted.
      - minimum_qualifications: An object with degree and years_of_experience.
      - preferred_qualifications: An object with degree and years_of_experience.

    Returns a dictionary containing:
      - _success (bool): Whether valid job details were extracted.
      - jobDetails (dict): The extracted job details.
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

        logger.info("Navigating to Google...")
        await stagehand.page.goto("https://www.google.com/")
        await asyncio.sleep(3)
        
        logger.info("Clicking on the about page...")
        await stagehand.page.act("click on the about page")
        
        logger.info("Clicking on the careers page...")
        await stagehand.page.act("click on the careers page")
        
        logger.info("Inputting data scientist into role field...")
        await stagehand.page.act("input data scientist into role")
        
        logger.info("Inputting new york city into location field...")
        await stagehand.page.act("input new york city into location")
        
        logger.info("Clicking on the search button...")
        await stagehand.page.act("click on the search button")
        
        logger.info("Clicking on the first job link...")
        await stagehand.page.act("click on the first job link")

        logger.info("Extracting job details...")
        # Note: The modern API may have changed how schema is passed
        # Using the extraction pattern from the examples
        job_details = await stagehand.page.extract(
            "Extract the following details from the job posting: "
            "application deadline, minimum qualifications "
            "(degree and years of experience), and preferred qualifications "
            "(degree and years of experience). Return as JSON with fields: "
            "application_deadline, minimum_qualifications, preferred_qualifications. "
            "Each qualification should have degree and years_of_experience fields."
        )

        logger.info(f"Extracted job details: {job_details}")
        
        # Validate the extracted data
        valid = is_job_details_valid(job_details)
        logger.info(f"Job details validation result: {valid}")

        return {
            "_success": valid,
            "jobDetails": job_details.model_dump() if hasattr(job_details, "model_dump") else job_details,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
        
    except Exception as e:
        err_message = str(e)
        err_trace = traceback.format_exc()
        logger.error(f"Error in google_jobs function: {err_message}")
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
        result = await google_jobs("gpt-4o-mini", logger, use_text_extract=False)
        print("Result:", result)

    asyncio.run(main())
