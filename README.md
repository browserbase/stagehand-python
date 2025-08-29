<div id="toc" align="center" style="margin-bottom: 0;">
  <ul style="list-style: none; margin: 0; padding: 0;">
    <a href="https://stagehand.dev">
      <picture>
        <source media="(prefers-color-scheme: dark)" srcset="media/dark_logo.png" />
        <img alt="Stagehand" src="media/light_logo.png" width="200" style="margin-right: 30px;" />
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
      <source media="(prefers-color-scheme: dark)" srcset="media/dark_license.svg" />
      <img alt="MIT License" src="media/light_license.svg" />
    </picture>
  </a>
  <a href="https://stagehand.dev/slack">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="media/dark_slack.svg" />
      <img alt="Slack Community" src="media/light_slack.svg" />
    </picture>
  </a>
</p>

<p align="center">
If you're looking for the TypeScript implementation, you can find it 
<a href="https://github.com/browserbase/stagehand"> here</a>
</p>

<div align="center" style="display: flex; align-items: center; justify-content: center; gap: 4px; margin-bottom: 0;">
  <b>Vibe code</b>
  <span style="font-size: 1.05em;"> Stagehand with </span>
  <a href="https://director.ai" style="display: flex; align-items: center;">
    <span>Director</span>
  </a>
  <span> </span>
  <picture>
    <img alt="Director" src="media/director_icon.svg" width="25" />
  </picture>
</div>


## Why Stagehand?

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
- **extract** — Extract and validate data from a page using a Pydantic schema.
```python
await stagehand.page.extract("the summary of the first paragraph")
```
- **observe** — Get natural language interpretations to, for example, identify selectors or elements from the page.
```python
await stagehand.page.observe("find the search bar")
```
- **agent** — Execute autonomous multi-step tasks with provider-specific agents (OpenAI, Anthropic, etc.).
```python
await stagehand.agent.execute("book a reservation for 2 people for a trip to the Maldives")
```


## Installation

To get started, simply:

```bash
pip install stagehand
```

> We recommend using [uv](https://docs.astral.sh/uv/) for your package/project manager. If you're using uv can follow these steps:

```bash
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install stagehand
```

### Prerequisites

Stagehand requires a local browser installation. The library uses Playwright to manage browser instances automatically. No additional browser setup is required - Playwright will download the necessary browser binaries on first use.

## Quickstart

```python
import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from stagehand import StagehandConfig, Stagehand

# Load environment variables
load_dotenv()  # Create a .env file or set environment variables in your shell

# Define Pydantic models for structured data extraction
class Company(BaseModel):
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Brief company description")

class Companies(BaseModel):
    companies: list[Company] = Field(..., description="List of companies")
    
async def main():
    # Create configuration with Alibaba ModelScope (DashScope)
    config = StagehandConfig(
        model_name="dashscope/qwen-turbo",
        model_client_options={
            "api_base": os.getenv("ALIBABA_ENDPOINT", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "api_key": os.getenv("ALIBABA_API_KEY")
        },
        local_browser_launch_options={
            "headless": False  # Set to True for headless mode
        }
    )
    
    stagehand = Stagehand(config)
    
    try:
        print("\nInitializing 🤘 Stagehand...")
        # Initialize Stagehand with local browser
        await stagehand.init()

        page = stagehand.page

        await page.goto("https://www.aigrant.com")
        
        # Extract companies using structured schema        
        companies_data = await page.extract(
          "Extract names and descriptions of 5 companies in batch 3",
          schema=Companies
        )
        
        # Display results
        print("\nExtracted Companies:")
        for idx, company in enumerate(companies_data.companies, 1):
            print(f"{idx}. {company.name}: {company.description}")

        observe = await page.observe("the search bar")
        print("\nObserve result:", observe)
        act = await page.act("click on the search bar")
        print("\nAct result:", act)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        # Close the client
        print("\nClosing 🤘 Stagehand...")
        await stagehand.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Options

### Basic Configuration

```python
# OpenAI (default)
config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={
        "api_key": os.getenv("OPENAI_API_KEY")
    }
)

# Anthropic Claude
config = StagehandConfig(
    model_name="claude-3-haiku-20240307",
    model_client_options={
        "api_base": "https://api.anthropic.com",
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    }
)
```

### Custom API Endpoints

Stagehand supports various OpenAI/Anthropic compatible providers:

```python
# Together AI
config = StagehandConfig(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_client_options={
        "api_base": "https://api.together.xyz/v1",
        "api_key": os.getenv("TOGETHER_API_KEY")
    }
)

