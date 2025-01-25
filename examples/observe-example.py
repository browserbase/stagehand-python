import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand

# Load environment variables from .env file
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
    # Create a Stagehand instance with automatic session creation
    stagehand = Stagehand(
        server_url=os.getenv("SERVER_URL"),
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        on_log=log_handler,  # attach the log handler to receive streaming logs
        verbose=2,
        model_name="gpt-4o-mini",  # optional - defaults to server's default
        debug_dom=True,  # optional - defaults to server's default
    )

    # Initialize - this will create a new session
    await stagehand.init()
    print(f"Created new session with ID: {stagehand.session_id}")

    try:
        # Navigate to GitHub repository
        await stagehand.page.navigate("https://elpasotexas.ionwave.net/Login.aspx")
        print("Navigation complete.")

        # # Make observations about the repository
        # observations = await stagehand.page.observe(
        #     use_vision=True  # Enable vision to better understand the page layout
        # )
        # print("\nObservations:", observations)

        # Make another observation focusing on recent activity
        activity = await stagehand.page.observe(
            use_accessibility_tree=True  # Use accessibility tree for better semantic understanding
        )
        print("\nObservations:", activity)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())