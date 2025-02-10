import asyncio
import traceback
from typing import Optional, Any, Dict
from pydantic import BaseModel
from evals.init_stagehand import init_stagehand
from stagehand.schemas import ActOptions, ExtractOptions


class Qualifications(BaseModel):
    degree: Optional[str] = None
    yearsOfExperience: Optional[float] = None  # Representing the number


class JobDetails(BaseModel):
    applicationDeadline: Optional[str] = None
    minimumQualifications: Qualifications
    preferredQualifications: Qualifications


def is_job_details_valid(details: Dict[str, Any]) -> bool:
    """
    Validates that each top-level field in the extracted job details is not None.
    For nested dictionary values, each sub-value must be non-null and a string or a number.
    """
    if not details:
        return False
    for key, value in details.items():
        if value is None:
            return False
        if isinstance(value, dict):
            for v in value.values():
                if v is None or not isinstance(v, (str, int, float)):
                    return False
        elif not isinstance(value, (str, int, float)):
            return False
    return True


async def google_jobs(model_name: str, logger, use_text_extract: bool) -> dict:
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
      - applicationDeadline: The opening date until which applications are accepted.
      - minimumQualifications: An object with degree and yearsOfExperience.
      - preferredQualifications: An object with degree and yearsOfExperience.
      
    Returns a dictionary containing:
      - _success (bool): Whether valid job details were extracted.
      - jobDetails (dict): The extracted job details.
      - debugUrl (str): The debug URL from Stagehand initialization.
      - sessionUrl (str): The session URL from Stagehand initialization.
      - logs (list): Logs collected from the provided logger.
      - error (dict, optional): Error details if an exception was raised.
    """
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

    try:
        await stagehand.page.navigate("https://www.google.com/")
        await asyncio.sleep(3) 
        await stagehand.page.act(ActOptions(action="click on the about page"))
        await stagehand.page.act(ActOptions(action="click on the careers page"))
        await stagehand.page.act(ActOptions(action="input data scientist into role"))
        await stagehand.page.act(ActOptions(action="input new york city into location"))
        await stagehand.page.act(ActOptions(action="click on the search button"))
        await stagehand.page.act(ActOptions(action="click on the first job link"))

        job_details = await stagehand.page.extract(ExtractOptions(
            instruction=(
                "Extract the following details from the job posting: application deadline, "
                "minimum qualifications (degree and years of experience), and preferred qualifications "
                "(degree and years of experience)"
            ),
            schemaDefinition=JobDetails.model_json_schema(),
            useTextExtract=use_text_extract
        ))

        valid = is_job_details_valid(job_details)

        await stagehand.close()

        return {
            "_success": valid,
            "jobDetails": job_details,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else []
        }
    except Exception as e:
        err_message = str(e)
        err_trace = traceback.format_exc()
        logger.error({
            "message": "error in google_jobs function",
            "level": 0,
            "auxiliary": {
                "error": {"value": err_message, "type": "string"},
                "trace": {"value": err_trace, "type": "string"}
            }
        })

        await stagehand.close()

        return {
            "_success": False,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "error": {"message": err_message, "trace": err_trace},
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
        result = await google_jobs("gpt-4o-mini", logger, use_text_extract=False) # TODO - use text extract
        print("Result:", result)
        
    asyncio.run(main()) 