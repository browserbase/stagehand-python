import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

# Ensure local stagehand package is used instead of any installed version
sys.path.insert(0, str(Path(__file__).parent.parent))

from stagehand import Stagehand, StagehandConfig, configure_logging

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
    Panel(
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
    # Build a unified configuration object for Stagehand with local browser
    config = StagehandConfig(
        model_name="qwen-turbo",  # Use Alibaba DashScope model for demo
        model_client_options={
            "api_base": os.getenv("ALIBABA_ENDPOINT", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "api_key": os.getenv("ALIBABA_API_KEY"),
            "timeout": 30
        },
        dom_settle_timeout_ms=3000,
        self_heal=True,
        wait_for_captcha_solves=True,
        system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
        local_browser_launch_options={
            "headless": False,  # Set to True for headless mode
            "viewport": {"width": 1280, "height": 720}
        },
        # Use verbose=2 for medium-detail logs (1=minimal, 3=debug)
        verbose=2,
    )

    stagehand = Stagehand(config)

    # Initialize - this creates a local browser session automatically.
    console.print("\n🚀 [info]Initializing Stagehand with local browser...[/]")
    await stagehand.init()
    page = stagehand.page
    
    # Validate LLM configuration
    validation = stagehand.llm.validate_configuration()
    if validation['valid']:
        console.print(f"✓ [success]LLM configured:[/] {validation['configuration']['provider']} - {config.model_name}")
    else:
        console.print("⚠ [warning]LLM configuration issues:[/]", validation['errors'])
    
    console.print("🌐 [white]Local browser session initialized successfully[/]")

    await asyncio.sleep(2)

    console.print("\n▶️ [highlight] Navigating[/] to Google")
    await page.goto("https://google.com/")
    console.print("✅ [success]Navigated to Google[/]")

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
    
    await asyncio.sleep(2)

    console.print("\n▶️ [highlight] Observing page[/] for news button")
    observed = await page.observe("find all articles")
    
    if len(observed) > 0:
        element = observed[0]
        console.print("✅ [success]Found element:[/] News button")
        console.print("\n▶️ [highlight] Performing action on observed element:")
        console.print(element)
        await page.act(element)
        console.print("✅ [success]Performing Action:[/] Action completed successfully")

    else:
        console.print("❌ [error]No element found[/]")

    console.print("\n▶️ [highlight] Extracting[/] first search result")
    data = await page.extract("extract the first result from the search")
    console.print("📊 [info]Extracted data:[/]")
    console.print_json(f"{data.model_dump_json()}")

    # Close the session
    console.print("\n⏹️  [warning]Closing session...[/]")
    await stagehand.close()
    console.print("✅ [success]Session closed successfully![/]")
    console.rule("[bold]End of Example[/]")


if __name__ == "__main__":
    # Add a fancy header
    console.print(
        "\n",
        Panel(
            "[light_gray]Stagehand 🤘 Python Example[/]",
            border_style="green",
            padding=(1, 10),
        ),
    )
    asyncio.run(main())
