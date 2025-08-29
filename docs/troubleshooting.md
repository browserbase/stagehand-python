# Troubleshooting Guide

This guide helps you resolve common issues when using Stagehand with local browser configuration and custom LLM providers.

## Migration-Specific Issues

### Browserbase Removal Errors

#### Error: "ModuleNotFoundError: No module named 'browserbase'"
```
ModuleNotFoundError: No module named 'browserbase'
```

**Solutions:**
1. **Remove browserbase imports:**
   ```python
   # Remove these lines
   import browserbase
   from browserbase import Browserbase
   ```

2. **Uninstall browserbase package:**
   ```bash
   pip uninstall browserbase
   ```

3. **Update requirements.txt:**
   ```txt
   # Remove this line
   browserbase>=1.0.0
   ```

#### Error: "StagehandConfig has no attribute 'env'"
```
AttributeError: 'StagehandConfig' has no attribute 'env'
```

**Solutions:**
1. **Remove env parameter:**
   ```python
   # OLD - Remove this
   config = StagehandConfig(env="BROWSERBASE", ...)
   
   # NEW - Use this
   config = StagehandConfig(model_name="gpt-4o", ...)
   ```

#### Error: "Browserbase API key not recognized"
```
StagehandConfigError: 'api_key' parameter not recognized
```

**Solutions:**
1. **Move API key to model_client_options:**
   ```python
   # OLD - Remove this
   config = StagehandConfig(api_key="bb_browserbase_key", ...)
   
   # NEW - Use this for LLM API key
   config = StagehandConfig(
       model_client_options={"api_key": "your_llm_api_key"}
   )
   ```

#### Error: "project_id parameter not found"
```
TypeError: StagehandConfig() got an unexpected keyword argument 'project_id'
```

**Solutions:**
1. **Remove project_id completely:**
   ```python
   # OLD - Remove this
   config = StagehandConfig(project_id="browserbase_project", ...)
   
   # NEW - Not needed
   config = StagehandConfig(model_name="gpt-4o", ...)
   ```

#### Error: "browserbase_session_id not supported"
```
TypeError: StagehandConfig() got an unexpected keyword argument 'browserbase_session_id'
```

**Solutions:**
1. **Remove all session-related parameters:**
   ```python
   # Remove these parameters
   browserbase_session_id="session_123"
   browserbase_session_create_params={...}
   use_api=True
   ```

### Configuration Migration Issues

#### Error: "model_api_key deprecated"
```
DeprecationWarning: model_api_key is deprecated, use model_client_options instead
```

**Solutions:**
1. **Update to new format:**
   ```python
   # OLD
   config = StagehandConfig(
       model_api_key="your_openai_key"
   )
   
   # NEW
   config = StagehandConfig(
       model_client_options={
           "api_key": "your_openai_key"
       }
   )
   ```

#### Error: "headless parameter not found"
```
TypeError: StagehandConfig() got an unexpected keyword argument 'headless'
```

**Solutions:**
1. **Move to local_browser_launch_options:**
   ```python
   # OLD
   config = StagehandConfig(headless=True, ...)
   
   # NEW
   config = StagehandConfig(
       local_browser_launch_options={"headless": True}
   )
   ```

## Configuration Issues

### API Key Errors

#### Error: "API key not found"
```
LLMProviderError: API key error for model gpt-4o. Please check your API key configuration in model_client_options.
```

**Solutions:**
1. **Set environment variable:**
   ```bash
   export OPENAI_API_KEY=your-api-key
   # On Windows PowerShell:
   $env:OPENAI_API_KEY="your-api-key"
   ```

2. **Specify in configuration:**
   ```python
   config = StagehandConfig(
       model_name="gpt-4o",
       model_client_options={
           "api_key": "your-api-key"  # Direct specification
       }
   )
   ```

