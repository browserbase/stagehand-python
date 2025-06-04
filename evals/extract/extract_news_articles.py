import asyncio
from pydantic import BaseModel
from typing import List, Optional

from evals.init_stagehand import init_stagehand
from evals.utils import validate_extraction_result


class Article(BaseModel):
    title: str
    author: Optional[str] = None
    publish_date: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None


class NewsExtraction(BaseModel):
    articles: List[Article]
    total_count: int


async def extract_news_articles(model_name: str, logger, use_text_extract: bool = False):
    """
    Extract structured article data from a news website using the Stagehand client.

    Args:
        model_name (str): Name of the AI model to use.
        logger: A custom logger that provides .error() and .get_logs() methods.
        use_text_extract (bool): Flag to control text extraction behavior.

    Returns:
        dict: A result object containing:
           - _success (bool): Whether the eval was successful.
           - extracted_articles (int): Number of articles extracted.
           - error (Optional[str]): Error message (if any).
           - logs (list): Collected logs from the logger.
           - debugUrl (str): Debug URL.
           - sessionUrl (str): Session URL.
    """
    stagehand = None
    try:
        # Initialize Stagehand
        stagehand, init_response = await init_stagehand(
            model_name, logger, dom_settle_timeout_ms=3000
        )
        debug_url = init_response.get("debugUrl")
        session_url = init_response.get("sessionUrl")

        # Navigate to BBC News (a reliable news source for testing)
        logger.info("Navigating to BBC News...")
        await stagehand.page.goto("https://www.bbc.com/news")
        
        # Wait for content to load
        await asyncio.sleep(5)

        # Extract article data using the simplified API
        logger.info("Extracting news articles...")
        raw_result = await stagehand.page.extract(
            "Extract the main news articles from this page. For each article, get the title, "
            "author (if available), publish date (if available), a brief summary, and category. "
            "Return as JSON with an 'articles' array where each article has fields: "
            "title, author, publish_date, summary, category. Also include a 'total_count' field."
        )
        
        logger.info(f"Raw extraction result type: {type(raw_result)}")
        logger.info(f"Raw extraction result: {raw_result}")
        
        # Validate and process the extraction result
        if not validate_extraction_result(raw_result, ["articles"]):
            error_message = "Extraction did not return valid article data structure."
            logger.error(f"{error_message} Raw result: {raw_result}")
            return {
                "_success": False,
                "error": error_message,
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
                "debugUrl": debug_url,
                "sessionUrl": session_url,
            }

        # Extract articles from result
        if hasattr(raw_result, "model_dump"):
            result_dict = raw_result.model_dump()
        elif isinstance(raw_result, dict):
            result_dict = raw_result
        else:
            error_message = f"Unexpected result type: {type(raw_result)}"
            logger.error(error_message)
            return {
                "_success": False,
                "error": error_message,
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
                "debugUrl": debug_url,
                "sessionUrl": session_url,
            }

        articles = result_dict.get("articles", [])
        total_count = result_dict.get("total_count", len(articles))
        
        logger.info(f"Successfully extracted {len(articles)} articles")

        # Validate that we got meaningful results
        if len(articles) < 3:
            logger.error(f"Too few articles extracted. Expected >= 3, got {len(articles)}")
            return {
                "_success": False,
                "error": f"Too few articles extracted. Expected >= 3, got {len(articles)}",
                "extracted_articles": len(articles),
                "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
                "debugUrl": debug_url,
                "sessionUrl": session_url,
            }

        # Check that articles have required fields
        valid_articles = 0
        for article in articles:
            if isinstance(article, dict) and "title" in article and article["title"]:
                valid_articles += 1

        success = valid_articles >= 3
        logger.info(f"Found {valid_articles} valid articles (expected >= 3)")

        return {
            "_success": success,
            "extracted_articles": len(articles),
            "valid_articles": valid_articles,
            "total_count": total_count,
            "sample_titles": [a.get("title", "No title") for a in articles[:3]],
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
            "debugUrl": debug_url,
            "sessionUrl": session_url,
        }
        
    except Exception as e:
        logger.error(f"Error in extract_news_articles function: {str(e)}")
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
        # Ensure we close the Stagehand client even upon error
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
        result = await extract_news_articles("gpt-4o", logger, use_text_extract=False)
        print("Result:", result)

    asyncio.run(main()) 