import asyncio
import os
from dotenv import load_dotenv
from stagehand import Stagehand

# Load environment variables from .env file
load_dotenv()

async def main():
    # Create a Stagehand instance with automatic session creation
    stagehand = Stagehand(
        server_url=os.getenv("SERVER_URL"),
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_api_key=os.getenv("OPENAI_API_KEY"),
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

        # # Make observations about the site
        activity = await stagehand.page.observe(
            instruction="find all the links on the page regarding the city of el paso",
            only_visible=True  # Use accessibility tree faster DOM parsing
        )
        print("\nObservations:", activity)
        print("Length of observations:", len(activity))

        print("Click on the first extracted element")
        print(activity[0])
        await stagehand.page.click(activity[0]["selector"])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())