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
    """
    Example async log handler. Prints real-time logs from the server.
    """
    if "message" in log_data:
        print(f"🤖 {log_data['message']}")
    else:
        print(f"🤖 LOG: {log_data}")

async def main():
    # Create a Stagehand instance with automatic session creation
    stagehand = Stagehand(
        server_url="http://localhost:3000",
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        on_log=log_handler,  # attach the log handler to receive streaming logs
        verbose=2,
        model_name="gpt-4o",  # optional - defaults to server's default
        debug_dom=True,  # optional - defaults to server's default
    )

    # Initialize - this will create a new session
    await stagehand.init()
    print(f"Created new session with ID: {stagehand.session_id}")

    try:

        await stagehand.navigate("https://github.com/facebook/react")
        print("Navigation complete.")

        result = await stagehand.act("find the number of stars for the project but dont click on the link")
        print("Action result:", result)

        # Define schema for stars extraction
        # extract_schema = {
        #     "type": "object",
        #     "properties": {
        #         "stars": {
        #             "type": "number",
        #             "description": "the number of stars for the project"
        #         }
        #     },
        #     "required": ["stars"]
        # }

        # we can either use a pydantic model or a json schema via dict
        extract_schema = ExtractSchema
        
        # Extract data using the schema
        data = await stagehand.extract(
            instruction="Extract the number of stars for the project",
            schema=extract_schema
        )
        print("\nExtracted stars:", data)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())