# Stagehand Python SDK

A Python SDK for BrowserBase Stagehand, enabling automated browser control and data extraction.

## Installation

```bash
pip install stagehand-py
```

## Usage

```python
import asyncio
from stagehand import Stagehand

async def main():
    # Initialize the Stagehand client
    browser = Stagehand(
        env="BROWSERBASE",
        api_key="your-api-key",
        project_id="your-project-id"
    )
    
    # Perform browser actions
    result = await browser.act("Navigate to google.com")
    
    # Extract data using a schema
    data = await browser.extract("Get the search results", {
        "results": [{"title": "string", "url": "string"}]
    })
    
    # Close the browser
    await browser.close()

# Run the example
asyncio.run(main())
```

## Configuration

- `env`: Environment to use (default: "BROWSERBASE")
- `api_key`: Your BrowserBase API key (can also be set via BROWSERBASE_API_KEY environment variable)
- `project_id`: Your BrowserBase project ID (can also be set via BROWSERBASE_PROJECT_ID environment variable)
- `verbose`: Verbosity level (default: 0)

## Features

- Automated browser control with natural language commands
- Data extraction with schema validation
- Async/await support
- Automatic NextJS server management

## Requirements

- Python 3.7+
- httpx
- asyncio

## License

MIT License 