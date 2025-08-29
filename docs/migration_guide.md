# Migration Guide: From Browserbase to Local Configuration

This guide helps you migrate from the previous Browserbase-dependent version of Stagehand to the new local-only version with enhanced LLM provider support.

## Overview of Changes

The new version of Stagehand:
- **Removes** dependency on Browserbase API
- **Uses** local Playwright browser instances
- **Supports** custom API endpoints for various LLM providers
- **Maintains** all existing functionality (act, extract, observe, agent)
- **Improves** Windows compatibility

## Step-by-Step Migration

### 1. Update Dependencies

The new version automatically removes Browserbase dependencies. Simply update:

```bash
pip install --upgrade stagehand
```

### 2. Update Configuration

#### Before (Browserbase)
```python
from stagehand import StagehandConfig, Stagehand

config = StagehandConfig(
    env="BROWSERBASE",  # ❌ No longer supported
    api_key="browserbase-api-key",  # ❌ No longer needed
    project_id="browserbase-project-id",  # ❌ No longer needed
    model_name="gpt-4o",
    model_api_key="openai-api-key"  # ❌ Deprecated
)
```

#### After (Local)
```python
from stagehand import StagehandConfig, Stagehand

config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={  # ✅ New configuration format
        "api_key": "openai-api-key",
        "api_base": "https://api.openai.com/v1"  # Optional
    },
    local_browser_launch_options={  # ✅ New browser options
        "headless": False,
        "viewport": {"width": 1280, "height": 720}
    }
)
```

### 3. Update Environment Variables

#### Remove Browserbase Variables
```bash
# Remove these from your .env file
BROWSERBASE_API_KEY=your-browserbase-key
BROWSERBASE_PROJECT_ID=your-project-id
```

#### Keep/Add LLM Provider Variables
```bash
# OpenAI (most common)
OPENAI_API_KEY=your-openai-key

# Or other providers
ANTHROPIC_API_KEY=your-anthropic-key
TOGETHER_API_KEY=your-together-key
GROQ_API_KEY=your-groq-key
```

### 4. Update Initialization Code

#### Before
```python
async def main():
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="gpt-4o"
    )
    
    stagehand = Stagehand(config)
    await stagehand.init()
    
    # Session URL was available
    if stagehand.env == "BROWSERBASE":
        print(f"Session: https://www.browserbase.com/sessions/{stagehand.session_id}")
```

#### After
```python
async def main():
    config = StagehandConfig(
        model_name="gpt-4o",
        model_client_options={
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    )
    
    stagehand = Stagehand(config)
    await stagehand.init()
    
    # Local browser - no session URL needed
    print("Local browser initialized successfully")
```

## Configuration Examples for Different Providers

### OpenAI (Default)
```python
config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={
        "api_key": os.getenv("OPENAI_API_KEY")
    }
)
```

### Anthropic Claude
```python
config = StagehandConfig(
    model_name="claude-3-haiku-20240307",
    model_client_options={
        "api_base": "https://api.anthropic.com",
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    }
)
```

### Together AI
```python
config = StagehandConfig(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    model_client_options={
        "api_base": "https://api.together.xyz/v1",
        "api_key": os.getenv("TOGETHER_API_KEY")
    }
)
```

### Groq
```python
config = StagehandConfig(
    model_name="llama2-70b-4096",
    model_client_options={
        "api_base": "https://api.groq.com/openai/v1",
        "api_key": os.getenv("GROQ_API_KEY")
    }
)
```

### Local OpenAI-Compatible Server
```python
config = StagehandConfig(
    model_name="local/custom-model",
    model_client_options={
        "api_base": "http://localhost:8000/v1",
        "api_key": "local-key",
        "timeout": 120  # Local servers might be slower
    }
)
```

## Browser Configuration Options

The new version provides extensive browser customization:

```python
config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={"api_key": os.getenv("OPENAI_API_KEY")},
    local_browser_launch_options={
        # Basic options
        "headless": True,  # Run without GUI
        "viewport": {"width": 1920, "height": 1080},
        
        # Data persistence
        "user_data_dir": "./browser_data",
        
        # Downloads
        "downloads_path": "./downloads",
        
        # Chrome arguments
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    }
)
```

## Testing Migration

### Update Test Configuration

