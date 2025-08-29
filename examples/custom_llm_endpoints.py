#!/usr/bin/env python3
"""
Example demonstrating how to use Stagehand with custom LLM API endpoints.

This example shows how to configure Stagehand to work with different LLM providers
including OpenAI, Anthropic, Together AI, Groq, and custom endpoints.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the local stagehand directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from stagehand.main import Stagehand
from stagehand.config import StagehandConfig


async def example_openai_custom_endpoint():
    """Example using OpenAI with custom endpoint configuration."""
    print("Example 1: OpenAI with custom endpoint")
    print("-" * 40)
    
    config = StagehandConfig(
        model_name="gpt-4o-mini",
        model_client_options={
            "api_base": "https://api.openai.com/v1",
            "api_key": os.getenv("OPENAI_API_KEY", "your-openai-key"),
            "timeout": 30,
            "max_retries": 3
        },
        verbose=1
    )
    
    async with Stagehand(config=config) as stagehand:
        print(f"✓ Initialized Stagehand with OpenAI model: {config.model_name}")
        print(f"  API Base: {config.model_client_options['api_base']}")
        print(f"  Timeout: {config.model_client_options['timeout']}s")
        
        # Validate LLM configuration
        validation = stagehand.llm.validate_configuration()
        print(f"  Configuration valid: {validation['valid']}")
        print(f"  Provider: {validation['configuration']['provider']}")


async def example_anthropic_configuration():
    """Example using Anthropic Claude with custom configuration."""
    print("\nExample 2: Anthropic Claude configuration")
    print("-" * 40)
    
    config = StagehandConfig(
        model_name="claude-3-haiku-20240307",
        model_client_options={
            "api_base": "https://api.anthropic.com",
            "api_key": os.getenv("ANTHROPIC_API_KEY", "your-anthropic-key"),
            "timeout": 60
        },
        verbose=1
    )
    
    async with Stagehand(config=config) as stagehand:
        print(f"✓ Initialized Stagehand with Anthropic model: {config.model_name}")
        print(f"  API Base: {config.model_client_options['api_base']}")
        
        validation = stagehand.llm.validate_configuration()
        print(f"  Configuration valid: {validation['valid']}")
        print(f"  Provider: {validation['configuration']['provider']}")


async def example_together_ai_configuration():
    """Example using Together AI with custom configuration."""
    print("\nExample 3: Together AI configuration")
    print("-" * 40)
    
    config = StagehandConfig(
        model_name="together/llama-2-7b-chat",
        model_client_options={
            "api_base": "https://api.together.xyz/v1",
            "api_key": os.getenv("TOGETHER_API_KEY", "your-together-key"),
            "timeout": 45,
            "max_retries": 2
        },
        verbose=1
    )
    
    async with Stagehand(config=config) as stagehand:
        print(f"✓ Initialized Stagehand with Together AI model: {config.model_name}")
        print(f"  API Base: {config.model_client_options['api_base']}")
        
        validation = stagehand.llm.validate_configuration()
        print(f"  Configuration valid: {validation['valid']}")
        print(f"  Provider: {validation['configuration']['provider']}")


async def example_groq_configuration():
    """Example using Groq with custom configuration."""
    print("\nExample 4: Groq configuration")
    print("-" * 40)
    
    config = StagehandConfig(
        model_name="groq/llama2-70b-4096",
        model_client_options={
            "api_base": "https://api.groq.com/openai/v1",
            "api_key": os.getenv("GROQ_API_KEY", "your-groq-key"),
            "timeout": 30
        },
        verbose=1
    )
    
    async with Stagehand(config=config) as stagehand:
        print(f"✓ Initialized Stagehand with Groq model: {config.model_name}")
        print(f"  API Base: {config.model_client_options['api_base']}")
        
        validation = stagehand.llm.validate_configuration()
        print(f"  Configuration valid: {validation['valid']}")
        print(f"  Provider: {validation['configuration']['provider']}")


async def example_local_openai_server():
    """Example using a local OpenAI-compatible server."""
    print("\nExample 5: Local OpenAI-compatible server")
    print("-" * 40)
    
    config = StagehandConfig(
        model_name="local/custom-model",
        model_client_options={
            "api_base": "http://localhost:8000/v1",
            "api_key": "local-key",
            "timeout": 120  # Local servers might be slower
        },
        verbose=1
    )
    
    async with Stagehand(config=config) as stagehand:
        print(f"✓ Initialized Stagehand with local model: {config.model_name}")
        print(f"  API Base: {config.model_client_options['api_base']}")
        
        validation = stagehand.llm.validate_configuration()
        print(f"  Configuration valid: {validation['valid']}")
        print(f"  Provider: {validation['configuration']['provider']}")


async def example_environment_variable_fallback():
    """Example showing environment variable fallback for API keys."""
    print("\nExample 6: Environment variable fallback")
    print("-" * 40)
    
    # Set environment variable for demonstration
    os.environ["OPENAI_API_KEY"] = "demo-key-from-env"
    
    config = StagehandConfig(
        model_name="gpt-4o-mini",
        model_client_options={
            "api_base": "https://api.openai.com/v1",
            # No api_key specified - should use environment variable
        },
        verbose=1
    )
    
    async with Stagehand(config=config) as stagehand:
        print(f"✓ Initialized Stagehand using environment variable for API key")
        print(f"  Model: {config.model_name}")
        
        validation = stagehand.llm.validate_configuration()
        print(f"  Configuration valid: {validation['valid']}")
        print(f"  API key configured: {validation['configuration']['api_key_configured']}")
    
    # Clean up
    del os.environ["OPENAI_API_KEY"]


async def example_error_handling():
    """Example demonstrating error handling for invalid configurations."""
    print("\nExample 7: Error handling for invalid configurations")
    print("-" * 40)
    
    try:
        # This should fail due to invalid API base
        config = StagehandConfig(
            model_name="gpt-4o",
            model_client_options={
                "api_base": "not-a-valid-url",
                "api_key": "test-key"
            }
        )
        print("✗ Should have failed with invalid URL")
        
    except ValueError as e:
        print(f"✓ Correctly caught configuration error: {e}")
    
    try:
        # This should fail due to negative timeout
        config = StagehandConfig(
            model_name="gpt-4o",
            model_client_options={
                "api_base": "https://api.openai.com/v1",
                "timeout": -10
            }
        )
        print("✗ Should have failed with negative timeout")
        
    except ValueError as e:
        print(f"✓ Correctly caught timeout validation error: {e}")


async def main():
    """Run all examples."""
    print("Stagehand Custom LLM Endpoints Examples")
    print("=" * 50)
    
    try:
        await example_openai_custom_endpoint()
        await example_anthropic_configuration()
        await example_together_ai_configuration()
        await example_groq_configuration()
        await example_local_openai_server()
        await example_environment_variable_fallback()
        await example_error_handling()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("\nKey features demonstrated:")
        print("• Custom API endpoint configuration")
        print("• Multiple LLM provider support")
        print("• Environment variable fallback")
        print("• Configuration validation")
        print("• Error handling")
        print("• Timeout and retry configuration")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())