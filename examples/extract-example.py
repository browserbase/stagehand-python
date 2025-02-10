import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand
from stagehand.config import StagehandConfig
from stagehand.schemas import ExtractOptions
from pydantic import BaseModel

class ExtractSchema(BaseModel):
    stars: int

# Load environment variables from .env file
load_dotenv()

async def main():
    # Build a unified Stagehand configuration object
    config = StagehandConfig(
        env="BROWSERBASE" if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID") else "LOCAL",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        debug_dom=True,
        headless=True,
        model_name="gpt-4o",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")}
    )

    # Create a Stagehand client using the configuration object.
    stagehand = Stagehand(config=config, server_url=os.getenv("STAGEHAND_SERVER_URL"), verbose=2)

    # Initialize - this creates a new session.
    await stagehand.init()
    print(f"Created new session with ID: {stagehand.session_id}")

    try:
        await stagehand.page.navigate("https://github.com/facebook/react")
        print("Navigation complete.")

        # Use the ExtractOptions Pydantic model to pass instruction and schema definition
        data = await stagehand.page.extract(
            ExtractOptions(
                instruction="Extract the number of stars for the project",
                schemaDefinition=ExtractSchema.model_json_schema()
            )
        )
        print("\nExtracted stars:", data)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())