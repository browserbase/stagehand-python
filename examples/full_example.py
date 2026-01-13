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
        # Start a new browser session (returns a session helper bound to a session_id)
        session = await client.sessions.create(
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
            observe_response = await session.observe(
                instruction="find the link to view comments for the top post",
            )

            results = observe_response.data.result
            print(f"Found {len(results)} possible actions")

            if not results:
                print("No actions found")
                return

            # Use the first result
            result = results[0]
            print(f"Acting on: {result.description}")

            # Pass the action to Act
            act_response = await session.act(
                input=result,  # type: ignore[arg-type]
            )
            print(f"Act completed: {act_response.data.result.message}")

            # Extract data from the page
            # We're now on the comments page, so extract the top comment text
            extract_response = await session.extract(
                instruction="extract the text of the top comment on this page",
                schema={
                    "type": "object",
                    "properties": {
                        "commentText": {"type": "string", "description": "The text content of the top comment"},
                        "author": {"type": "string", "description": "The username of the comment author"},
                    },
                    "required": ["commentText"],
                },
            )

            # Get the extracted result
            extracted_result = extract_response.data.result
            print(f"Extracted data: {extracted_result}")

            # Get the author from the extracted data
            author: str = (
                extracted_result.get("author", "unknown") if isinstance(extracted_result, dict) else "unknown"  # type: ignore[union-attr]
            )
            print(f"Looking up profile for author: {author}")

            # Use the Agent to find the author's profile
            # Execute runs an autonomous agent that can navigate and interact with pages
            # Use a longer timeout (5 minutes) since agent execution can take a while
            execute_response = await session.execute(  # pyright: ignore[reportArgumentType]
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
                timeout=300.0,  # 5 minutes
            )

            print(f"Agent completed: {execute_response.data.result.message}")
            print(f"Agent success: {execute_response.data.result.success}")
            print(f"Agent actions taken: {len(execute_response.data.result.actions)}")

        finally:
            # End the session to clean up resources
            await session.end()
            print("Session ended")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
