"""
Example demonstrating calling act() with a string instruction.

This example shows how to use the act() method with a natural language
string instruction instead of an Action object from observe().

The act() method accepts either:
1. A string instruction (demonstrated here): input="click the button"
2. An Action object from observe(): input=action_object

Required environment variables:
- BROWSERBASE_API_KEY: Your Browserbase API key
- BROWSERBASE_PROJECT_ID: Your Browserbase project ID
- MODEL_API_KEY: Your OpenAI API key
"""

import os

from stagehand import AsyncStagehand


async def main() -> None:
    # Create client using environment variables
    # BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID, MODEL_API_KEY
    async with AsyncStagehand(
        browserbase_api_key=os.environ.get("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
        model_api_key=os.environ.get("MODEL_API_KEY"),
    ) as client:
        # Start a new browser session
        session = await client.sessions.create(
            model_name="openai/gpt-5-nano",
        )

        print(f"Session started: {session.id}")

        try:
            # Navigate to example.com
            await session.navigate(
                url="https://www.example.com",
            )
            print("Navigated to example.com")

            # Call act() with a string instruction directly
            # This is the key test - passing a string instead of an Action object
            print("\nAttempting to call act() with string input...")
            act_response = await session.act(
                input="click the 'More information' link",  # String instruction
            )

            print(f"Act completed successfully!")
            print(f"Result: {act_response.data.result.message}")
            print(f"Success: {act_response.data.result.success}")

        except Exception as e:
            print(f"Error: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback

            traceback.print_exc()

        finally:
            # End the session to clean up resources
            await session.end()
            print("\nSession ended")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
