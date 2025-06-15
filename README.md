<div id="toc" align="center">
  <ul style="list-style: none">
    <a href="https://stagehand.dev">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://stagehand.dev/logo-dark.svg" />
        <img alt="Stagehand" src="https://www.stagehand.dev/_next/image?url=%2Flogos%2Fmain-logo.webp&w=384&q=75" width="200" style="margin-right: 30px;" />
      </picture>
    </a>
  </ul>
</div>

<p align="center">
  <strong>The AI Browser Automation Framework</strong><br>
    <a href="https://docs.stagehand.dev">Read the Docs</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/stagehand">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/pypi/v/stagehand.svg?style=for-the-badge" />
      <img alt="PyPI version" src="https://img.shields.io/pypi/v/stagehand.svg?style=for-the-badge" />
    </picture>
  </a>
  <a href="https://github.com/browserbase/stagehand/tree/main?tab=MIT-1-ov-file#MIT-1-ov-file">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://stagehand.dev/api/assets/license?mode=dark" />
      <img alt="MIT License" src="https://stagehand.dev/api/assets/license?mode=light" />
    </picture>
  </a>
  <a href="https://stagehand.dev/slack">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://stagehand.dev/api/assets/slack?mode=dark" />
      <img alt="Slack Community" src="https://stagehand.dev/api/assets/slack?mode=light" />
    </picture>
  </a>
</p>

> Stagehand Python SDK is currently available as an early release, and we're actively seeking feedback from the community. Please join our [Slack community](https://stagehand.dev/slack) to stay updated on the latest developments and provide feedback.  

> We also have a TypeScript SDK available <a href="https://github.com/browserbase/stagehand" >here</a>.

## Why Stagehand?

*Stagehand is the easiest way to build browser automations with AI-powered interactions.*

Most existing browser automation tools either require you to write low-level code in a framework like Selenium, Playwright, or Puppeteer, or use high-level agents that can be unpredictable in production. By letting developers choose what to write in code vs. natural language, Stagehand is the natural choice for browser automations in production.

1. **Choose when to write code vs. natural language**: use AI when you want to navigate unfamiliar pages, and use code ([Playwright](https://playwright.dev/)) when you know exactly what you want to do.

2. **Preview and cache actions**: Stagehand lets you preview AI actions before running them, and also helps you easily cache repeatable actions to save time and tokens.

3. **Computer use models with one line of code**: Stagehand lets you integrate SOTA computer use models from OpenAI and Anthropic into the browser with one line of code.

-----

### TL;DR: Automate the web *reliably* with natural language:

- **act** — Instruct the AI to perform actions (e.g. click a button or scroll).
```python
await stagehand.page.act("click on the 'Quickstart' button")
```
- **extract** — Extract and validate data from a page using a JSON schema (generated either manually or via a Pydantic model).
```python
await stagehand.page.extract("the summary of the first paragraph")
```
- **observe** — Get natural language interpretations to, for example, identify selectors or elements from the DOM.
```python
await stagehand.page.observe("find the search bar")
```
- **agent** — Execute autonomous multi-step tasks with provider-specific agents (OpenAI, Anthropic, etc.).
```python
await stagehand.agent.execute("book a reservation for 2 people for a trip to the Maldives")
```


## Installation:

`pip install stagehand`


## Quickstart

```python
import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl

from stagehand import StagehandConfig, Stagehand
from stagehand.schemas import ExtractOptions

# Load environment variables
load_dotenv()

# Define Pydantic models for structured data extraction
class Company(BaseModel):
    name: str = Field(..., description="Company name")
    url: HttpUrl = Field(..., description="Company URL")

class Companies(BaseModel):
    companies: list[Company] = Field(..., description="List of companies")
    
async def main():
    # Create configuration
    config = StagehandConfig(
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="gpt-4o",
        model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
    )
    
    # Initialize async client
    stagehand = Stagehand(
        env=os.getenv("STAGEHAND_ENV"),
        config=config,
        api_url=os.getenv("STAGEHAND_SERVER_URL"),
    )
    
    try:
        # Initialize the client
        await stagehand.init()
        page = stagehand.page

        await page.goto("https://www.aigrant.com")
        
        # Extract companies using structured schema
        extract_options = ExtractOptions(
            instruction="Extract names and URLs of up to 5 companies in batch 3",
            schema_definition=Companies
        )
        
        companies_data = await page.extract(extract_options)
        
        # Display results
        print("Extracted Companies:")
        for idx, company in enumerate(companies_data.companies, 1):
            print(f"{idx}. {company.name}: {company.url}")

        observe = await page.observe("the link to the company Browserbase")
        print("Observe result:", observe)
        act = await page.act("click the link to the company Browserbase")
        print("Act result:", act)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        # Close the client
        await stagehand.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

See our full documentation [here](https://docs.stagehand.dev/).

## Actions caching

You can cache actions in Stagehand to avoid redundant LLM calls. This is particularly useful for actions that are expensive to run or when the underlying DOM structure is not expected to change.

### Using `observe` to preview an action

`observe` lets you preview an action before taking it. If you are satisfied with the action preview, you can run it in `page.act` with no further LLM calls.

```python
# Get the action preview
action_preview = await page.observe("Click the quickstart link")

# action_preview is a JSON-ified version of a Playwright action:
# {
#     "description": "The quickstart link",
#     "action": "click",
#     "selector": "/html/body/div[1]/div[1]/a",
#     "arguments": []
# }

# NO LLM INFERENCE when calling act on the preview
await page.act(action_preview[0])
```


## Configuration

Stagehand can be configured via environment variables or through a `StagehandConfig` object. Available configuration options include:

- `STAGEHAND_API_URL`: URL of the Stagehand API server.
- `browserbase_api_key`: Your Browserbase API key (`BROWSERBASE_API_KEY`).
- `browserbase_project_id`: Your Browserbase project ID (`BROWSERBASE_PROJECT_ID`).
- `model_api_key`: Your model API key (e.g. OpenAI, Anthropic, etc.) (`MODEL_API_KEY`).
- `verbose`: Verbosity level (default: 1).
  - Level 0: Error logs
  - Level 1: Basic info logs (minimal, maps to INFO level)
  - Level 2: Medium logs including warnings (maps to WARNING level)
  - Level 3: Detailed debug information (maps to DEBUG level)
- `model_name`: Optional model name for the AI (e.g. "gpt-4o").
- `dom_settle_timeout_ms`: Additional time (in ms) to have the DOM settle.
- `debug_dom`: Enable debug mode for DOM operations.
- `stream_response`: Whether to stream responses from the server (default: True).
- `timeout_settings`: Custom timeout settings for HTTP requests.

Example using a unified configuration:

```python
from stagehand import StagehandConfig
import os

config = StagehandConfig(
    env="BROWSERBASE" if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID") else "LOCAL",
    api_key=os.getenv("BROWSERBASE_API_KEY"),
    project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
    debug_dom=True,
    headless=False,
    dom_settle_timeout_ms=3000,
    model_name="gpt-4o-mini",
    model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
    verbose=3  # Set verbosity level: 1=minimal, 2=medium, 3=detailed logs
)
```

## Contributing

First, create and activate a virtual environment to keep your project dependencies isolated:

```bash
# Create a virtual environment
python -m venv stagehand-env

# Activate the environment
# On macOS/Linux:
source stagehand-env/bin/activate
# On Windows:
stagehand-env\Scripts\activate
```

**Local Development Installation:**


```bash
# Clone the repository
git clone https://github.com/browserbase/stagehand-python.git
cd stagehand-python

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```


## License

MIT License (c) 2025 Browserbase, Inc.