# Groq
config = StagehandConfig(
    model_name="llama2-70b-4096",
    model_client_options={
        "api_base": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("GROQ_API_KEY")
    }
)

# Local OpenAI-compatible server
config = StagehandConfig(
    model_name="local/custom-model",
    model_client_options={
        "api_base": "http://localhost:8000/v1",
        "api_key": "local-key"
    }
)
```

### Browser Configuration

```python
config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={"api_key": os.getenv("OPENAI_API_KEY")},
    local_browser_launch_options={
        "headless": True,  # Run in headless mode
        "viewport": {"width": 1280, "height": 720},
        "user_data_dir": "./browser_data",  # Persistent browser data
        "args": ["--no-sandbox", "--disable-dev-shm-usage"]  # Additional Chrome args
    }
)
```

## Migration from Browserbase

If you're upgrading from a previous version that used Browserbase, here's how to migrate your configuration:

### Quick Migration Check

Use our migration utility to scan your project:

```bash
# Scan current directory for files needing migration
python docs/migration_utility.py scan .

# Generate configuration examples
python docs/migration_utility.py config openai
```

### Before (Browserbase Configuration)
```python
# Old Browserbase configuration
config = StagehandConfig(
    env="BROWSERBASE",
    api_key="browserbase-api-key",
    project_id="browserbase-project-id",
    model_name="gpt-4o",
    model_api_key="openai-api-key"
)
```

### After (Local Configuration)
```python
# New local configuration
config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_key": "openai-api-key",
        # Optional: specify custom endpoint
        "api_base": "https://api.openai.com/v1"
    },
    local_browser_launch_options={
        "headless": False  # Configure browser options as needed
    }
)
```

### Key Changes
- **Removed**: `env`, `api_key`, `project_id` parameters
- **Replaced**: `model_api_key` with `model_client_options.api_key`
- **Added**: `local_browser_launch_options` for browser configuration
- **Enhanced**: Support for custom API endpoints via `model_client_options.api_base`

### Environment Variables
Update your environment variables:
```bash
# Remove these (no longer needed)
# BROWSERBASE_API_KEY=your-browserbase-key
# BROWSERBASE_PROJECT_ID=your-project-id

# Keep or add these
OPENAI_API_KEY=your-openai-key
# Or for other providers:
# ANTHROPIC_API_KEY=your-anthropic-key
# TOGETHER_API_KEY=your-together-key
```

For a complete migration guide with troubleshooting, see [docs/migration_guide.md](docs/migration_guide.md).

## Documentation

See our full documentation [here](https://docs.stagehand.dev/).

## Cache Actions

You can cache actions in Stagehand to avoid redundant LLM calls. This is particularly useful for actions that are expensive to run or when the underlying DOM structure is not expected to change.

### Using `observe` to preview an action

`observe` lets you preview an action before taking it. If you are satisfied with the action preview, you can run it in `page.act` with no further LLM calls.

```python
# Get the action preview
action_preview = await page.observe("Click the quickstart link")

# action_preview is a JSON-ified version of a Playwright action:
# {
#     "description": "The quickstart link",
#     "method": "click",
#     "selector": "/html/body/div[1]/div[1]/a",
#     "arguments": []
# }

# NO LLM INFERENCE when calling act on the preview
await page.act(action_preview[0])
```

If the website happens to change, `self_heal` will run the loop again to save you from constantly updating your scripts.


## Contributing

At a high level, we're focused on improving reliability, speed, and cost in that order of priority. If you're interested in contributing, reach out on [Slack](https://stagehand.dev/slack), open an issue or start a discussion. 

For more info, check the [Contributing Guide](https://docs.stagehand.dev/examples/contributing).

**Local Development Installation:**

```bash
# Clone the repository
git clone https://github.com/browserbase/stagehand-python.git
cd stagehand-python

# Install in editable mode with development dependencies
pip install -r requirements.txt

# On Windows, you may need to install Playwright browsers
playwright install
```

### Dependencies

Stagehand has minimal dependencies and no longer requires external browser services:

- **Core**: `playwright`, `pydantic`, `python-dotenv`
- **LLM Support**: `openai`, `anthropic`, `litellm`
- **Utilities**: `rich`, `nest-asyncio`

All dependencies are automatically installed with `pip install stagehand`.


## License

MIT License (c) 2025 Browserbase, Inc.
