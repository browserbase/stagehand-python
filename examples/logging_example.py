"""
Example demonstrating how to run an extract() call with streaming logs enabled
using the remote Browserbase Stagehand service.

Required environment variables:
- BROWSERBASE_API_KEY: Your Browserbase API key
- BROWSERBASE_PROJECT_ID: Your Browserbase project ID
- MODEL_API_KEY: Your OpenAI API key
"""

import os

from stagehand import AsyncStagehand


async def main() -> None:
    # Create client using environment variables
    async with AsyncStagehand(
        browserbase_api_key=os.environ.get("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
        model_api_key=os.environ.get("MODEL_API_KEY"),
    ) as client:
        # Start a new browser session with verbose logging enabled
        session = await client.sessions.create(
            model_name="openai/gpt-5-nano",
            verbose=2,
        )

        print(f"Session started: {session.id}")

        try:
            print("Navigating to https://www.example.com...")
            await session.navigate(url="https://www.example.com")
            print("Navigation complete.")

            print("\nExtracting the page heading with streaming logs...")
            stream = await session.extract(
                instruction="Extract the text of the top-level heading on this page.",
                schema={
                    "type": "object",
                    "properties": {
                        "headingText": {
                            "type": "string",
                            "description": "The text content of the top-level heading",
                        },
                        "subheadingText": {
                            "type": "string",
                            "description": "Optional subheading text below the main heading",
                        },
                    },
                    "required": ["headingText"],
                },
                stream_response=True,
                x_stream_response="true",
            )

            result_payload: object | None = None
            async for event in stream:
                if event.type == "log":
                    print(f"[log] {event.data.message}")
                    continue

                status = event.data.status
                print(f"[system] status={status}")
                if status == "finished":
                    result_payload = event.data.result
                elif status == "error":
                    error_message = event.data.error or "unknown error"
                    raise RuntimeError(f"Stream reported error: {error_message}")

            print("Extract completed successfully!")
            print(f"Payload received: {result_payload}")
        finally:
            await session.end()
            print("\nSession ended.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
