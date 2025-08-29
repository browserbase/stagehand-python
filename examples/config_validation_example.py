#!/usr/bin/env python3
"""
Example demonstrating Stagehand configuration validation and error handling.

This example shows how to:
1. Validate configuration before initialization
2. Handle configuration errors gracefully
3. Use custom API endpoints with validation
4. Get helpful error messages for common issues
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import stagehand
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from stagehand.config import (
    StagehandConfig,
    StagehandConfigError,
    validate_stagehand_config,
    validate_api_base_url,
    validate_api_key_configuration,
    create_helpful_error_message,
    infer_provider_from_model_name
)
    from stagehand.utils import (
        validate_model_name,
        check_environment_setup,
        suggest_configuration_fixes
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run this script from the stagehand-python root directory")
    sys.exit(1)


def demonstrate_api_base_validation():
    """Demonstrate API base URL validation."""
    print("🔍 API Base URL Validation Examples")
    print("-" * 40)
    
    test_urls = [
        "https://api.openai.com/v1",           # Valid OpenAI
        "https://api.anthropic.com",           # Valid Anthropic
        "https://api.together.xyz/v1",         # Valid Together AI
        "http://localhost:8000/v1",            # Valid local (with warning)
        "https://api.groq.com/openai/v1/",     # Valid with trailing slash
        "not-a-url",                           # Invalid
        "ftp://invalid.com",                   # Invalid protocol
        "",                                    # Empty
    ]
    
    for url in test_urls:
        result = validate_api_base_url(url)
        status = "✅" if result["valid"] else "❌"
        print(f"{status} {url}")
        
        if result["valid"]:
            if result["normalized_url"] != url:
                print(f"   → Normalized to: {result['normalized_url']}")
            if result["warnings"]:
                for warning in result["warnings"]:
                    print(f"   ⚠️  {warning}")
        else:
            print(f"   ❌ {result['error']}")
        print()


def demonstrate_provider_inference():
    """Demonstrate provider inference from model names."""
    print("🤖 Provider Inference Examples")
    print("-" * 40)
    
    models = [
        "gpt-4o",
        "gpt-3.5-turbo", 
        "claude-3-opus-20240229",
        "claude-3-sonnet",
        "meta-llama/Llama-2-70b-chat-hf",
        "mixtral-8x7b-32768",
        "gemini-pro",
        "command-r-plus",
        "unknown-model-name"
    ]
    
    for model in models:
        provider = infer_provider_from_model_name(model)
        provider_display = provider if provider else "Unknown"
        print(f"📝 {model} → {provider_display}")
    print()


def demonstrate_configuration_validation():
    """Demonstrate full configuration validation."""
    print("⚙️  Configuration Validation Examples")
    print("-" * 40)
    
    # Example 1: Valid configuration
    print("1. Valid Configuration:")
    try:
        config = StagehandConfig(
            model_name="gpt-4o",
            model_client_options={
                "api_key": "sk-test-key-here",
                "api_base": "https://api.openai.com/v1"
            },
            verbose=1
        )
        
        result = validate_stagehand_config(config)
        if result["valid"]:
            print("   ✅ Configuration is valid!")
            if result["warnings"]:
                for warning in result["warnings"]:
                    print(f"   ⚠️  {warning}")
        else:
            print("   ❌ Configuration has errors:")
            for error in result["errors"]:
                print(f"      • {error}")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
    print()
    
    # Example 2: Missing model name
    print("2. Missing Model Name:")
    try:
        config = StagehandConfig(model_name=None)
        result = validate_stagehand_config(config)
        if not result["valid"]:
            error_message = create_helpful_error_message(result, "Example 2")
            print(f"   ❌ {error_message}")
    except Exception as e:
        print(f"   ❌ Validation error: {e}")
    print()
    
    # Example 3: Invalid API base
    print("3. Invalid API Base URL:")
    try:
        config = StagehandConfig(
            model_name="gpt-4o",
            model_client_options={
                "api_base": "not-a-valid-url"
            }
        )
        # This will fail at Pydantic validation level
    except Exception as e:
        print(f"   ❌ Pydantic caught the error: {type(e).__name__}")
        print(f"      {str(e)}")
    print()


def demonstrate_api_key_validation():
    """Demonstrate API key validation."""
    print("🔑 API Key Validation Examples")
    print("-" * 40)
    
    # Save and clear environment for clean testing
    original_openai_key = os.getenv("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        # Test 1: No API key
        print("1. No API Key Provided:")
        result = validate_api_key_configuration("gpt-4o", None, None)
        if not result["valid"]:
            print("   ❌ No API key found")
            for error in result["errors"]:
                print(f"      • {error}")
        print()
        
        # Test 2: API key in model_client_options
        print("2. API Key in model_client_options:")
        result = validate_api_key_configuration(
            "gpt-4o", 
            None, 
            {"api_key": "sk-test-key"}
        )
        if result["valid"]:
            print(f"   ✅ API key found in {result['api_key_source']}")
        print()
        
        # Test 3: API key in environment
        print("3. API Key in Environment:")
        os.environ["OPENAI_API_KEY"] = "sk-env-test-key"
        result = validate_api_key_configuration("gpt-4o", None, None)
        if result["valid"]:
            print(f"   ✅ API key found in {result['api_key_source']}")
        print()
        
    finally:
        # Restore original environment
        if original_openai_key:
            os.environ["OPENAI_API_KEY"] = original_openai_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def demonstrate_helpful_error_messages():
    """Demonstrate helpful error message generation."""
    print("💬 Helpful Error Messages")
    print("-" * 40)
    
    # Create a validation result with multiple issues
    validation_result = {
        "valid": False,
        "errors": [
            "No API key found for openai provider. Please provide an API key via model_api_key, model_client_options['api_key'], or set the OPENAI_API_KEY environment variable.",
            "Invalid api_base URL: api_base must be a valid HTTP/HTTPS URL"
        ],
        "warnings": [
            "Using localhost/local IP - ensure this is intended for development",
            "Debug logging (verbose=2) may impact performance in production"
        ],
        "recommendations": [
            "Consider enabling caching for better performance",
            "Consider using HTTPS for security"
        ]
    }
    
    error_message = create_helpful_error_message(validation_result, "demonstration")
    print(error_message)
    print()


def demonstrate_environment_check():
    """Demonstrate environment setup checking."""
    print("🌍 Environment Setup Check")
    print("-" * 40)
    
    env_result = check_environment_setup()
    
    if env_result["issues"]:
        print("Issues found:")
        for issue in env_result["issues"]:
            print(f"   ❌ {issue}")
        print()
    
    if env_result["warnings"]:
        print("Warnings:")
        for warning in env_result["warnings"]:
            print(f"   ⚠️  {warning}")
        print()
    
    if env_result["recommendations"]:
        print("Recommendations:")
        for rec in env_result["recommendations"]:
            print(f"   ✅ {rec}")
        print()


def demonstrate_custom_endpoint_configuration():
    """Demonstrate configuration for custom API endpoints."""
    print("🔗 Custom API Endpoint Configuration Examples")
    print("-" * 40)
    
    examples = [
        {
            "name": "Together AI",
            "config": StagehandConfig(
                model_name="meta-llama/Llama-2-70b-chat-hf",
                model_client_options={
                    "api_base": "https://api.together.xyz/v1",
                    "api_key": "your-together-api-key"
                }
            )
        },
        {
            "name": "Local OpenAI-compatible server",
            "config": StagehandConfig(
                model_name="gpt-3.5-turbo",
                model_client_options={
                    "api_base": "http://localhost:8000/v1",
                    "api_key": "local-key"
                }
            )
        },
        {
            "name": "Groq",
            "config": StagehandConfig(
                model_name="mixtral-8x7b-32768",
                model_client_options={
                    "api_base": "https://api.groq.com/openai/v1",
                    "api_key": "your-groq-api-key"
                }
            )
        }
    ]
    
    for example in examples:
        print(f"📡 {example['name']}:")
        try:
            result = validate_stagehand_config(example["config"])
            if result["valid"]:
                print("   ✅ Configuration is valid")
                if result["warnings"]:
                    for warning in result["warnings"]:
                        print(f"   ⚠️  {warning}")
            else:
                print("   ❌ Configuration has issues:")
                for error in result["errors"]:
                    print(f"      • {error}")
        except Exception as e:
            print(f"   ❌ Validation failed: {e}")
        print()


def main():
    """Run all demonstration examples."""
    print("🚀 Stagehand Configuration Validation Examples")
    print("=" * 60)
    print()
    
    demonstrate_api_base_validation()
    demonstrate_provider_inference()
    demonstrate_configuration_validation()
    demonstrate_api_key_validation()
    demonstrate_helpful_error_messages()
    demonstrate_environment_check()
    demonstrate_custom_endpoint_configuration()
    
    print("=" * 60)
    print("✨ All examples completed!")
    print()
    print("💡 Tips:")
    print("   • Always validate your configuration before initializing Stagehand")
    print("   • Use environment variables for API keys in production")
    print("   • Check the logs for warnings and recommendations")
    print("   • Test your custom API endpoints before deployment")


if __name__ == "__main__":
    main()