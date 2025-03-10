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
  <strong>NOTE:</strong> This is a Python SDK for Stagehand. The original implementation is in TypeScript and is available <a href="https://github.com/browserbase/stagehand" style="color: blue;">here</a>.
</div>

---

Stagehand is the easiest way to build browser automations with AI-powered interactions. It extends the Playwright API with three powerful AI primitives:

- **act** — Instruct the AI to perform actions (e.g. click a button or scroll).
- **extract** — Extract and validate data from a page using a JSON schema (generated either manually or via a Pydantic model).
- **observe** — Get natural language interpretations to, for example, identify selectors or elements from the DOM.
## Pydantic Schemas

Stagehand uses Pydantic models to define the options for AI commands:

- **ActOptions**  
  The `ActOptions` model takes an `action` field that tells the AI what to do on the page, plus optional fields such as `useVision` and `variables`:
  ```python
  from stagehand.schemas import ActOptions
  
  # Example:
  await page.act(ActOptions(action="click on the 'Quickstart' button"))
  ```

- **ObserveOptions**  
  The `ObserveOptions` model lets you find elements on the page using natural language. The `onlyVisible` option helps limit the results:
  ```python
  from stagehand.schemas import ObserveOptions
  
  # Example:
  await page.observe(ObserveOptions(instruction="find the button labeled 'News'", onlyVisible=True))
  ```

- **ExtractOptions**  
  The `ExtractOptions` model extracts structured data from the page. Pass your instructions and a schema defining your expected data format. **Note:** If you are using a Pydantic model for the schema, call its `.model_json_schema()` method to ensure JSON serializability.
  ```python
  from stagehand.schemas import ExtractOptions
  from pydantic import BaseModel
  
  class DescriptionSchema(BaseModel):
      description: str
  
  # Example:
  data = await page.extract(
      ExtractOptions(
          instruction="extract the description of the page",
          schemaDefinition=DescriptionSchema.model_json_schema()
      )
  )
  description = data.get("description") if isinstance(data, dict) else data.description
  ```

## Why?
**Stagehand adds determinism to otherwise unpredictable agents.**

While there's no limit to what you could instruct Stagehand to do, our primitives allow you to control how much you want to leave to an AI. It works best when your code is a sequence of atomic actions. Instead of writing a single script for a single website, Stagehand allows you to write durable, self-healing, and repeatable web automation workflows that actually work.

> [!NOTE] 
> `Stagehand` is currently available as an early release, and we're actively seeking feedback from the community. Please join our [Slack community](https://join.slack.com/t/stagehand-dev/shared_invite/zt-2tdncfgkk-fF8y5U0uJzR2y2_M9c9OJA) to stay updated on the latest developments and provide feedback.


## Installation

Install the Python package via pip:

```bash
pip install stagehand-py
```

## Environment Variables

Before running your script, set the following environment variables:

```bash
export BROWSERBASE_API_KEY="your-api-key"
export BROWSERBASE_PROJECT_ID="your-project-id"
export OPENAI_API_KEY="your-openai-api-key"  # or your preferred model's API key
export STAGEHAND_SERVER_URL="url-of-stagehand-server"
```

## Quickstart

Stagehand supports both synchronous and asynchronous usage. Here are examples for both approaches:

### Synchronous Usage

```python
import os
from stagehand.sync.client import Stagehand
from stagehand.schemas import ActOptions, ExtractOptions
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class DescriptionSchema(BaseModel):
    description: str

def main():
    # Create a Stagehand client - it will automatically create a new session if needed
    stagehand = Stagehand(
        model_name="gpt-4",  # Optional: defaults are available from the server
    )

    # Initialize Stagehand and create a new session
    stagehand.init()
    print(f"Created new session: {stagehand.session_id}")

    # Navigate to a webpage using local Playwright controls
    stagehand.page.goto("https://www.example.com")
    print("Navigation complete.")

    # Perform an action using the AI (e.g. simulate a button click)
    stagehand.page.act("click on the 'Quickstart' button")

    # Extract data from the page with schema validation
    data = stagehand.page.extract(
        ExtractOptions(
            instruction="extract the description of the page",
            schemaDefinition=DescriptionSchema.model_json_schema()
        )
    )
    description = data.get("description") if isinstance(data, dict) else data.description
    print("Extracted description:", description)

    stagehand.close()

if __name__ == "__main__":
    main()
```

