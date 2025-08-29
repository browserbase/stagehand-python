# LLM Client Configuration Guide

This guide explains how to configure the enhanced LLM client in Stagehand to work with custom API endpoints and different providers.

## Overview

The enhanced LLM client supports:
- Custom API endpoints for OpenAI/Anthropic compatible providers
- Multiple LLM providers (OpenAI, Anthropic, Together AI, Groq, etc.)
- Environment variable fallback for API keys
- Configuration validation and error handling
- Timeout and retry configuration

## Basic Configuration

### OpenAI Configuration

```python
from stagehand.config import StagehandConfig

config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={
        "api_base": "https://api.openai.com/v1",
        "api_key": "your-openai-api-key",
        "timeout": 30,
        "max_retries": 3
    }
)
```

### Anthropic Configuration

```python
config = StagehandConfig(
    model_name="claude-3-haiku-20240307",
    model_client_options={
        "api_base": "https://api.anthropic.com",
        "api_key": "your-anthropic-api-key",
        "timeout": 60
    }
)
```

### Together AI Configuration

```python
config = StagehandConfig(
    model_name="together/llama-2-7b-chat",
    model_client_options={
        "api_base": "https://api.together.xyz/v1",
        "api_key": "your-together-api-key"
    }
)
```

### Groq Configuration

```python
config = StagehandConfig(
    model_name="groq/llama2-70b-4096",
    model_client_options={
        "api_base": "https://api.groq.com/openai/v1",
        "api_key": "your-groq-api-key"
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

## Environment Variable Fallback

The LLM client automatically detects API keys from environment variables based on the model name:

- OpenAI models: `OPENAI_API_KEY`
- Anthropic models: `ANTHROPIC_API_KEY`
- Together AI models: `TOGETHER_API_KEY`
- Groq models: `GROQ_API_KEY`
- Google/Gemini models: `GOOGLE_API_KEY`
- Generic fallback: `MODEL_API_KEY` or `LLM_API_KEY`

Example without explicit API key:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"

config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={
        "api_base": "https://api.openai.com/v1"
        # API key will be automatically detected
    }
)
```

## Configuration Options

### Available Options

- `api_base` or `baseURL`: Custom API endpoint URL
- `api_key` or `apiKey`: API key for authentication
- `timeout`: Request timeout in seconds (default: 30)
- `max_retries`: Maximum number of retries for failed requests (default: 3)

### Validation

The configuration is automatically validated:

- API base must be a valid HTTP/HTTPS URL
- Timeout must be a positive number
- Max retries must be a non-negative integer
- Only one API key field should be specified

## Error Handling

The enhanced LLM client provides detailed error messages for common issues:

### API Key Errors
```
LLMProviderError: API key error for model gpt-4o. Please check your API key configuration in model_client_options.
```

### Model Not Found
```
LLMProviderError: Model gpt-4o not found. Please check the model name and your API endpoint configuration.
```

### Unauthorized Access
```
LLMProviderError: Unauthorized access for model gpt-4o. Please check your API key and permissions.
```

### Rate Limiting
```
LLMProviderError: Rate limit exceeded for model gpt-4o. Please try again later or check your usage limits.
```

## Configuration Validation

You can validate your LLM configuration programmatically:

```python
async with Stagehand(config=config) as stagehand:
    validation = stagehand.llm.validate_configuration()
    
    if validation['valid']:
        print("Configuration is valid")
        print(f"Provider: {validation['configuration']['provider']}")
        print(f"API Base: {validation['configuration']['api_base']}")
    else:
        print("Configuration errors:", validation['errors'])
        print("Configuration warnings:", validation['warnings'])
```

## Migration from Browserbase

If you're migrating from a Browserbase configuration, here's how to update:

### Before (Browserbase)
```python
config = StagehandConfig(
    env="BROWSERBASE",  # ❌ No longer supported
    api_key="browserbase-api-key",  # ❌ No longer needed
    project_id="browserbase-project-id",  # ❌ No longer needed
    model_name="gpt-4o",
    model_client_options={"apiKey": "openai-api-key"}  # ❌ Old format
)
```

### After (Local with Custom Endpoint)
```python
config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_base": "https://api.openai.com/v1",  # ✅ Optional custom endpoint
        "api_key": "openai-api-key",  # ✅ New format
        "timeout": 30
    },
    local_browser_launch_options={  # ✅ New browser configuration
        "headless": False
    }
)
```

### Key Migration Points

1. **Remove Browserbase fields**: `env`, `api_key`, `project_id`
2. **Update API key format**: Use `api_key` instead of `apiKey` in `model_client_options`
3. **Add browser options**: Configure local browser with `local_browser_launch_options`
4. **Update environment variables**: Remove `BROWSERBASE_*` variables, keep LLM provider keys

For a complete migration guide, see [Migration Guide](migration_guide.md).

## Best Practices

1. **Use Environment Variables**: Store API keys in environment variables rather than hardcoding them
2. **Set Appropriate Timeouts**: Configure timeouts based on your provider and model
3. **Handle Errors Gracefully**: Implement proper error handling for API failures
4. **Validate Configuration**: Use the validation method to check configuration before making requests
5. **Monitor Usage**: Keep track of token usage and API limits

## Example: Complete Configuration

```python
import asyncio
import os
from stagehand.main import Stagehand
from stagehand.config import StagehandConfig

async def main():
    config = StagehandConfig(
        model_name="gpt-4o-mini",
        model_client_options={
            "api_base": "https://api.openai.com/v1",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "timeout": 30,
            "max_retries": 3
        },
        verbose=1,
        local_browser_launch_options={
            "headless": False,
            "viewport": {"width": 1280, "height": 720}
        }
    )
    
    async with Stagehand(config=config) as stagehand:
        # Validate configuration
        validation = stagehand.llm.validate_configuration()
        if not validation['valid']:
            print("Configuration errors:", validation['errors'])
            return
        
        # Use Stagehand normally
        page = stagehand.page
        await page.goto("https://example.com")
        
        # Extract data using the configured LLM
        result = await page.extract("Extract the page title")
        print("Extracted:", result)

if __name__ == "__main__":
    asyncio.run(main())
```