3. **Check environment variable loading:**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()  # Load from .env file
   print(f"API Key loaded: {bool(os.getenv('OPENAI_API_KEY'))}")
   ```

#### Error: "Unauthorized access"
```
LLMProviderError: Unauthorized access for model gpt-4o. Please check your API key and permissions.
```

**Solutions:**
1. **Verify API key validity** on your provider's dashboard
2. **Check API key permissions** (ensure it has the required scopes)
3. **Verify billing status** (some providers require active billing)

### Model Configuration Issues

#### Error: "Model not found"
```
LLMProviderError: Model gpt-4o not found. Please check the model name and your API endpoint configuration.
```

**Solutions:**
1. **Check model name spelling:**
   ```python
   # Correct model names
   "gpt-4o-mini"  # OpenAI
   "claude-3-haiku-20240307"  # Anthropic
   "meta-llama/Llama-2-7b-chat-hf"  # Together AI
   ```

2. **Verify model availability** with your provider
3. **Check API endpoint compatibility:**
   ```python
   config = StagehandConfig(
       model_name="gpt-4o-mini",
       model_client_options={
           "api_base": "https://api.openai.com/v1",  # Correct endpoint
           "api_key": os.getenv("OPENAI_API_KEY")
       }
   )
   ```

### Custom Endpoint Issues

#### Error: "Connection failed to custom endpoint"
```
ConnectionError: Failed to connect to https://api.custom-provider.com/v1
```

**Solutions:**
1. **Verify endpoint URL:**
   ```python
   # Ensure URL is complete and correct
   "api_base": "https://api.together.xyz/v1"  # Include /v1 if required
   ```

2. **Test endpoint manually:**
   ```bash
   curl -H "Authorization: Bearer your-api-key" https://api.custom-provider.com/v1/models
   ```

3. **Check network connectivity and firewall settings**

## Browser Issues

### Browser Launch Failures

#### Error: "Browser failed to launch"
```
BrowserConnectionError: Failed to launch browser
```

**Solutions:**
1. **Install Playwright browsers:**
   ```bash
   playwright install
   # Or specific browser:
   playwright install chromium
   ```

2. **Check system requirements:**
   - Sufficient RAM (minimum 2GB available)
   - Disk space for browser installation
   - Required system libraries (Linux)

3. **Try different browser options:**
   ```python
   config = StagehandConfig(
       model_name="gpt-4o-mini",
       model_client_options={"api_key": os.getenv("OPENAI_API_KEY")},
       local_browser_launch_options={
           "headless": True,  # Try headless mode
           "args": ["--no-sandbox", "--disable-dev-shm-usage"]
       }
   )
   ```

#### Error: "Permission denied" (Linux/macOS)
```
PermissionError: [Errno 13] Permission denied: '/path/to/browser'
```

**Solutions:**
1. **Fix browser permissions:**
   ```bash
   chmod +x ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome
   ```

2. **Run with proper user permissions**
3. **Install system dependencies (Linux):**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
   ```

### Windows-Specific Issues

#### Error: "PowerShell execution policy"
```
ExecutionPolicy: Execution of scripts is disabled on this system
```

