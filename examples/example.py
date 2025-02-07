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
            model_api_key=os.getenv("OPENAI_API_KEY"),
            verbose=2,
            model_name="gpt-4o",  # optional - defaults to server's default
            dom_settle_timeout_ms=3000,  # optional - defaults to server's default
            debug_dom=True,  # optional - defaults to server's default
        )

        # Initialize - this will create a new session since we didn't provide session_id
        await stagehand.init()
        print(f"Created new session with ID: {stagehand.session_id}")

        print('EXAMPLE: You can navigate to any website using the local or remote Playwright.')

        await stagehand.page.goto("https://news.ycombinator.com/")
        print("Navigation complete with local Playwright.")

        await stagehand.page.navigate("https://www.google.com")
        print("Navigation complete with remote Playwright.")


        print("EXAMPLE: Clicking on About link using local Playwright's get_by_role")
        # Click on the "About" link using Playwright
        await stagehand.page.get_by_role("link", name="About", exact=True).click()
        print("Clicked on About link")

        await asyncio.sleep(2)

        await stagehand.page.navigate("https://www.google.com")
        
        # Hosted Stagehand API - ACT to do something like 'search for openai'
        await stagehand.page.act("search for openai")
        
        print("EXAMPLE: Find the XPATH of the button 'News' using Stagehand API")
        xpaths = await stagehand.page.observe("find the button 'News'", only_visible=True)
        if len(xpaths) > 0:
            element = xpaths[0]
            print("EXAMPLE: Click on the button 'News' using local Playwright.")
            await stagehand.page.click(element["selector"])
        else:
            print("No element found")


    except Exception as e:
        print(f"An error occurred in the example: {e}")


if __name__ == "__main__":
    asyncio.run(main())