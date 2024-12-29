import asyncio
import os
from dotenv import load_dotenv
from stagehand.client import Stagehand

load_dotenv()

async def log_handler(log_data: dict):
    """
    Example async log handler. Prints real-time logs from the server.
    """
    if "message" in log_data:
        print(f"🤖 {log_data['message']}")
    else:
        print(f"🤖 LOG: {log_data}")

async def main():
    # Create a Stagehand client - it will create a new session automatically
    stagehand = Stagehand(
        server_url="http://localhost:3000",
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

    # Example: navigate to google.com
    await stagehand.navigate("https://www.google.com")
    print("Navigation complete.")

    # Example: ACT to do something like 'search for openai'
    result = await stagehand.act("search for openai")
    print("Action result:", result)

    # You can observe the DOM or environment after that
    observations = await stagehand.observe({"timeoutMs": 3000})
    print("Observations:", observations)

if __name__ == "__main__":
    asyncio.run(main())