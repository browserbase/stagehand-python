# Stagehand Python SDK

A Python SDK for BrowserBase Stagehand, enabling automated browser control and data extraction.

## Installation

```bash
pip install stagehand-py
```

## Quickstart

Before running your script, make sure you have exported the necessary environment variables:

```bash
export BROWSERBASE_API_KEY="your-api-key"
export BROWSERBASE_PROJECT_ID="your-project-id"
export OPENAI_API_KEY="your-openai-api-key"
export SERVER_URL="url-of-stagehand-server" 
```

## Usage

Here is a minimal example to get started:

```python
import asyncio
import os
from stagehand import Stagehand
from dotenv import load_dotenv

load_dotenv()

async def log_handler(log_data: dict):
    """
    Example async log handler. Prints real-time logs from the server.
    """
    if "message" in log_data:
        print(f"🤖 {log_data['message']}")
    else:
        print(f"🤖 LOG: {log_data}")

async def main():
    # Create a Stagehand client - it will create a new session automatically
    stagehand = Stagehand(
        server_url=os.getenv("SERVER_URL"),
        browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        on_log=log_handler,  # attach the log handler to receive streaming logs
        verbose=2,
        model_name="gpt-4o",  # optional - defaults to server's default
        dom_settle_timeout_ms=3000,  # optional - defaults to server's default
        debug_dom=True,  # optional - defaults to server's default
    )


    # Initialize - this will create a new session
    await stagehand.init()
    print(f"Created new session: {stagehand.session_id}")

    # Example: navigate to google.com
    await stagehand.navigate("https://www.google.com")
    print("Navigation complete.")

    # Example: ACT to do something like 'search for openai'
    result = await stagehand.act("search for openai")
    print("Action result:", result)

    # Close the session (if needed)
    # await stagehand.close()
if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

- `server_url`: The Stagehand server URL (default: http://localhost:3000)
- `browserbase_api_key`: Your BrowserBase API key (can also be set via BROWSERBASE_API_KEY environment variable)
- `browserbase_project_id`: Your BrowserBase project ID (can also be set via BROWSERBASE_PROJECT_ID environment variable)
- `openai_api_key`: Your OpenAI API key (can also be set via OPENAI_API_KEY environment variable)
- `verbose`: Verbosity level (default: 1)
- `model_name`: (optional) Model name to use for the conversation
- `dom_settle_timeout_ms`: (optional) Additional time for the DOM to settle
- `debug_dom`: (optional) Whether or not to enable DOM debug mode

## Features

- Automated browser control with natural language commands
- Data extraction with schema validation (either pydantic or JSON schema)
- Async/await support

## Requirements

- Python 3.7+
- httpx
- asyncio
- pydantic
- python-dotenv (optional if using a .env file)

## License

MIT License (c) Browserbase, Inc.