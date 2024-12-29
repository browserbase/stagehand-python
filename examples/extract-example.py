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
    # TODO - create the session, need backend endpoint for this.
    # the session commands all of the params for the session for stagehand to use

    
    # Create a Stagehand instance, referencing an existing session
    stagehand = Stagehand(
        server_url="http://localhost:3000",
        session_id=os.getenv("BROWSERBASE_SESSION_ID"),
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        on_log=log_handler,
        verbose=2,
    )
    # Initialize the browser
    await stagehand.init()

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
        
        data = await stagehand.extract(
            instruction="Extract the number of stars for the project",
            schema=extract_schema,
            url="https://github.com/facebook/react"
        )
        print("\nExtracted stars:", data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())