import asyncio
import logging
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from stagehand.client import Stagehand
from stagehand.config import StagehandConfig

# Create a custom theme for consistent styling
custom_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "highlight": "magenta",
        "url": "blue underline",
    }
)

# Create a Rich console instance with our theme
console = Console(theme=custom_theme)

load_dotenv()

# Configure logging with Rich handler
logging.basicConfig(
    level=logging.WARNING,  # Feel free to change this to INFO or DEBUG to see more logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def main():
    # Build a unified configuration object for Stagehand
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        headless=False,
        dom_settle_timeout_ms=3000,
        model_name="claude-3-5-sonnet-latest",
        self_heal=True,
        wait_for_captcha_solves=True,
        act_timeout_ms=60000,  # 60 seconds timeout for actions
        system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
    )

    # Create a Stagehand client using the configuration object.
    stagehand = Stagehand(
        config=config, server_url=os.getenv("STAGEHAND_SERVER_URL"), verbose=2
    )

    # Initialize - this creates a new session automatically.
    console.print("\n🚀 [info]Initializing Stagehand...[/]")
    await stagehand.init()
    page = stagehand.page
    console.print(f"\n[yellow]Created new session:[/] {stagehand.session_id}")
    console.print(
        f"🌐 [white]View your live browser:[/] [url]https://www.browserbase.com/sessions/{stagehand.session_id}[/]"
    )

    await asyncio.sleep(2)

    console.print("\n▶️ [highlight] Navigating[/] to Google")
    await page.goto("https://google.com/")
    console.print("✅ [success]Navigated to Google[/]")

    await stagehand.agentExecute(
        agent_config={
            "provider": "anthropic",
            "model": "claude-3-7-sonnet-20250219",
            "instructions": "You are a helpful assistant that can use a web browser. You are currently on the following page: {page.url()}. Do not ask follow up questions, the user will trust your judgement.",
            "options": {
                "apiKey": os.getenv("MODEL_API_KEY"),
            },
        },
        execute_options={
            "instruction": "Search a nice trip for 2 people to NYC for the last week of May",
            "maxSteps": 10,
        },
    )

    console.print("\n▶️ [highlight] Clicking[/] on About link")
    # Click on the "About" link using Playwright
    await page.get_by_role("link", name="About", exact=True).click()
    console.print("✅ [success]Clicked on About link[/]")

    await asyncio.sleep(2)
    console.print("\n▶️ [highlight] Navigating[/] back to Google")
    await page.goto("https://google.com/")
    console.print("✅ [success]Navigated back to Google[/]")

    console.print("\n▶️ [highlight] Performing action:[/] search for openai")
    await page.act("search for openai")
    await page.keyboard.press("Enter")
    console.print("✅ [success]Performing Action:[/] Action completed successfully")

    console.print("\n▶️ [highlight] Observing page[/] for news button")
    observed = await page.observe("find the news button on the page")
    if len(observed) > 0:
        element = observed[0]
        console.print("✅ [success]Found element:[/] News button")
        console.print("\n▶️ [highlight] Performing action on observed element")
        await page.act(element)
        console.print("✅ [success]Performing Action:[/] Action completed successfully")

    else:
        console.print("❌ [error]No element found[/]")

    console.print("\n▶️ [highlight] Extracting[/] first search result")
    data = await page.extract("extract the first result from the search")
    console.print("📊 [info]Extracted data:[/]")
    console.print_json(f"{data.model_dump_json()}")

    # Close the session
    console.print("\n⏹️ [warning]Closing session...[/]")
    await stagehand.close()
    console.print("✅ [success]Session closed successfully![/]")
    console.rule("[bold]End of Example[/]")


if __name__ == "__main__":
    # Add a fancy header
    console.print(
        "\n",
        Panel.fit(
            "[light_gray]Stagehand 🤘 Python Example[/]",
            border_style="green",
            padding=(1, 10),
        ),
    )
    asyncio.run(main())
