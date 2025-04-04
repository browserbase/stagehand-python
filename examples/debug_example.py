import asyncio
import logging
import os
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
import json
from dotenv import load_dotenv

from stagehand import Stagehand, StagehandConfig
from stagehand.utils import configure_logging

# Configure logging with cleaner format
configure_logging(
    level=logging.INFO,
    remove_logger_name=True,  # Remove the redundant stagehand.client prefix
    quiet_dependencies=True,   # Suppress httpx and other noisy logs
)

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

console.print(
    Panel.fit(
        "[yellow]Logging Levels:[/]\n"
        "[white]- Set [bold]verbose=0[/] for errors (ERROR)[/]\n"
        "[white]- Set [bold]verbose=1[/] for minimal logs (INFO)[/]\n"
        "[white]- Set [bold]verbose=2[/] for medium logs (WARNING)[/]\n"
        "[white]- Set [bold]verbose=3[/] for detailed logs (DEBUG)[/]",
        title="Verbosity Options",
        border_style="blue",
    )
)

async def main():
    # Build a unified configuration object for Stagehand
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        headless=False,
        dom_settle_timeout_ms=3000,
        model_name="gpt-4o",
        self_heal=True,
        wait_for_captcha_solves=True,
        system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
        # Use verbose=2 for medium-detail logs (1=minimal, 3=debug)
        verbose=2,
    )

    stagehand = Stagehand(
        config=config, 
        server_url=os.getenv("STAGEHAND_SERVER_URL"),
    )

    console.print(f"🌐 [white]Stagehand URL:[/] [url]{stagehand.server_url}[/]")

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

    console.print("\n▶️ [highlight] Performing action:[/] click on the search bar")
    await stagehand.page.act("click on the search bar")
    console.print("✅ [success]Clicked on the search bar[/]")

    # Check if function exists before
    exists_before = await stagehand.page.evaluate("typeof window.getScrollableElementXpaths === 'function'") # true
    console.print(f"\n🔍 getScrollableElementsXpath exists before: {exists_before}")
    
    console.print("\n▶️ [highlight] Performing action:[/] type openai")
    await stagehand.page.keyboard.type("openai")
    console.print("✅ [success]Typed openai[/]")
    
    # Check if function exists after 
    exists_after = await stagehand.page.evaluate("typeof window.getScrollableElementXpaths === 'function'") # true
    console.print(f"🔍 getScrollableElementsXpath exists after: {exists_after}")
    

    console.print("\n▶️ [highlight] Clicking[/] on About link")
    # Click on the "About" link using Playwright
    await stagehand.page.get_by_role("link", name="About", exact=True).click() # works
    console.print("✅ [success]Clicked on About link[/]")

    await asyncio.sleep(2)
    console.print("\n▶️ [highlight] Navigating[/] back to Google")
    await stagehand.page.goto("https://google.com/") # works
    console.print("✅ [success]Navigated back to Google[/]")

    console.print("\n▶️ [highlight] Performing action:[/] search for openai")
    await stagehand.page.act("search for openai") # works
    exists_before = await stagehand.page.evaluate("typeof window.getScrollableElementXpaths === 'function'") # true
    console.print(f"\n🔍 getScrollableElementsXpath exists before: {exists_before}")
    
    await stagehand.page.keyboard.press("Enter") #error
    await asyncio.sleep(5) # moved sleep to after the keyboard press
    exists_before = await stagehand.page.evaluate("typeof window.getScrollableElementXpaths === 'function'") # false
    console.print(f"\n🔍 getScrollableElementsXpath exists before: {exists_before}")

    console.print("\n▶️ [highlight] Performing action:[/] click on the search button")
    await page.act("click on the search button")
    console.print("✅ [success]Performing Action:[/] Action completed successfully")

    console.print("\n▶️ [highlight] Observing page[/] for news button")
    observed = await page.observe("find the news button on the page") # error
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
