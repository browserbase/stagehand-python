import asyncio
import os
import logging
from dotenv import load_dotenv
from stagehand.client import Stagehand

load_dotenv()
# Configure logging at the start of the script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def main():

    try:
        # Create a Stagehand client - it will create a new session automatically
        stagehand = Stagehand(
            server_url=os.getenv("SERVER_URL"),
            browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
            browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            verbose=2,
            model_name="gpt-4o",  # optional - defaults to server's default
            dom_settle_timeout_ms=3000,  # optional - defaults to server's default
            debug_dom=True,  # optional - defaults to server's default
        )

        # Initialize - this will create a new session since we didn't provide session_id
        await stagehand.init()
        print(f"Created new session with ID: {stagehand.session_id}")

        await stagehand.page.goto("https://news.ycombinator.com/")

        await asyncio.sleep(5)

        # await stagehand.page.goto("https://news.ycombinator.com/")
        await stagehand.page.navigate("https://www.google.com")
        print("Navigation complete client side.")

        await asyncio.sleep(5)

        # await stagehand.page.goto("https://news.ycombinator.com/")

        print("Clicking on About link")
        # Click on the "About" link using Playwright's get_by_role
        await stagehand.page.get_by_role("link", name="About", exact=True).click()
        print("Clicked on About link")

        await asyncio.sleep(5)

        # SERVER side playwright page navigation
        # await stagehand.page.navigate("https://news.ycombinator.com/")
        await stagehand.page.navigate("https://www.google.com")
        print("Navigation complete server side.")

        await asyncio.sleep(2)
        
        # CLIENT side Playwright page in Python - navigate
        # await stagehand.page.goto("https://www.google.com")
        # await stagehand.page.goto("https://news.ycombinator.com/")
        # print("Navigation complete client side.")

        # Hosted Stagehand - ACT to do something like 'search for openai'
        await stagehand.page.act("type 'openai' into the search bar")

        await stagehand.page.act("click the search button")

        await asyncio.sleep(5)
        print("Clicking on search button")

        # Pure client side Playwright - after searching for OpenAI, click on the News tab
        await stagehand.page.get_by_role("link", name="News", exact=True).first.click()
        print("Clicked on News tab")
    except Exception as e:
        print(f"An error occurred in the example: {e}")


if __name__ == "__main__":
    asyncio.run(main())