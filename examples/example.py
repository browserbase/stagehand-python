import asyncio
import os
from dotenv import load_dotenv
from stagehand.client import Stagehand

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
    # TODO - create the session, need backend endpoint for this.
    
    # Create a Stagehand client pointing to your existing server/session
    # Make sure you set BROWSERBASE_SESSION_ID, BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID,
    # and optionally OPENAI_API_KEY in your environment or pass directly here.
    stagehand = Stagehand(
        server_url="http://localhost:3000",
        session_id=os.getenv("BROWSERBASE_SESSION_ID"),
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        on_log=log_handler,  # attach the log handler to receive streaming logs
        verbose=2,
    )

    # Ensure the server is reachable
    await stagehand.init()

    print("Server healthcheck passed. Starting actions...")

    # Example: navigate to google.com
    await stagehand.navigate("https://www.google.com")
    print("Navigation complete.")

    # Example: ACT to do something like 'search for openai'
    # This calls the /api/execute with method="act" and args=[{"action":"search for openai"}]
    result = await stagehand.act("search for openai")
    print("Action result:", result)

    # You can observe the DOM or environment after that
    observations = await stagehand.observe({"timeoutMs": 3000})
    print("Observations:", observations)

if __name__ == "__main__":
    asyncio.run(main())