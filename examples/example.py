# example.py
import asyncio
from stagehand import Stagehand

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
        api_key="your-key",
        project_id="your-project",
        on_log=log_handler  # Add the log handler to get real-time updates
    )
    # Initialize the browser
    await browser.init()

    print("Browser initialized")

    try:
        # Use exactly like the TypeScript version, but now with streaming logs
        result = await browser.act("Navigate to google.com")
        print("\nAction result:", result)
        
        data = await browser.extract("Get the search results", {
            "results": [{"title": "string", "url": "string"}]
        })
        print("\nExtracted data:", data)
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())