### Asynchronous Usage

```python
import asyncio
import os
from stagehand.client import Stagehand
from stagehand.schemas import ActOptions, ExtractOptions
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class DescriptionSchema(BaseModel):
    description: str

async def main():
    # Create a Stagehand client - it will automatically create a new session if needed
    stagehand = Stagehand(
        model_name="gpt-4o",  # Optional: defaults are available from the server
    )

    # Initialize Stagehand and create a new session
    await stagehand.init()
    print(f"Created new session: {stagehand.session_id}")

    # Navigate to a webpage using local Playwright controls
    await stagehand.page.goto("https://www.example.com")
    print("Navigation complete.")

    # Perform an action using the AI (e.g. simulate a button click)
    await stagehand.page.act("click on the 'Quickstart' button")

    # Extract data from the page with schema validation
    data = await stagehand.page.extract(
        ExtractOptions(
            instruction="extract the description of the page",
            schemaDefinition=DescriptionSchema.model_json_schema()
        )
    )
    description = data.get("description") if isinstance(data, dict) else data.description
    print("Extracted description:", description)

    await stagehand.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Evals

To test all evaluations, run the following command in your terminal:

`python evals/run_all_evals.py`

This script will dynamically discover and execute every evaluation module within the `evals` directory and print the results for each.

## More Examples

For further examples, check out the scripts in the `examples/` directory:

1. **examples/example.py**: Demonstrates combined server-side/page navigation with AI-based actions.
2. **examples/extract-example.py**: Shows how to use the extract functionality with a JSON schema or a Pydantic model.
3. **examples/observe-example.py**: Demonstrates the observe functionality to get natural-language readings of the page.

## Configuration

Stagehand can be configured via environment variables or through a `StagehandConfig` object. Available configuration options include:

- `stagehand_server_url`: URL of the Stagehand API server.
- `browserbase_api_key`: Your Browserbase API key (`BROWSERBASE_API_KEY`).
- `browserbase_project_id`: Your Browserbase project ID (`BROWSERBASE_PROJECT_ID`).
- `model_api_key`: Your model API key (e.g. OpenAI, Anthropic, etc.) (`MODEL_API_KEY`).
- `verbose`: Verbosity level (default: 1).
- `model_name`: Optional model name for the AI.
- `dom_settle_timeout_ms`: Additional time (in ms) to have the DOM settle.
- `debug_dom`: Enable debug mode for DOM operations.
- `stream_response`: Whether to stream responses from the server (default: True).
- `timeout_settings`: Custom timeout settings for HTTP requests.

Example using a unified configuration:

```python
from stagehand.config import StagehandConfig
import os

config = StagehandConfig(
    env="BROWSERBASE" if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID") else "LOCAL",
    api_key=os.getenv("BROWSERBASE_API_KEY"),
    project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
    debug_dom=True,
    headless=False,
    dom_settle_timeout_ms=3000,
    model_name="gpt-4o-mini",
    model_client_options={"apiKey": os.getenv("MODEL_API_KEY")}
)
```

## Features

- **AI-powered Browser Control**: Execute natural language instructions over a running browser.
- **Validated Data Extraction**: Use JSON schemas (or Pydantic models) to extract and validate information from pages.
- **Async/Sync Support**: Choose between asynchronous and synchronous APIs based on your needs.
- **Context Manager Support**: Automatic resource cleanup with async and sync context managers.
- **Extensible**: Seamlessly extend Playwright functionality with AI enrichments.
- **Streaming Support**: Sreaming responses for better performance with long-running operations. Default True.

## Requirements

- Python 3.7+
- httpx (for async client)
- requests (for sync client)
- asyncio (for async client)
- pydantic
- python-dotenv (optional, for .env support)
- playwright

## Contributing

### Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

chmod +x run_tests.sh && ./run_tests.sh
```

## License

MIT License (c) 2025 Browserbase, Inc.
