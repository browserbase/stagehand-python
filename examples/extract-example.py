import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand
from pydantic import BaseModel

class ExtractSchema(BaseModel):
    stars: int

# Load environment variables from .env file
load_dotenv()

async def main():
    # Create a Stagehand instance with automatic session creation
    stagehand = Stagehand(
        server_url=os.getenv("STAGEHAND_SERVER_URL"),
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        verbose=2,
        model_name="gpt-4o",  # optional - defaults to server's default
        debug_dom=True,  # optional - defaults to server's default
    )

    # Initialize - this will create a new session
    await stagehand.init()
    print(f"Created new session with ID: {stagehand.session_id}")

    try:

        await stagehand.page.navigate("https://github.com/facebook/react")
        print("Navigation complete.")

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
        data = await stagehand.page.extract(
            instruction="Extract the number of stars for the project",
            schema=extract_schema
        )
        print("\nExtracted stars:", data)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())