**Solutions:**
1. **Update execution policy:**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Run scripts with bypass:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File script.ps1
   ```

#### Error: "Path too long" (Windows)
```
OSError: [Errno 2] No such file or directory (path too long)
```

**Solutions:**
1. **Enable long path support:**
   - Run `gpedit.msc` as administrator
   - Navigate to: Computer Configuration > Administrative Templates > System > Filesystem
   - Enable "Enable Win32 long paths"

2. **Use shorter paths:**
   ```python
   config = StagehandConfig(
       local_browser_launch_options={
           "user_data_dir": "C:/tmp/browser"  # Shorter path
       }
   )
   ```

## Performance Issues

### Slow Browser Startup

**Solutions:**
1. **Use persistent browser data:**
   ```python
   config = StagehandConfig(
       local_browser_launch_options={
           "user_data_dir": "./browser_data"  # Reuse browser profile
       }
   )
   ```

2. **Optimize browser arguments:**
   ```python
   config = StagehandConfig(
       local_browser_launch_options={
           "args": [
               "--disable-extensions",
               "--disable-plugins",
               "--disable-images",  # For faster loading
               "--disable-javascript"  # If JS not needed
           ]
       }
   )
   ```

3. **Use headless mode:**
   ```python
   config = StagehandConfig(
       local_browser_launch_options={"headless": True}
   )
   ```

### High Memory Usage

**Solutions:**
1. **Limit browser resources:**
   ```python
   config = StagehandConfig(
       local_browser_launch_options={
           "args": [
               "--memory-pressure-off",
               "--max_old_space_size=2048"
           ]
       }
   )
   ```

2. **Close browser properly:**
   ```python
   try:
       # Your automation code
       pass
   finally:
       await stagehand.close()  # Always close
   ```

3. **Use context managers:**
   ```python
   async with Stagehand(config=config) as stagehand:
       # Automatic cleanup
       pass
   ```

## LLM Provider Issues

### Rate Limiting

#### Error: "Rate limit exceeded"
```
LLMProviderError: Rate limit exceeded for model gpt-4o. Please try again later or check your usage limits.
```

**Solutions:**
1. **Implement retry logic:**
   ```python
   config = StagehandConfig(
       model_client_options={
           "max_retries": 5,
           "timeout": 60
       }
   )
   ```

2. **Use exponential backoff:**
   ```python
   import asyncio
   import random
   
   async def retry_with_backoff(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return await func()
           except Exception as e:
               if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                   wait_time = (2 ** attempt) + random.uniform(0, 1)
                   await asyncio.sleep(wait_time)
               else:
                   raise
   ```

3. **Switch to different model/provider temporarily**

### Token Limit Issues

#### Error: "Token limit exceeded"
```
LLMProviderError: Token limit exceeded for model gpt-4o-mini
```

**Solutions:**
1. **Use models with larger context windows:**
   ```python
   config = StagehandConfig(
       model_name="gpt-4o",  # Larger context than gpt-4o-mini
       model_client_options={"api_key": os.getenv("OPENAI_API_KEY")}
   )
   ```

2. **Reduce DOM content:**
   ```python
   # Extract specific elements instead of full page
   result = await page.extract("specific element text", selector="div.content")
   ```

3. **Use observe for action planning:**
   ```python
   # Get action plan first (smaller response)
   action = await page.observe("find the login button")
   # Then execute without additional LLM call
   await page.act(action)
   ```

## Testing Issues

### Test Configuration

#### Error: "Tests fail with local configuration"
```python
# Update test fixtures
@pytest.fixture
def stagehand_config():
    return StagehandConfig(
        model_name="gpt-4o-mini",
        model_client_options={
            "api_key": os.getenv("OPENAI_API_KEY")
        },
        local_browser_launch_options={"headless": True}  # Important for CI
    )
```

### CI/CD Issues

#### Error: "Browser not found in CI"
```yaml
# GitHub Actions example
- name: Install Playwright
  run: |
    pip install playwright
    playwright install --with-deps chromium
```

#### Error: "Display not found" (Linux CI)
```yaml
# Add virtual display for non-headless testing
- name: Setup virtual display
  run: |
    sudo apt-get install -y xvfb
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
```

## Debugging Tips

### Enable Verbose Logging

```python
config = StagehandConfig(
    verbose=2,  # Maximum verbosity
    use_rich_logging=True,  # Pretty console output
    model_client_options={"api_key": os.getenv("OPENAI_API_KEY")}
)
```

### Custom Logger

```python
def custom_logger(message):
    print(f"[DEBUG] {message}")

config = StagehandConfig(
    logger=custom_logger,
    model_client_options={"api_key": os.getenv("OPENAI_API_KEY")}
)
```

### Browser Developer Tools

```python
config = StagehandConfig(
    local_browser_launch_options={
        "headless": False,
        "devtools": True  # Open DevTools automatically
    }
)
```

### Network Debugging

```python
# Monitor network requests
async with Stagehand(config=config) as stagehand:
    page = stagehand.page
    
    # Enable request logging
    page.on("request", lambda request: print(f"Request: {request.url}"))
    page.on("response", lambda response: print(f"Response: {response.status} {response.url}"))
    
    await page.goto("https://example.com")
```

## Getting Help

If these solutions don't resolve your issue:

1. **Check the logs** with verbose logging enabled
2. **Search existing issues** on GitHub
3. **Join our community** on [Slack](https://stagehand.dev/slack)
4. **Create a minimal reproduction** case
5. **Include system information** (OS, Python version, Stagehand version)

### Issue Template

When reporting issues, include:

```
**Environment:**
- OS: [Windows 11/macOS/Linux]
- Python: [3.9/3.10/3.11/3.12]
- Stagehand: [version]

**Configuration:**
```python
config = StagehandConfig(
    # Your configuration here
)
```

**Error:**
```
Full error traceback here
```

**Expected behavior:**
What you expected to happen

**Actual behavior:**
What actually happened
```

This information helps us provide faster and more accurate support.