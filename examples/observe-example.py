import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand
from stagehand.config import StagehandConfig
from stagehand.schemas import ObserveOptions

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
        model_name="gpt-4o-mini",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")}
    )

    # Create a Stagehand client using the configuration object.
    stagehand = Stagehand(config=config, server_url=os.getenv("SERVER_URL"), verbose=2)

    # Initialize - this creates a new session.
    await stagehand.init()
    print(f"Created new session with ID: {stagehand.session_id}")

    try:
        # Navigate to the desired page
        await stagehand.page.navigate("https://elpasotexas.ionwave.net/Login.aspx")
        print("Navigation complete.")

        # Use ObserveOptions for detailed instructions
        options = ObserveOptions(
            instruction="find all the links on the page regarding the city of el paso",
            only_visible=True
        )
        activity = await stagehand.page.observe(options)
        print("\nObservations:", activity)
        print("Length of observations:", len(activity))

        print("Click on the first extracted element")
        if activity:
            print(activity[0])
            await stagehand.page.click(activity[0]["selector"])
        else:
            print("No elements found")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())