# example.py
import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand

# Load environment variables from .env file
load_dotenv()

async def log_handler(log_data: dict):
    # Pretty print the log data - you can customize this to your needs
    if "message" in log_data:
        print(f"🤖 {log_data['message']}")
    elif "error" in log_data:
        print(f"❌ {log_data['error']}")

async def main():
    # Creates instance and automatically manages NextJS server
    stagehand = Stagehand(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        on_log=log_handler  # Add the log handler to get real-time updates
    )
    # Initialize the browser
    await stagehand.init()

    print("Browser initialized")

    try:
        # Use exactly like the TypeScript version, but now with streaming logs
        result = await stagehand.act(action="Search for OpenAI", url="https://google.com")
        print("\nAction result:", result)
        print('-'*100)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())