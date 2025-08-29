# Configuration Validation and Error Handling

This document describes the enhanced configuration validation and error handling features in Stagehand Python.

## Overview

Stagehand now includes comprehensive configuration validation that helps catch common configuration issues early and provides helpful error messages with suggestions for fixes.

## Features

### 1. API Base URL Validation

The system validates custom API endpoints to ensure they are properly formatted:

```python
from stagehand.config import StagehandConfig

# Valid configurations
config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_base": "https://api.openai.com/v1",
        "api_key": "your-api-key"
    }
)

# The system will catch invalid URLs
try:
    config = StagehandConfig(
        model_name="gpt-4o",
        model_client_options={
            "api_base": "not-a-valid-url",  # This will fail
            "api_key": "your-api-key"
        }
    )
except ValidationError as e:
    print(f"Configuration error: {e}")
```

### 2. API Key Validation

The system checks for API keys in multiple locations and provides helpful guidance:

```python
# API key in model_client_options (recommended)
config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_key": "your-openai-api-key"
    }
)

# API key via direct parameter
config = StagehandConfig(
    model_name="gpt-4o",
    model_api_key="your-openai-api-key"
)

# API key via environment variable (automatic detection)
# export OPENAI_API_KEY=your-api-key
config = StagehandConfig(model_name="gpt-4o")
```

### 3. Provider Inference

The system automatically infers the LLM provider from the model name:

```python
from stagehand.config import infer_provider_from_model_name

# Examples of provider inference
print(infer_provider_from_model_name("gpt-4o"))                    # "openai"
print(infer_provider_from_model_name("claude-3-opus-20240229"))    # "anthropic"
print(infer_provider_from_model_name("meta-llama/Llama-2-70b"))    # "together"
print(infer_provider_from_model_name("mixtral-8x7b-32768"))        # "groq"
```

### 4. Comprehensive Configuration Validation

You can validate a complete configuration before using it:

```python
from stagehand.config import StagehandConfig, validate_stagehand_config

config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_base": "https://api.openai.com/v1",
        "api_key": "your-api-key"
    }
)

# Validate the configuration
result = validate_stagehand_config(config)

if result["valid"]:
    print("✅ Configuration is valid!")
    
    # Check for warnings
    for warning in result["warnings"]:
        print(f"⚠️  {warning}")
        
    # Check for recommendations
    for recommendation in result["recommendations"]:
        print(f"💡 {recommendation}")
else:
    print("❌ Configuration has errors:")
    for error in result["errors"]:
        print(f"   • {error}")
```

## Error Messages

The system provides helpful error messages with examples:

```python
from stagehand.config import create_helpful_error_message

# Example error message for missing API key
validation_result = {
    "valid": False,
    "errors": ["No API key found for openai provider"],
    "warnings": ["Using localhost/local IP - ensure this is intended for development"],
    "recommendations": ["Consider enabling caching for better performance"]
}

error_message = create_helpful_error_message(validation_result, "initialization")
print(error_message)
```

Output:
```
Configuration Error in initialization:

Errors:
  • No API key found for openai provider

Warnings:
  • Using localhost/local IP - ensure this is intended for development

Recommendations:
  • Consider enabling caching for better performance

Example API key configuration:
  config = StagehandConfig(
      model_name='gpt-4o',
      model_client_options={
          'api_key': 'your-api-key-here'
      }
  )

Or set environment variable: export OPENAI_API_KEY=your-api-key-here
```

## Custom API Endpoints

The validation system supports various custom API endpoints:

### OpenAI Compatible Endpoints

```python
# Together AI
config = StagehandConfig(
    model_name="meta-llama/Llama-2-70b-chat-hf",
    model_client_options={
        "api_base": "https://api.together.xyz/v1",
        "api_key": "your-together-api-key"
    }
)

# Groq
config = StagehandConfig(
    model_name="mixtral-8x7b-32768",
    model_client_options={
        "api_base": "https://api.groq.com/openai/v1",
        "api_key": "your-groq-api-key"
    }
)

# Local OpenAI-compatible server
config = StagehandConfig(
    model_name="gpt-3.5-turbo",
    model_client_options={
        "api_base": "http://localhost:8000/v1",
        "api_key": "local-key"
    }
)
```

### Anthropic Compatible Endpoints

```python
# Official Anthropic API
config = StagehandConfig(
    model_name="claude-3-opus-20240229",
    model_client_options={
        "api_base": "https://api.anthropic.com",
        "api_key": "your-anthropic-api-key"
    }
)
```

## Environment Variables

The system automatically detects API keys from environment variables:

| Provider | Environment Variable |
|----------|---------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Together AI | `TOGETHER_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Google | `GOOGLE_API_KEY` |
| Cohere | `COHERE_API_KEY` |

## Validation Functions

### `validate_api_base_url(api_base: str)`

Validates an API base URL and returns detailed results:

```python
from stagehand.config import validate_api_base_url

result = validate_api_base_url("https://api.openai.com/v1")
# Returns: {
#     "valid": True,
#     "error": "",
#     "normalized_url": "https://api.openai.com/v1",
#     "warnings": []
# }
```

### `validate_api_key_configuration(model_name, model_api_key, model_client_options)`

Validates API key configuration for a specific model:

```python
from stagehand.config import validate_api_key_configuration

result = validate_api_key_configuration(
    "gpt-4o", 
    None, 
    {"api_key": "test-key"}
)
# Returns: {
#     "valid": True,
#     "errors": [],
#     "warnings": [],
#     "provider": "openai",
#     "api_key_source": "model_client_options"
# }
```

### `validate_stagehand_config(config: StagehandConfig)`

Performs comprehensive validation of a complete configuration:

```python
from stagehand.config import StagehandConfig, validate_stagehand_config

config = StagehandConfig(model_name="gpt-4o")
result = validate_stagehand_config(config)
# Returns detailed validation results
```

## Best Practices

1. **Always validate configuration** before initializing Stagehand in production
2. **Use environment variables** for API keys to keep them secure
3. **Check warnings and recommendations** to optimize your configuration
4. **Test custom API endpoints** before deployment
5. **Use HTTPS** for production API endpoints

## Migration from Browserbase

If you're migrating from a Browserbase setup, the validation system will help guide you:

```python
# Old Browserbase configuration (no longer supported)
# config = StagehandConfig(
#     env="BROWSERBASE",
#     api_key="browserbase-key",
#     project_id="browserbase-project"
# )

# New local configuration
config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_key": "your-openai-api-key"
    },
    local_browser_launch_options={
        "headless": False
    }
)
```

## Troubleshooting

### Common Issues

1. **"No API key found"** - Set the appropriate environment variable or add `api_key` to `model_client_options`
2. **"Invalid api_base URL"** - Ensure the URL starts with `http://` or `https://`
3. **"Model name required"** - Specify a valid model name like `"gpt-4o"` or `"claude-3-opus-20240229"`

### Getting Help

If you encounter configuration issues:

1. Check the validation error messages for specific guidance
2. Review the examples in this documentation
3. Ensure your API keys are correctly set
4. Verify your custom API endpoints are accessible

## Examples

See the `examples/config_validation_example.py` file for comprehensive examples of all validation features.