#!/usr/bin/env python3
"""
Windows PowerShell Compatible Example for Stagehand

This example demonstrates:
1. Local browser automation without external dependencies
2. Multiple LLM provider configurations
3. Windows PowerShell compatibility
4. Error handling and validation
5. Structured data extraction

Prerequisites:
- Python 3.8+ installed
- Chrome/Chromium browser installed
- At least one LLM provider API key (OpenAI, Anthropic, etc.)

Usage in PowerShell:
    python examples/windows_powershell_example.py
    
Or with specific provider:
    $env:PREFERRED_PROVIDER="openai"; python examples/windows_powershell_example.py
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add the local stagehand directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from stagehand.main import Stagehand
from stagehand.config import StagehandConfig

# Load environment variables
load_dotenv()


class NewsArticle(BaseModel):
    """Model for news articles."""
    title: str = Field(..., description="Article title")
    summary: str = Field(..., description="Brief article summary")
    url: Optional[str] = Field(None, description="Article URL if available")


class NewsArticles(BaseModel):
    """Collection of news articles."""
    articles: List[NewsArticle] = Field(..., description="List of news articles")


def get_provider_configs():
    """Get available LLM provider configurations based on environment variables."""
    configs = {}
    
    # OpenAI configuration
    if os.getenv("OPENAI_API_KEY"):
        configs["openai"] = StagehandConfig(
            model_name="gpt-4o-mini",
            model_client_options={
                "api_base": "https://api.openai.com/v1",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "timeout": 30
            },
            local_browser_launch_options={
                "headless": False,
                "viewport": {"width": 1280, "height": 720}
            },
            verbose=1
        )
    
    # Anthropic configuration
    if os.getenv("ANTHROPIC_API_KEY"):
        configs["anthropic"] = StagehandConfig(
            model_name="claude-3-haiku-20240307",
            model_client_options={
                "api_base": "https://api.anthropic.com",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "timeout": 60
            },
            local_browser_launch_options={
                "headless": False,
                "viewport": {"width": 1280, "height": 720}
            },
            verbose=1
        )
    
    # Together AI configuration
    if os.getenv("TOGETHER_API_KEY"):
        configs["together"] = StagehandConfig(
            model_name="together/llama-2-7b-chat",
            model_client_options={
                "api_base": "https://api.together.xyz/v1",
                "api_key": os.getenv("TOGETHER_API_KEY"),
                "timeout": 45
            },
            local_browser_launch_options={
                "headless": False,
                "viewport": {"width": 1280, "height": 720}
            },
            verbose=1
        )
    
    # Groq configuration
    if os.getenv("GROQ_API_KEY"):
        configs["groq"] = StagehandConfig(
            model_name="groq/llama2-70b-4096",
            model_client_options={
                "api_base": "https://api.groq.com/openai/v1",
                "api_key": os.getenv("GROQ_API_KEY"),
                "timeout": 30
            },
            local_browser_launch_options={
                "headless": False,
                "viewport": {"width": 1280, "height": 720}
            },
            verbose=1
        )
    
    return configs


def select_provider_config(configs):
    """Select the best available provider configuration."""
    # Check for preferred provider from environment
    preferred = os.getenv("PREFERRED_PROVIDER", "").lower()
    if preferred and preferred in configs:
        print(f"✓ Using preferred provider: {preferred}")
        return preferred, configs[preferred]
    
    # Default priority order
    priority = ["openai", "anthropic", "groq", "together"]
    
    for provider in priority:
        if provider in configs:
            print(f"✓ Using available provider: {provider}")
            return provider, configs[provider]
    
    raise ValueError(
        "No LLM provider API keys found. Please set one of: "
        "OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, TOGETHER_API_KEY"
    )


async def demonstrate_basic_automation(stagehand):
    """Demonstrate basic browser automation capabilities."""
    print("\n" + "="*50)
    print("🤖 Demonstrating Basic Browser Automation")
    print("="*50)
    
    page = stagehand.page
    
    # Navigate to a news website
    print("📰 Navigating to BBC News...")
    await page.goto("https://www.bbc.com/news")
    print("✓ Successfully navigated to BBC News")
    
    # Extract news articles
    print("\n📊 Extracting top news articles...")
    try:
        articles_data = await page.extract(
            "Extract the titles and summaries of the top 5 news articles on the page",
            schema=NewsArticles
        )
        
        print(f"✓ Successfully extracted {len(articles_data.articles)} articles")
        
        # Display results
        print("\n📋 Extracted Articles:")
        for idx, article in enumerate(articles_data.articles, 1):
            print(f"\n{idx}. {article.title}")
            print(f"   Summary: {article.summary}")
            if article.url:
                print(f"   URL: {article.url}")
            print("-" * 40)
                
    except Exception as e:
        print(f"⚠ Error extracting articles: {e}")
    
    # Demonstrate observe functionality
    print("\n🔍 Demonstrating observe functionality...")
    try:
        observed = await page.observe("find the search box on the page")
        print(f"✓ Observed search element: {observed}")
    except Exception as e:
        print(f"⚠ Error observing elements: {e}")


async def demonstrate_windows_compatibility():
    """Demonstrate Windows-specific features and compatibility."""
    print("\n" + "="*50)
    print("🪟 Demonstrating Windows PowerShell Compatibility")
    print("="*50)
    
    # Check Windows environment
    if os.name == 'nt':
        print("✓ Running on Windows")
        print(f"  Python version: {sys.version}")
        print(f"  Working directory: {os.getcwd()}")
        
        # Demonstrate PowerShell command execution
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Get-Location"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ PowerShell integration working: {result.stdout.strip()}")
            else:
                print(f"⚠ PowerShell command failed: {result.stderr}")
        except Exception as e:
            print(f"⚠ PowerShell integration error: {e}")
    else:
        print(f"ℹ Running on {os.name} (not Windows)")
    
    # Check browser availability
    print("\n🌐 Checking browser availability...")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browsers = []
            if p.chromium.executable_path:
                browsers.append("Chromium")
            if hasattr(p, 'chrome') and p.chrome.executable_path:
                browsers.append("Chrome")
            if p.firefox.executable_path:
                browsers.append("Firefox")
            
            if browsers:
                print(f"✓ Available browsers: {', '.join(browsers)}")
            else:
                print("⚠ No browsers found")
    except Exception as e:
        print(f"⚠ Error checking browsers: {e}")


async def main():
    """Main function demonstrating Stagehand with Windows PowerShell compatibility."""
    print("🤘 Stagehand Windows PowerShell Example")
    print("=" * 50)
    
    try:
        # Get available provider configurations
        configs = get_provider_configs()
        
        if not configs:
            print("❌ No LLM provider API keys found!")
            print("\nPlease set one of the following environment variables:")
            print("  • OPENAI_API_KEY - for OpenAI GPT models")
            print("  • ANTHROPIC_API_KEY - for Anthropic Claude models")
            print("  • GROQ_API_KEY - for Groq models")
            print("  • TOGETHER_API_KEY - for Together AI models")
            print("\nExample PowerShell commands:")
            print("  $env:OPENAI_API_KEY='your-api-key-here'")
            print("  python examples/windows_powershell_example.py")
            return
        
        # Select provider configuration
        provider_name, config = select_provider_config(configs)
        
        print(f"\n🔧 Configuration Details:")
        print(f"  Provider: {provider_name}")
        print(f"  Model: {config.model_name}")
        print(f"  API Base: {config.model_client_options.get('api_base', 'default')}")
        print(f"  Timeout: {config.model_client_options.get('timeout', 'default')}s")
        print(f"  Browser: Local ({'headless' if config.local_browser_launch_options.get('headless') else 'headed'})")
        
        # Initialize Stagehand
        print(f"\n🚀 Initializing Stagehand with {provider_name}...")
        async with Stagehand(config=config) as stagehand:
            # Validate LLM configuration
            validation = stagehand.llm.validate_configuration()
            if validation['valid']:
                print(f"✓ LLM configured successfully")
                print(f"  Provider: {validation['configuration']['provider']}")
                print(f"  Model: {config.model_name}")
                print(f"  API Key: {'✓ Configured' if validation['configuration']['api_key_configured'] else '❌ Missing'}")
            else:
                print("⚠ LLM configuration issues:")
                for error in validation['errors']:
                    print(f"  • {error}")
            
            # Demonstrate Windows compatibility
            await demonstrate_windows_compatibility()
            
            # Demonstrate basic automation
            await demonstrate_basic_automation(stagehand)
            
            print("\n" + "="*50)
            print("🎉 Example completed successfully!")
            print("="*50)
            
            print("\n💡 Tips for Windows PowerShell users:")
            print("  • Use $env:VARIABLE_NAME to set environment variables")
            print("  • Use semicolons (;) instead of && for command chaining")
            print("  • Run 'python -m pip install stagehand' to install")
            print("  • Use './run_tests.ps1' to run tests with PowerShell")
            print("  • Use './format.ps1' to format code with PowerShell")
            
    except KeyboardInterrupt:
        print("\n\n⏹ Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Set up Windows-specific console encoding if needed
    if os.name == 'nt':
        try:
            # Ensure proper UTF-8 encoding on Windows
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
        except:
            pass  # Fallback to default encoding
    
    asyncio.run(main())