#### Before
```python
@pytest.fixture
def browserbase_config():
    return StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID")
    )
```

#### After
```python
@pytest.fixture
def local_config():
    return StagehandConfig(
        model_name="gpt-4o-mini",
        model_client_options={
            "api_key": os.getenv("OPENAI_API_KEY")
        },
        local_browser_launch_options={"headless": True}
    )
```

### Update Test Cases

All existing test functionality remains the same - only configuration changes:

```python
async def test_page_extract(local_config):
    async with Stagehand(config=local_config) as stagehand:
        page = stagehand.page
        await page.goto("https://example.com")
        
        result = await page.extract("the page title")
        assert result is not None
```

## Common Issues and Solutions

### Issue: "Browserbase API key not found"
**Solution**: Remove all Browserbase-related environment variables and configuration. Use the new `model_client_options` format.

### Issue: "Browser failed to launch"
**Solution**: Ensure Playwright browsers are installed:
```bash
playwright install
```

### Issue: "API key not found"
**Solution**: Set the appropriate environment variable for your LLM provider:
```bash
export OPENAI_API_KEY=your-key
# or
export ANTHROPIC_API_KEY=your-key
```

### Issue: Windows compatibility problems
**Solution**: The new version has improved Windows support. Use PowerShell and ensure paths use forward slashes or proper escaping.

## Performance Considerations

### Benefits of Local Configuration
- **Faster startup**: No API calls to create browser sessions
- **Lower latency**: Direct browser communication
- **Better reliability**: No dependency on external browser service
- **Cost savings**: No Browserbase subscription needed

### Resource Usage
- **Memory**: Local browsers use more local memory
- **CPU**: Browser processes run on your machine
- **Storage**: Browser data stored locally (configurable)

## Rollback Plan

If you need to temporarily rollback:

1. **Pin the old version** in your requirements:
   ```bash
   pip install stagehand==0.4.x  # Replace with last Browserbase version
   ```

2. **Keep old configuration** in a separate branch
3. **Test thoroughly** before upgrading production systems

## Frequently Asked Questions (FAQ)

### General Migration Questions

**Q: Will my existing automation scripts still work after migration?**
A: Yes! The core API methods (`page.act()`, `page.extract()`, `page.observe()`, `agent.execute()`) remain completely unchanged. Only the configuration setup needs to be updated.

**Q: Do I need to rewrite my browser automation logic?**
A: No. All your existing automation code will work exactly the same way. The change is only in how you configure Stagehand, not how you use it.

**Q: Can I still use the same LLM models I was using before?**
A: Absolutely! You can use the same models (like `gpt-4o`, `gpt-4o-mini`, etc.), and now you have even more flexibility to use different providers or custom endpoints.

**Q: What happens to my existing test suites?**
A: Your test logic remains the same. You'll only need to update the configuration fixtures to use the new local format instead of Browserbase.

### Performance and Reliability

**Q: Will performance be better or worse with local browsers?**
A: Performance should be significantly better! Local browsers eliminate network latency to Browserbase servers, provide faster startup times, and give you direct control over browser resources.

**Q: What about reliability compared to Browserbase?**
A: Local browsers are generally more reliable since you're not dependent on external services. You have full control over the browser environment and don't need to worry about API rate limits or service outages.

**Q: How much memory will local browsers use?**
A: Local browsers typically use 100-500MB of RAM per instance, depending on the pages you're automating. You can control this with the `headless` option and browser arguments.

### Configuration and Setup

**Q: Can I use multiple LLM providers in the same application?**
A: Yes! You can create different `StagehandConfig` instances for different providers and switch between them as needed.

**Q: How do I handle API keys securely?**
A: Use environment variables (recommended) or a secure configuration management system. Never hardcode API keys in your source code.

**Q: What if I want to use a custom or self-hosted LLM?**
A: The new version supports any OpenAI-compatible API endpoint. Just set the `api_base` in your `model_client_options` to point to your custom server.

**Q: Can I still run headless browsers for CI/CD?**
A: Yes! Set `"headless": True` in your `local_browser_launch_options`. This is actually easier now since you don't need to manage Browserbase sessions.

### Migration Process

**Q: How long does the migration typically take?**
A: For most projects, migration takes 15-30 minutes. It's mainly updating configuration and removing Browserbase imports.

