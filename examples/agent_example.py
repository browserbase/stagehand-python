import asyncio
import logging
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from stagehand import Stagehand, StagehandConfig, configure_logging

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

# Configure logging with the utility function
configure_logging(
    level=logging.INFO,  # Set to INFO for regular logs, DEBUG for detailed
    quiet_dependencies=True,  # Reduce noise from dependencies
)

async def main():
    # Build a unified configuration object for Stagehand
    config = StagehandConfig(
        env="BROWSERBASE",
        # env="LOCAL",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="gpt-4o",
        self_heal=True,
        system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
        verbose=2,
    )

    # Create a Stagehand client using the configuration object.
    stagehand = Stagehand(config)

    # Initialize - this creates a new session automatically.
    console.print("\n🚀 [info]Initializing Stagehand...[/]")
    await stagehand.init()
    if stagehand.env == "BROWSERBASE":    
        console.print(f"\n[yellow]Created new session:[/] {stagehand.session_id}")
        console.print(
            f"🌐 [white]View your live browser:[/] [url]https://www.browserbase.com/sessions/{stagehand.session_id}[/]"
        )

    console.print("\n▶️ [highlight] Navigating[/] to Google")
    await stagehand.page.goto("https://google.com/")
    console.print("✅ [success]Navigated to Google[/]")
    
    console.print("\n▶️ [highlight] Using Agent to perform a task[/]: playing a game of 2048")
    agent = stagehand.agent(
        model="gemini-2.5-computer-use-preview-10-2025",
        instructions="You are a helpful web navigation assistant that helps users find information. You are currently on the following page: google.com. Do not ask follow up questions, the user will trust your judgement.",
        options={"apiKey": os.getenv("GEMINI_API_KEY")}
    )
    agent_result = await agent.execute(
        instruction="Play a game of 2048",
        max_steps=20,
        auto_screenshot=True,
    )

    console.print("📊 [info]Agent execution result:[/]")
    console.print(f"✅ Success: [bold]{'Yes' if agent_result.success else 'No'}[/]")
    console.print(f"🎯 Completed: [bold]{'Yes' if agent_result.completed else 'No'}[/]")
    if agent_result.message:
        console.print(f"💬 Message: [italic]{agent_result.message}[/]")
    
    if agent_result.actions:
        console.print(f"🔄 Actions performed: [bold]{len(agent_result.actions)}[/]")
        for i, action in enumerate(agent_result.actions):
            console.print(f"  Action {i+1}: {action.get('type', 'Unknown')} - {action.get('description', 'No description')}")
    
    # For debugging, you can also print the full JSON
    console.print("[dim]Full response JSON:[/]")
    console.print_json(f"{agent_result.model_dump_json()}")

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
            "[light_gray]Stagehand 🤘 Agent Example[/]",
            border_style="green",
            padding=(1, 10),
        ),
    )
    asyncio.run(main()) 