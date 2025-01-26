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
    <strong>NOTE:</strong> This is a Python SDK for Stagehand. Original implementation is in TypeScript and is available <a href="https://github.com/browserbase/stagehand" style="color: blue;">here</a>.
  </div>

---

A Python SDK for [Stagehand](https://stagehand.dev), enabling automated browser control and data extraction.

Stagehand is the easiest way to build browser automations. It is fully compatible with Playwright, offering three simple AI APIs (act, extract, and observe) on top of the base Playwright Page class that provide the building blocks for web automation via natural language. 

You can write all of your Playwright commands as you normally would, while offloading the AI-powered `act/extract/observe` operations to Stagehand hosted on our Stagehand API.


Here's a sample of what you can do with Stagehand:

```python
# Keep your existing Playwright code unchanged
await page.goto("https://docs.stagehand.dev");

# Stagehand AI: Act on the page via Stagehand API
await page.act("click on the 'Quickstart'");

# Stagehand AI: Extract data from the page
from pydantic import BaseModel

class DescriptionSchema(BaseModel):
    description: str

data = await page.extract(
    instruction="extract the description of the page",
    schema=DescriptionSchema
)
description = data.description
```

## Why?
**Stagehand adds determinism to otherwise unpredictable agents.**

While there's no limit to what you could instruct Stagehand to do, our primitives allow you to control how much you want to leave to an AI. It works best when your code is a sequence of atomic actions. Instead of writing a single script for a single website, Stagehand allows you to write durable, self-healing, and repeatable web automation workflows that actually work.

> [!NOTE] 
> `Stagehand` is currently available as an early release, and we're actively seeking feedback from the community. Please join our [Slack community](https://join.slack.com/t/stagehand-dev/shared_invite/zt-2tdncfgkk-fF8y5U0uJzR2y2_M9c9OJA) to stay updated on the latest developments and provide feedback.


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
export STAGEHAND_SERVER_URL="url-of-stagehand-server" 
```

## Usage

Here is a minimal example to get started:

```python
import asyncio
import os
from stagehand.client import Stagehand
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Create a Stagehand client - it will create a new session automatically
    stagehand = Stagehand(
        model_name="gpt-4o",  # optional - defaults to server's default
    )

    # Initialize - this will create a new session
    await stagehand.page.init()
    print(f"Created new session: {stagehand.session_id}")

    # Example: navigate to google.com - from Playwright in Python
    await stagehand.page.goto("https://www.google.com")
    print("Navigation complete.")

    # Example: ACT to do something like 'search for openai'
    # executes remote on a Typescript server and logs are streamed back
    await stagehand.page.act("search for openai")

    # Pure client side Playwright - after searching for OpenAI, click on the News tab
    await stagehand.page.get_by_role("link", name="News", exact=True).first.click()
    print("Clicked on News tab")

    # Close the session (if needed)
    await stagehand.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

- `stagehand_server_url`: The Stagehand server URL (default: http://localhost:3000)
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

