import asyncio
import os

from pydantic import BaseModel

from evals.init_stagehand import init_stagehand
from evals.utils import compare_strings


# Define Pydantic models for validating press release data
class PressRelease(BaseModel):
    title: str
    publish_date: str


class PressReleases(BaseModel):
    items: list[PressRelease]


async def extract_press_releases(model_name: str, logger, use_text_extract: bool = False):
    """
    Extract press releases from the dummy press releases page using the Stagehand
    client.

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
    try:
        # Initialize Stagehand (mimicking the TS initStagehand)
        stagehand, init_response = await init_stagehand(
            model_name, logger, dom_settle_timeout_ms=3000
        )
        debug_url = init_response.get("debugUrl")
        session_url = init_response.get("sessionUrl")

        # Navigate to the dummy press releases page
        logger.info("Navigating to press releases page...")
        await stagehand.page.goto("https://dummy-press-releases.surge.sh/news")
        
        # Wait for 5 seconds to ensure content has loaded
        await asyncio.sleep(5)

        # Extract data using Stagehand's extract method with simplified API
        logger.info("Extracting press releases...")
        raw_result = await stagehand.page.extract(
            "Extract the title and corresponding publish date of EACH AND EVERY "
            "press releases on this page. DO NOT MISS ANY PRESS RELEASES. "
            "Return as JSON with an 'items' array, where each item has 'title' and 'publish_date' fields."
        )
        
        logger.info(f"Raw extraction result: {raw_result}")
        
        # Get the items list from the raw_result, which could be a dict or a PressReleases object
        if isinstance(raw_result, PressReleases):
            items = raw_result.items
        elif hasattr(raw_result, "model_dump"):
            # It's a Pydantic model, get the dict representation
            result_dict = raw_result.model_dump()
            if "items" in result_dict:
                items = [PressRelease(**item) for item in result_dict["items"]]
            else:
                raise ValueError("No 'items' field found in extraction result")
        elif isinstance(raw_result, dict) and "items" in raw_result:
            # Parse the raw result using the defined schema if it's a dictionary
            items = [PressRelease(**item) for item in raw_result["items"]]
        else:
            error_message = "Extraction did not return valid press releases data."
            logger.error(f"{error_message} Raw result: {raw_result}")
            return {
                "_success": False,
                "error": error_message,
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
                "debugUrl": debug_url,
                "sessionUrl": session_url,
            }

        logger.info(f"Successfully extracted {len(items)} press releases")

        # Expected results (from the TS eval)
        expected_length = 28
        expected_first = PressRelease(
            title="UAW Region 9A Endorses Brad Lander for Mayor",
            publish_date="Dec 4, 2024",
        )
        expected_last = PressRelease(
            title="Fox Sued by New York City Pension Funds Over Election Falsehoods",
            publish_date="Nov 12, 2023",
        )

        if len(items) <= expected_length:
            logger.error(f"Not enough items extracted. Expected > {expected_length}, got {len(items)}")
            return {
                "_success": False,
                "error": f"Not enough items extracted. Expected > {expected_length}, got {len(items)}",
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

        logger.info(f"Found expected first item: {found_first}")
        logger.info(f"Found expected last item: {found_last}")

        result = {
            "_success": found_first and found_last,
            "extracted_count": len(items),
            "found_first": found_first,
            "found_last": found_last,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            "debugUrl": debug_url,
            "sessionUrl": session_url,
        }
        return result
        
    except Exception as e:
        logger.error(f"Error in extract_press_releases function: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "_success": False,
            "error": str(e),
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            "debugUrl": debug_url if 'debug_url' in locals() else None,
            "sessionUrl": session_url if 'session_url' in locals() else None,
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
        result = await extract_press_releases("gpt-4o", logger, use_text_extract=False)
        print("Result:", result)

    asyncio.run(main())
