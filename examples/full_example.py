"""
Basic example demonstrating the Stagehand Python SDK.

This example shows the full flow of:
1. Starting a browser session
2. Navigating to a webpage
3. Observing to find possible actions
4. Acting on an element
5. Extracting structured data
6. Running an autonomous agent
7. Ending the session

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
        # Start a new browser session (returns a session helper bound to a session_id)
        session = await client.sessions.start(
            model_name="openai/gpt-5-nano",
        )

        print(f"Session started: {session.id}")

        try:
            # Navigate to Hacker News
            await session.navigate(
                url="https://news.ycombinator.com",
            )
            print("Navigated to Hacker News")

            # Observe to find possible actions - looking for the comments link
            observe_stream = await session.observe(
                instruction="find the link to view comments for the top post",
                stream_response=True,
                x_stream_response="true",
            )

            results = await _stream_to_result(observe_stream, "observe")
            results = results if isinstance(results, list) else []
            print(f"Found {len(results)} possible actions")

            if not results:
                print("No actions found")
                return

            # Use the first result
            result = results[0]
            print(f"Acting on: {result.description}")

            # Pass the action to Act
            act_stream = await session.act(
                input=result,  # type: ignore[arg-type]
                stream_response=True,
                x_stream_response="true",
            )
            act_result = await _stream_to_result(act_stream, "act")
            act_message = (
                act_result.get("message")
                if isinstance(act_result, dict)
                else act_result
            )
            print(f"Act completed: {act_message}")

            # Extract data from the page
            # We're now on the comments page, so extract the top comment text
            extract_stream = await session.extract(
                instruction="extract the text of the top comment on this page",
                schema={
                    "type": "object",
                    "properties": {
                        "commentText": {"type": "string", "description": "The text content of the top comment"},
                        "author": {"type": "string", "description": "The username of the comment author"},
                    },
                    "required": ["commentText"],
                },
                stream_response=True,
                x_stream_response="true",
            )

            extracted_result = await _stream_to_result(extract_stream, "extract")
            print(f"Extracted data: {extracted_result}")

            # Get the author from the extracted data
            author: str = (
                extracted_result.get("author", "unknown") if isinstance(extracted_result, dict) else "unknown"  # type: ignore[union-attr]
            )
            print(f"Looking up profile for author: {author}")

            # Use the Agent to find the author's profile
            # Execute runs an autonomous agent that can navigate and interact with pages
            # Use a longer timeout (5 minutes) since agent execution can take a while
            execute_stream = await session.execute(  # pyright: ignore[reportArgumentType]
                execute_options={
                    "instruction": (
                        f"Find any personal website, GitHub, LinkedIn, or other best profile URL for the Hacker News user '{author}'. "
                        f"Click on their username to go to their profile page and look for any links they have shared. "
                        f"Use Google Search with their username or other details from their profile if you dont find any direct links."
                    ),
                    "max_steps": 15,
                },
                agent_config={
                    "model": {
                        "model_name": "openai/gpt-5-nano",
                        "api_key": os.environ.get("MODEL_API_KEY"),
                    },
                    "cua": False,
                },
                stream_response=True,
                x_stream_response="true",
                timeout=300.0,  # 5 minutes
            )

            execute_result = await _stream_to_result(execute_stream, "execute")
            execute_message = (
                execute_result.get("message")
                if isinstance(execute_result, dict)
                else execute_result
            )
            execute_success = (
                execute_result.get("success")
                if isinstance(execute_result, dict)
                else None
            )
            execute_actions = (
                execute_result.get("actions")
                if isinstance(execute_result, dict)
                else None
            )
            print(f"Agent completed: {execute_message}")
            print(f"Agent success: {execute_success}")
            print(f"Agent actions taken: {len(execute_actions or [])}")

        finally:
            # End the session to clean up resources
            await session.end()
            print("Session ended")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
