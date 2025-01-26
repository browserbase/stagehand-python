<div id="toc" align="center">
  <ul style="list-style: none">
    <a href="https://stagehand.dev">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://stagehand.dev/logo-dark.svg" />
        <img alt="Stagehand" src="https://stagehand.dev/logo-light.svg" />
      </picture>
    </a>
  </ul>
</div>

<p align="center">
  An AI web browsing framework focused on simplicity and extensibility.<br>
</p>

<p align="center">
  <a href="https://pypi.org/project/stagehand-py">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/pypi/v/stagehand-py.svg?style=for-the-badge" />
      <img alt="PyPI version" src="https://img.shields.io/pypi/v/stagehand-py.svg?style=for-the-badge" />
    </picture>
  </a>
  <a href="https://github.com/browserbase/stagehand/tree/main?tab=MIT-1-ov-file#MIT-1-ov-file">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://stagehand.dev/api/assets/license?mode=dark" />
      <img alt="MIT License" src="https://stagehand.dev/api/assets/license?mode=light" />
    </picture>
  </a>
  <a href="https://join.slack.com/t/stagehand-dev/shared_invite/zt-2tdncfgkk-fF8y5U0uJzR2y2_M9c9OJA">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://stagehand.dev/api/assets/slack?mode=dark" />
      <img alt="Slack Community" src="https://stagehand.dev/api/assets/slack?mode=light" />
    </picture>
  </a>
</p>


  <div class="note" style="background-color: #808096; border-left: 5px solid #ffeb3b; padding: 15px; margin: 10px 0; color: white;">
    <strong>NOTE:</strong> This is a Python SDK for Stagehand. Original implementation is in TypeScript and is available <a href="https://stagehand.dev" style="color: blue;">here</a>.
  </div>

# Stagehand Python SDK

A Python SDK for Stagehand, enabling automated browser control and data extraction.

Stagehand is a natural AI extension to Playwright. You can write all of your PLaywright commands as you normally would.

Offload the AI-powered `act/extract/observe` to Stagehand.

## Installation```bash
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
from stagehand.client import Stagehand
from dotenv import load_dotenv

load_dotenv()

async def log_handler(log_data: dict):
    """
    Enhanced async log handler that shows more detailed server logs.
    """
    # Print the full log data structure
    if "type" in log_data:
        log_type = log_data["type"]
        data = log_data.get("data", {})
        
        if log_type == "system":
            print(f"🔧 SYSTEM: {data}")
        elif log_type == "log":
            print(f"📝 LOG: {data}")
        else:
            print(f"ℹ️ OTHER [{log_type}]: {data}")
    else:
        # Fallback for any other format
        print(f"🤖 RAW LOG: {log_data}")

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
    await stagehand.page.init()
    print(f"Created new session: {stagehand.session_id}")

    # Example: navigate to google.com
    await stagehand.page.navigate("https://www.google.com")
    print("Navigation complete.")

    # Example: ACT to do something like 'search for openai'
    result = await stagehand.page.act("search for openai")
    print("Action result:", result)

    # Close the session (if needed)
    await stagehand.close()
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
- Extension of Playwright - run playwright commands normally, with act/extract/observe offloaded to an API

## Requirements

- Python 3.7+
- httpx
- asyncio
- pydantic
- python-dotenv (optional if using a .env file)

## License

MIT License (c) Browserbase, Inc.

