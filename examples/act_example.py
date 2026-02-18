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

from __future__ import annotations

import os

from env import load_example_env

from stagehand import AsyncStagehand


async def _stream_to_result(stream, label: str) -> object | None:
    result_payload: object | None = None
    async for event in stream:
        if event.type == "log":
            print(f"[{label}][log] {event.data.message}")
            continue

        status = event.data.status
        print(f"[{label}][system] status={status}")
        if status == "finished":
            result_payload = event.data.result
        elif status == "error":
            error_message = event.data.error or "unknown error"
            raise RuntimeError(f"{label} stream reported error: {error_message}")

    return result_payload


async def main() -> None:
    load_example_env()
    load_example_env()
    # Create client using environment variables
    # BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID, MODEL_API_KEY
    async with AsyncStagehand(
        browserbase_api_key=os.environ.get("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
        model_api_key=os.environ.get("MODEL_API_KEY"),
    ) as client:
        # Start a new browser session
        session = await client.sessions.start(
            model_name="anthropic/claude-sonnet-4-6",
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
            act_stream = await session.act(
                input="click the 'Learn more' link",  # String instruction
                stream_response=True,
                x_stream_response="true",
            )

            act_result = await _stream_to_result(act_stream, "act")
            result_message = (
                act_result.get("message")
                if isinstance(act_result, dict)
                else act_result
            )
            result_success = (
                act_result.get("success")
                if isinstance(act_result, dict)
                else None
            )
            print("Act completed successfully!")
            print(f"Result: {result_message}")
            print(f"Success: {result_success}")

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
