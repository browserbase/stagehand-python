import asyncio
from pydantic import BaseModel
from stagehand.schemas import ExtractOptions
from evals.init_stagehand import init_stagehand
from evals.utils import compare_strings

# Define Pydantic models for validating press release data
class PressRelease(BaseModel):
    title: str
    publish_date: str

class PressReleases(BaseModel):
    items: list[PressRelease]

async def extract_press_releases(model_name: str, logger, use_text_extract: bool):
    """
    Extract press releases from the dummy press releases page using the Stagehand client.
    
    Args:
        model_name (str): Name of the AI model to use.
        logger: A custom logger that provides .error() and .get_logs() methods.
        use_text_extract (bool): Flag to control text extraction behavior.
    
    Returns:
        dict: A result object containing:
           - _success (bool): Whether the eval was successful.
           - error (Optional[str]): Error message (if any).
           - logs (list): Collected logs from the logger.
           - debugUrl (str): Debug URL.
           - sessionUrl (str): Session URL.
    """
    stagehand = None
    debug_url = None
    session_url = None
    try:
        # Initialize Stagehand (mimicking the TS initStagehand)
        stagehand, init_response = await init_stagehand(model_name, logger, dom_settle_timeout_ms=3000)
        debug_url = init_response["debugUrl"]
        session_url = init_response["sessionUrl"]

        # Navigate to the dummy press releases page # TODO - choose a different page
        await stagehand.page.navigate("https://dummy-press-releases.surge.sh/news", wait_until="networkidle")
        # Wait for 5 seconds to ensure content has loaded
        await asyncio.sleep(5)

        # Extract data using Stagehand's extract method.
        # TODO - FAILING - extract is likely timing out
        raw_result = await stagehand.page.extract(
            ExtractOptions(
                instruction="extract the title and corresponding publish date of EACH AND EVERY press releases on this page. DO NOT MISS ANY PRESS RELEASES.",
                schemaDefinition=PressReleases.model_json_schema(),
                useTextExtract=use_text_extract
            )
        )
        print("Raw result:", raw_result)
        # Check that the extraction returned a valid dictionary
        if not raw_result or not isinstance(raw_result, dict):
            error_message = "Extraction did not return a valid dictionary."
            logger.error({"message": error_message, "raw_result": raw_result})
            return {
                "_success": False,
                "error": error_message,
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
                "debugUrl": debug_url,
                "sessionUrl": session_url,
            }

        # Parse the raw result using the defined schema.
        parsed = PressReleases.parse_obj(raw_result)
        items = parsed.items

        # Expected results (from the TS eval)
        expected_length = 28
        expected_first = PressRelease(
            title="UAW Region 9A Endorses Brad Lander for Mayor",
            publish_date="Dec 4, 2024"
        )
        expected_last = PressRelease(
            title="Fox Sued by New York City Pension Funds Over Election Falsehoods",
            publish_date="Nov 12, 2023"
        )

        if len(items) <= expected_length:
            logger.error({
                "message": "Not enough items extracted",
                "expected": f"> {expected_length}",
                "actual": len(items)
            })
            return {
                "_success": False,
                "error": "Not enough items extracted",
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
                "debugUrl": debug_url,
                "sessionUrl": session_url,
            }

        def is_item_match(item: PressRelease, expected: PressRelease) -> bool:
            title_similarity = compare_strings(item.title, expected.title)
            date_similarity = compare_strings(item.publish_date, expected.publish_date)
            return title_similarity >= 0.9 and date_similarity >= 0.9

        found_first = any(is_item_match(item, expected_first) for item in items)
        found_last = any(is_item_match(item, expected_last) for item in items)

        result = {
            "_success": found_first and found_last,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            "debugUrl": debug_url,
            "sessionUrl": session_url,
        }
        await stagehand.close()
        return result
    except Exception as e:
        logger.error({
            "message": "Error in extract_press_releases function",
            "error": str(e)
        })
        return {
            "_success": False,
            "error": str(e),
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            "debugUrl": debug_url,
            "sessionUrl": session_url,
        }
    finally:
        # Ensure we close the Stagehand client even upon error.
        if stagehand:
            await stagehand.close()

# For quick local testing.
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
        result = await extract_press_releases("gpt-4o", logger, use_text_extract=False) # TODO - use text extract
        print("Result:", result)
        
    asyncio.run(main()) 