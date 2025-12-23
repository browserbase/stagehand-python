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

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
REPRO_INSTRUCTION = (
    "Step 1: Use the goto tool to open https://example.com/.\n"
    "Step 2: After it loads, scroll down and click the 'More information...' link "
    "to open the iana.org page, then report the heading text you see."
)
ERROR_SIGNATURES = [
    "messages.1.content.1.tool_use.caller",
    "Extra inputs are not permitted",
]

# Configure logging with the utility function
configure_logging(
    level=logging.INFO,  # Set to INFO for regular logs, DEBUG for detailed
    quiet_dependencies=True,  # Reduce noise from dependencies
)


def require_env_var(var_name: str) -> str:
    """Fetch a required env var with a helpful error for local runs."""
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"{var_name} is not set. Add it to your .env before running this example."
        )
    return value


async def main():
    # Build a unified configuration object for Stagehand
    config = StagehandConfig(
        env="LOCAL",
        system_prompt="You are a browser automation assistant that helps users navigate websites effectively.",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
        self_heal=True,
        verbose=2,
    )

    # Create a Stagehand client using the configuration object.
    stagehand = Stagehand(config)

    # Initialize - this creates a new session automatically.
    console.print("\n🚀 [info]Initializing Stagehand...[/]")
    await stagehand.init()

    console.print("\n▶️ [highlight] Navigating[/] to Google")
    await stagehand.page.goto("https://google.com/")
    console.print("✅ [success]Navigated to Google[/]")
    
    console.print(
        "\n▶️ [highlight]Using Anthropic CUA agent[/]: reproducing the tool_use caller bug"
    )
    anthropic_api_key = require_env_var("ANTHROPIC_API_KEY")
    agent = stagehand.agent(
        model=ANTHROPIC_MODEL,
        instructions=(
            "You are controlling a fullscreen local browser with the Anthropic computer-use tools. "
            "Read the current page carefully, decide on your next action, and avoid asking follow-up questions."
        ),
        options={"apiKey": anthropic_api_key}
    )
    agent_result = await agent.execute(
        instruction=REPRO_INSTRUCTION,
        max_steps=5,
        auto_screenshot=True,
    )

    console.print(agent_result)
    if agent_result.message and any(
        signature in agent_result.message for signature in ERROR_SIGNATURES
    ):
        console.print(
            "🐛 [error]Reproduced the Anthropic `tool_use.caller` validation error.[/]\n"
            "    Check the logs above for 'Extra inputs are not permitted' to link back to the GitHub issue."
        )
    else:
        console.print(
            "⚠️ [warning]Bug signature not detected in this run. "
            "Re-run the example or tweak the instructions if you need the failing payload."
        )

    console.print("📊 [info]Agent execution result:[/]")
    console.print(f"🎯 Completed: [bold]{'Yes' if agent_result.completed else 'No'}[/]")
    if agent_result.message:
        console.print(f"💬 Message: [italic]{agent_result.message}[/]")
    
    if agent_result.actions:
        console.print(f"🔄 Actions performed: [bold]{len(agent_result.actions)}[/]")
        for i, action in enumerate(agent_result.actions):
            action_type = action.type

            console.print(f"  Action {i+1}: {action_type if action_type else 'Unknown'}")
    
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
