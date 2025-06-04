# Stagehand Python Evaluations

This directory contains evaluation tests for the Stagehand Python implementation. The evals have been updated to use the modern Stagehand API patterns and are designed to test various browser automation capabilities.

## Structure

The evaluations are organized into three main categories:

### 📋 Observe Evals (`observe/`)
Test the `page.observe()` functionality for finding and identifying elements on web pages.

- `observe_taxes.py` - Tests finding form input elements on a tax website
- `observe_search_results.py` - Tests observing search results on Google

### 🎯 Act Evals (`act/`)  
Test the `page.act()` functionality for performing actions and interactions.

- `google_jobs.py` - Tests a complex multi-step job search flow on Google Careers
- `act_form_filling.py` - Tests form filling capabilities on various input types

### 📊 Extract Evals (`extract/`)
Test the `page.extract()` functionality for extracting structured data from web pages.

- `extract_press_releases.py` - Tests extracting press release data with validation
- `extract_news_articles.py` - Tests extracting article data from news websites

## API Updates

The evals have been updated to use the modern Stagehand Python API:

### Old Pattern (Deprecated)
```python
from stagehand.schemas import ActOptions, ExtractOptions, ObserveOptions

await page.act(ActOptions(action="click the button"))
await page.extract(ExtractOptions(instruction="...", schemaDefinition=Schema))
await page.observe(ObserveOptions(instruction="find elements"))
```

### New Pattern (Current)
```python
# Simple string-based API
await page.act("click the button")
await page.extract("extract the data and return as JSON")
await page.observe("find all the buttons on the page")
```

### Configuration Updates

The initialization now uses `StagehandConfig`:

```python
from stagehand import Stagehand, StagehandConfig

config = StagehandConfig(
    env="BROWSERBASE",  # or "LOCAL"
    api_key=os.getenv("BROWSERBASE_API_KEY"),
    project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
    model_name="gpt-4o",
    headless=False,
    verbose=2,
    # ... other options
)

stagehand = Stagehand(config)
await stagehand.init()
```

## Running Evaluations

### Prerequisites

1. Set up environment variables:
   ```bash
   # For Browserbase (cloud) mode
   export BROWSERBASE_API_KEY="your_api_key"
   export BROWSERBASE_PROJECT_ID="your_project_id"
   
   # For AI model access
   export OPENAI_API_KEY="your_openai_key"
   # OR
   export MODEL_API_KEY="your_model_key"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running All Evals

```bash
# Run only observe evals (default)
python -m evals.run_all_evals

# Run all eval types
python -m evals.run_all_evals --all

# Run with specific model
python -m evals.run_all_evals --model gpt-4o-mini

# Run specific eval
python -m evals.run_all_evals --eval observe_taxes
```

### Running Individual Evals

Each eval can be run independently for testing:

```bash
cd evals/observe
python observe_taxes.py

cd ../act  
python act_form_filling.py

cd ../extract
python extract_news_articles.py
```

## Environment Modes

### Browserbase Mode (Recommended)
- Uses Browserbase cloud browsers
- Requires `BROWSERBASE_API_KEY` and `BROWSERBASE_PROJECT_ID`
- Provides session URLs for debugging
- More stable and consistent

### Local Mode
- Uses local browser instances
- Falls back when Browserbase credentials not available
- Good for development and testing
- May have more variability

## Evaluation Results

Each eval returns a standardized result format:

```python
{
    "_success": bool,           # Whether the eval passed
    "debugUrl": str | None,     # Debug URL (Browserbase only)
    "sessionUrl": str | None,   # Session URL (Browserbase only)  
    "logs": list,              # Collected logs
    "error": str | None,       # Error message if failed
    # ... eval-specific fields
}
```

## Adding New Evaluations

To add a new evaluation:

1. Create a new Python file in the appropriate directory (`observe/`, `act/`, or `extract/`)
2. Follow the naming convention: `{type}_{description}.py`
3. Implement an async function with the same name as the file
4. Use the signature: `async def eval_name(model_name: str, logger, use_text_extract: bool = False) -> dict`
5. Follow the patterns shown in existing evals

### Example Template

```python
import asyncio
from evals.init_stagehand import init_stagehand

async def my_new_eval(model_name: str, logger, use_text_extract: bool = False) -> dict:
    stagehand = None
    try:
        stagehand, init_response = await init_stagehand(model_name, logger)
        debug_url = init_response.get("debugUrl")
        session_url = init_response.get("sessionUrl")

        # Your evaluation logic here
        await stagehand.page.goto("https://example.com")
        result = await stagehand.page.observe("find something")
        
        return {
            "_success": len(result) > 0,
            "debugUrl": debug_url,
            "sessionUrl": session_url,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "_success": False,
            "error": str(e),
            "debugUrl": debug_url if 'debug_url' in locals() else None,
            "sessionUrl": session_url if 'session_url' in locals() else None,
            "logs": logger.get_logs() if hasattr(logger, "get_logs") else [],
        }
    finally:
        if stagehand:
            await stagehand.close()
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root and all dependencies are installed
2. **Environment Variables**: Verify API keys are set correctly
3. **Network Issues**: Some evals depend on external websites being available
4. **Model Timeouts**: Increase timeouts or try different models for complex evals

### Debugging

- Use `verbose=3` in StagehandConfig for detailed logs
- Check session URLs in Browserbase mode for visual debugging
- Run individual evals to isolate issues
- Check the logs returned in eval results

## Contributing

When contributing new evals:

1. Follow the existing patterns and naming conventions
2. Include proper error handling and cleanup
3. Add meaningful validation of results
4. Test both Browserbase and Local modes
5. Update this README if adding new categories 