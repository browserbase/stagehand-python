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

async def log_handler(log_data: dict):
    """
    Enhanced async log handler that shows more detailed server logs.
    """
    # Print the full log data structure
    if "type" in log_data:
        log_type = log_data["type"]
        data = log_data.get("data", {})
        
        if log_type == "system":
            print(f"🔧 SYSTEM: {data}")
        elif log_type == "log":
            print(f"📝 LOG: {data}")
        else:
            print(f"ℹ️ OTHER [{log_type}]: {data}")
    else:
        # Fallback for any other format
        print(f"🤖 RAW LOG: {log_data}")

async def main():
    # Create a Stagehand client - it will create a new session automatically
    stagehand = Stagehand(
        server_url=os.getenv("SERVER_URL"),
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        on_log=log_handler,  # attach the log handler to receive streaming logs
        verbose=2,
        model_name="gpt-4o",  # optional - defaults to server's default
        dom_settle_timeout_ms=3000,  # optional - defaults to server's default
        debug_dom=True,  # optional - defaults to server's default
    )

    # Initialize - this will create a new session since we didn't provide session_id
    await stagehand.init()
    print(f"Created new session with ID: {stagehand.session_id}")

    await asyncio.sleep(1)

    # SERVER side playwright page in TS - navigate FIRST 
    # Need to inject scripts into the browsers current context's DOM from TS first
    await stagehand.page.navigate("https://news.ycombinator.com/")
    print("Navigation complete server side.")
    
    # Wait 10 seconds
    await asyncio.sleep(5)
    print("Waited 5 seconds")

    # CLIENT side Playwright page in Python - navigate
    await stagehand.page.goto("https://www.google.com")
    print("Navigation complete client side.")

    # Hosted Stagehand - ACT to do something like 'search for openai'
    result = await stagehand.page.act("type 'openai' into the search bar")
    print("Action result:", result)

    await asyncio.sleep(1)

    result = await stagehand.page.act("click the search button")
    print("Action result:", result)

    # Pure client side Playwright - after searching for OpenAI, click on the News tab
    await stagehand.page.get_by_role("link", name="News", exact=True).first.click()
    print("Clicked on News tab")


if __name__ == "__main__":
    asyncio.run(main())