**Q: Can I migrate gradually or do I need to do everything at once?**
A: You can migrate gradually. Update one script at a time and test each one before moving to the next.

**Q: What if I encounter errors during migration?**
A: Use the migration utility (`python docs/migration_utility.py`) to identify issues, check the troubleshooting guide, and enable verbose logging (`verbose=2`) to see detailed error messages.

**Q: Is there a way to validate my migration before going live?**
A: Yes! Run your existing test suite with the new configuration, and use the validation script provided in the migration guide.

### Browser and System Compatibility

**Q: Does this work on Windows, macOS, and Linux?**
A: Yes! The new version has improved cross-platform support, with particular improvements for Windows 11 PowerShell compatibility.

**Q: What browsers are supported?**
A: Stagehand uses Playwright, so it supports Chromium, Firefox, and WebKit. Chromium is the default and most tested option.

**Q: Can I use my existing browser profile or extensions?**
A: Yes! Use the `user_data_dir` option in `local_browser_launch_options` to specify a persistent browser profile directory.

### Troubleshooting

**Q: I'm getting "browserbase module not found" errors**
A: Remove all `import browserbase` and `from browserbase import` statements from your code. The new version doesn't use the browserbase package.

**Q: My API key isn't working**
A: Make sure you've moved your LLM API key to `model_client_options["api_key"]` and that you're using the correct environment variable name (e.g., `OPENAI_API_KEY`, not `BROWSERBASE_API_KEY`).

**Q: The browser won't start on my system**
A: Run `playwright install` to ensure browser binaries are installed. On Linux, you might need additional dependencies: `playwright install-deps`.

**Q: I'm getting timeout errors**
A: Local browsers might need different timeout settings. Increase `dom_settle_timeout_ms` or add timeout options to your `model_client_options`.

### Advanced Usage

**Q: Can I run multiple browser instances simultaneously?**
A: Yes! Each `Stagehand` instance manages its own browser. You can create multiple instances for parallel automation.

**Q: How do I debug issues with the local browser?**
A: Set `"headless": False` to see the browser in action, enable verbose logging with `verbose=2`, and use browser developer tools.

**Q: Can I customize the browser further than the provided options?**
A: Yes! The `local_browser_launch_options` accepts any Playwright browser launch option. You can also pass custom Chrome arguments via the `args` array.

**Q: What about proxy support?**
A: You can configure proxies through the `local_browser_launch_options` using Playwright's proxy settings.

## Getting Help

If you encounter issues during migration:

1. **Run the migration utility**: `python docs/migration_utility.py` to analyze your code
2. **Check the troubleshooting guide**: See [troubleshooting.md](troubleshooting.md) for common issues
3. **Enable verbose logging**: Set `verbose=2` in your config for detailed error messages
4. **Review configuration**: Double-check your `model_client_options` and API keys
5. **Test incrementally**: Migrate one script at a time to isolate issues
6. **Check examples**: Look at the updated examples in the `examples/` directory

## Complete Migration Example

Here's a complete before/after example:

### Before (Browserbase)
```python
import asyncio
import os
from stagehand import StagehandConfig, Stagehand

async def main():
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="gpt-4o",
        model_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    async with Stagehand(config=config) as stagehand:
        if stagehand.env == "BROWSERBASE":
            print(f"Session: https://www.browserbase.com/sessions/{stagehand.session_id}")
        
        page = stagehand.page
        await page.goto("https://example.com")
        result = await page.extract("the page title")
        print(f"Title: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### After (Local)
```python
import asyncio
import os
from stagehand import StagehandConfig, Stagehand

async def main():
    config = StagehandConfig(
        model_name="gpt-4o",
        model_client_options={
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_base": "https://api.openai.com/v1"
        },
        local_browser_launch_options={
            "headless": False,
            "viewport": {"width": 1280, "height": 720}
        }
    )
    
    async with Stagehand(config=config) as stagehand:
        print("Local browser initialized successfully")
        
        page = stagehand.page
        await page.goto("https://example.com")
        result = await page.extract("the page title")
        print(f"Title: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

The migration is straightforward - the core functionality remains identical, only the configuration format has changed to be more flexible and support multiple LLM providers.