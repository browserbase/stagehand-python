import asyncio
import os
from dotenv import load_dotenv
from stagehand.client import Stagehand

load_dotenv()

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