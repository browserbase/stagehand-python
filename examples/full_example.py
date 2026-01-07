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

from stagehand import Stagehand


def main() -> None:
    # SDK version for API compatibility (matches TypeScript SDK v3)
    SDK_VERSION = "3.0.6"

    # Create client using environment variables
    # BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID, MODEL_API_KEY
    client = Stagehand(
        browserbase_api_key=os.environ.get("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
        model_api_key=os.environ.get("MODEL_API_KEY"),
    )

    # Start a new browser session
    start_response = client.sessions.start(
        model_name="openai/gpt-5-nano",
        x_language="typescript",
        x_sdk_version=SDK_VERSION,
    )

    session_id = start_response.data.session_id
    print(f"Session started: {session_id}")

    try:
        # Navigate to Hacker News
        client.sessions.navigate(
            id=session_id,
            url="https://news.ycombinator.com",
            frame_id="",  # Empty string for main frame
            x_language="typescript",
            x_sdk_version=SDK_VERSION,
        )
        print("Navigated to Hacker News")

        # Observe to find possible actions - looking for the comments link
        observe_response = client.sessions.observe(
            id=session_id,
            instruction="find the link to view comments for the top post",
            x_language="typescript",
            x_sdk_version=SDK_VERSION,
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
        act_response = client.sessions.act(
            id=session_id,
            input=result,  # type: ignore[arg-type]
            x_language="typescript",
            x_sdk_version=SDK_VERSION,
        )
        print(f"Act completed: {act_response.data.result.message}")

        # Extract data from the page
        # We're now on the comments page, so extract the top comment text
        extract_response = client.sessions.extract(
            id=session_id,
            instruction="extract the text of the top comment on this page",
            schema={
                "type": "object",
                "properties": {
                    "commentText": {
                        "type": "string",
                        "description": "The text content of the top comment"
                    },
                    "author": {
                        "type": "string",
                        "description": "The username of the comment author"
                    }
                },
                "required": ["commentText"]
            },
            x_language="typescript",
            x_sdk_version=SDK_VERSION,
        )

        # Get the extracted result
        extracted_result = extract_response.data.result
        print(f"Extracted data: {extracted_result}")

        # Get the author from the extracted data
        author: str = extracted_result.get("author", "unknown") if isinstance(extracted_result, dict) else "unknown"  # type: ignore[union-attr]
        print(f"Looking up profile for author: {author}")

        # Use the Agent to find the author's profile
        # Execute runs an autonomous agent that can navigate and interact with pages
        # Use a longer timeout (5 minutes) since agent execution can take a while
        execute_response = client.sessions.execute(  # pyright: ignore[reportArgumentType]
            id=session_id,
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
            x_language="typescript",
            x_sdk_version=SDK_VERSION,
            timeout=300.0,  # 5 minutes
        )

        print(f"Agent completed: {execute_response.data.result.message}")
        print(f"Agent success: {execute_response.data.result.success}")
        print(f"Agent actions taken: {len(execute_response.data.result.actions)}")

    finally:
        # End the session to clean up resources
        client.sessions.end(
            id=session_id,
            x_language="typescript",
            x_sdk_version=SDK_VERSION,
        )
        print("Session ended")


if __name__ == "__main__":
    main()
