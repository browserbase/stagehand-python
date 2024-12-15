# example.py
import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand
from pydantic import BaseModel

class ExtractSchema(BaseModel):
    stars: int

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
    browser = Stagehand(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="claude-3-5-sonnet-20241022",
        on_log=log_handler  # Add the log handler to get real-time updates
    )
    # Initialize the browser
    await browser.init()

    print("Browser initialized")

    try:

        # Define schema for stars extraction
        extract_schema = {
            "type": "object",
            "properties": {
                "stars": {
                    "type": "number",
                    "description": "the number of stars for the project"
                }
            },
            "required": ["stars"]
        }
        
        data = await browser.extract(
            instruction="Extract the number of stars for the project",
            schema=extract_schema,
            url="https://github.com/facebook/react"
        )
        print("\nExtracted stars:", data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())