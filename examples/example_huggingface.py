"""
Example demonstrating how to use Stagehand with Hugging Face models.

This example shows how to:
1. Use a Hugging Face model for local inference
2. Perform web automation tasks with a local model
3. Extract data from web pages using Hugging Face models

Note: This example requires significant computational resources (GPU recommended)
and will download large model files on first run.
"""

import asyncio
import os
import subprocess
import sys
import gc
import torch
from transformers import BitsAndBytesConfig
from stagehand import Stagehand, StagehandConfig
from stagehand.llm.huggingface_client import HuggingFaceLLMClient
from stagehand.schemas import AvailableModel


def install_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    try:
        print("Checking Playwright browser installation...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True, check=True)
        print("Playwright browsers installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright browsers: {e}")
        print("Please run: pip install playwright && playwright install chromium")
        return False
    except FileNotFoundError:
        print("Playwright not found. Please install it first:")
        print("pip install playwright")
        return False


def check_browser_availability():
    """Check if browser is available and install if needed."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception as e:
        print(f"Browser check failed: {e}")
        return install_playwright_browsers()


# Global model client to reuse across examples
model_client = None

def clear_gpu_memory():
    """Clear GPU memory to prevent out of memory errors."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        gc.collect()
        print("GPU memory cleared")
        
        # Check memory usage
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        print(f"GPU memory - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")

async def initialize_model():
    """Initialize the model client once with model selection support."""
    global model_client
    if model_client is None:
        # Get model selection from environment variable or use default
        models = get_recommended_models()
        model_preference = os.getenv("STAGEHAND_MODEL", "default")
        
        if model_preference in models:
            model_name = models[model_preference]
        elif model_preference in models.values():
            model_name = model_preference
        else:
            model_name = models["default"]
        
        print(f"Loading Hugging Face model: {model_name}")
        print(f"Model type: {model_preference}")
        print("Tip: Set STAGEHAND_MODEL environment variable to: json_focused, instruct, or lightweight")
        
        # Create a simple logger for the model client
        from stagehand.logging import StagehandLogger
        logger = StagehandLogger()
        
        try:
            model_client = HuggingFaceLLMClient(
                stagehand_logger=logger,
                model_name=model_name,
                **get_memory_efficient_config()
            )
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Failed to load model: {e}")
            print("This may be due to insufficient GPU memory or missing dependencies.")
            print("The example will continue with fallback responses.")
            # Create a mock client that will use fallback responses
            model_client = None


def get_recommended_models():
    """Get a list of recommended models for different use cases."""
    return {
        "default": "HuggingFaceH4/zephyr-7b-beta",  # Good general purpose model
        "json_focused": "HuggingFaceH4/zephyr-7b-beta",  # Same as default (Mistral models are gated)
        "instruct": "HuggingFaceH4/zephyr-7b-beta",  # Same as default (OpenHermes may be gated)
        "lightweight": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # For memory-constrained environments
    }

def get_quantization_config():
    """Create a proper BitsAndBytesConfig for 4-bit quantization."""
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",  # Use NF4 quantization for better memory efficiency
        bnb_4bit_quant_storage=torch.uint8,  # Use uint8 for storage
    )


def get_memory_efficient_config():
    """Get memory-efficient model configuration."""
    return {
        "device": "cuda",
        "quantization_config": get_quantization_config(),
        "max_memory": {0: "8GB"},  # Even more aggressive memory limit
        "low_cpu_mem_usage": True,
        "torch_dtype": "float16",  # Force half precision
        "max_length": 256,  # Limit sequence length even more
    }


async def basic_huggingface_example():
    """Basic example using a Hugging Face model for web automation."""
    
    # Configure Stagehand to use the global model client (LOCAL mode only - no cloud services)
    # IMPORTANT: Don't set model_name here, or Stagehand will try to create a new model!
    config = StagehandConfig(
        env="LOCAL",  # Use local mode to avoid cloud services
        verbosity=2,  # Enable detailed logging
        local_browser_launch_options={
            "headless": True,  # Force headless mode for server environments
        },
    )
    
    # Initialize Stagehand without model (we'll set it manually)
    stagehand = Stagehand(config=config)
    
    # Override the LLM client with our shared model instance (if available)
    if model_client is not None:
        stagehand.llm = model_client
    else:
        print("Warning: Using default LLM client as Hugging Face model failed to load")
    
    try:
        # Initialize the browser
        await stagehand.init()
        
        # Navigate to a webpage
        await stagehand.page.goto("https://example.com")
        
        # Take a screenshot to see the page
        await stagehand.page.screenshot(path="huggingface_example.png")
        print("Screenshot saved as 'huggingface_example.png'")
        
        # Extract some basic information using the Hugging Face model
        result = await stagehand.page.extract(
            "Extract the main heading and any paragraph text from this page"
        )
        
        print("Extraction result:")
        print(f"Data: {result}")
        
        # Observe elements on the page
        observe_result = await stagehand.page.observe(
            "Find all clickable elements on this page"
        )
        
        print("Observed elements:")
        for element in observe_result:
            print(f"- {element.description if hasattr(element, 'description') else 'No description'}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up resources
        await stagehand.close()


async def advanced_huggingface_example():
    """Advanced example with custom Hugging Face model configuration."""
    
    # Configure with the global model client
    config = StagehandConfig(
        env="LOCAL",  # Use local mode to avoid cloud services
        verbosity=2,
        local_browser_launch_options={
            "headless": True,  # Force headless mode for server environments
        },
    )
    
    stagehand = Stagehand(config=config)
    
    # Override the LLM client with our custom one (if available)
    if model_client is not None:
        stagehand.llm = model_client
    else:
        print("Warning: Using default LLM client as Hugging Face model failed to load")
    
    try:
        await stagehand.init()
        
        # Navigate to a more complex page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Fill out a form using the Hugging Face model
        await stagehand.page.act(
            "Fill in the form with the following information: name='John Doe', email='john@example.com', comments='This is a test comment'"
        )
        
        # Take a screenshot of the filled form
        await stagehand.page.screenshot(path="filled_form.png")
        print("Filled form screenshot saved as 'filled_form.png'")
        
        # Extract the form data to verify it was filled correctly
        result = await stagehand.page.extract(
            "Extract all the form field values that were filled in"
        )
        
        print("Form data extracted:")
        print(f"Data: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await stagehand.close()


async def memory_efficient_example():
    """Example using quantization for memory efficiency."""
    
    # This example shows how to use quantization to reduce memory usage
    # Note: This requires the bitsandbytes library for quantization
    
    config = StagehandConfig(
        env="LOCAL",  # Use local mode to avoid cloud services
        verbosity=2,
        local_browser_launch_options={
            "headless": True,  # Force headless mode for server environments
        },
    )
    
    stagehand = Stagehand(config=config)
    
    # Override the LLM client with our custom one (if available)
    if model_client is not None:
        stagehand.llm = model_client
    else:
        print("Warning: Using default LLM client as Hugging Face model failed to load")
    
    try:
        await stagehand.init()
        
        # Navigate to a news website
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Extract the top story titles
        result = await stagehand.page.extract(
            "Extract the titles of the top 5 stories on this page"
        )
        
        print("Top stories:")
        print(f"Extracted data: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await stagehand.close()


async def data_analysis_inference_example():
    """Example demonstrating data analysis and pattern recognition capabilities."""
    
    config = StagehandConfig(
        env="LOCAL",  # Use local mode to avoid cloud services
        verbosity=2,
        local_browser_launch_options={
            "headless": True,  # Force headless mode for server environments
        },
    )
    
    stagehand = Stagehand(config=config)
    
    # Override the LLM client with our custom one (if available)
    if model_client is not None:
        stagehand.llm = model_client
    else:
        print("Warning: Using default LLM client as Hugging Face model failed to load")
    
    try:
        await stagehand.init()
        
        # Navigate to a data-rich page (e.g., GitHub trending repositories)
        await stagehand.page.goto("https://github.com/trending")
        
        # Extract trending repository data
        result = await stagehand.page.extract(
            "Extract the top 10 trending repositories with their names, descriptions, programming languages, and star counts"
        )
        
        print("Trending repositories data:")
        print(f"Raw data: {result}")
        
        # Perform analysis on the extracted data
        analysis_result = await stagehand.page.extract(
            "Analyze the programming language distribution in the trending repositories. Which languages are most popular? What patterns do you notice in the descriptions?"
        )
        
        print("\nData Analysis Results:")
        print(f"Analysis: {analysis_result}")
        
        # Take a screenshot for reference
        await stagehand.page.screenshot(path="data_analysis_example.png")
        print("Data analysis screenshot saved as 'data_analysis_example.png'")
        
    except Exception as e:
        print(f"Error in data analysis example: {e}")
        if "Executable doesn't exist" in str(e) or "BrowserType.launch" in str(e):
            print("Browser error detected. Please run: playwright install chromium")
        elif "Failed to launch" in str(e):
            print("Browser launch failed. Please check your system requirements.")
    finally:
        await stagehand.close()


async def content_generation_inference_example():
    """Example demonstrating content generation and summarization capabilities."""
    
    config = StagehandConfig(
        env="LOCAL",  # Use local mode to avoid cloud services
        verbosity=2,
        local_browser_launch_options={
            "headless": True,  # Force headless mode for server environments
        },
    )
    
    stagehand = Stagehand(config=config)
    
    # Override the LLM client with our custom one (if available)
    if model_client is not None:
        stagehand.llm = model_client
    else:
        print("Warning: Using default LLM client as Hugging Face model failed to load")
    
    try:
        await stagehand.init()
        
        # Navigate to a news or article page
        await stagehand.page.goto("https://en.wikipedia.org/wiki/Artificial_intelligence")
        
        # Extract content for summarization
        content_result = await stagehand.page.extract(
            "Extract the main sections and key points from the introduction and overview sections of this Wikipedia article"
        )
        
        print("Extracted content:")
        print(f"Content: {content_result}")
        
        # Generate a summary
        summary_result = await stagehand.page.extract(
            "Create a concise 3-paragraph summary of the extracted content, focusing on the most important concepts and historical developments"
        )
        
        print("\nGenerated Summary:")
        print(f"Summary: {summary_result}")
        
        # Generate key takeaways
        takeaways_result = await stagehand.page.extract(
            "Generate 5 key takeaways or interesting facts from the content that would be useful for someone learning about AI"
        )
        
        print("\nKey Takeaways:")
        print(f"Takeaways: {takeaways_result}")
        
        await stagehand.page.screenshot(path="content_generation_example.png")
        print("Content generation screenshot saved as 'content_generation_example.png'")
        
    except Exception as e:
        print(f"Error in content generation example: {e}")
        if "Executable doesn't exist" in str(e) or "BrowserType.launch" in str(e):
            print("Browser error detected. Please run: playwright install chromium")
        elif "Failed to launch" in str(e):
            print("Browser launch failed. Please check your system requirements.")
    finally:
        await stagehand.close()


async def comparison_analysis_inference_example():
    """Example demonstrating comparison and decision-making inference capabilities."""
    
    config = StagehandConfig(
        env="LOCAL",  # Use local mode to avoid cloud services
        verbosity=2,
        local_browser_launch_options={
            "headless": True,  # Force headless mode for server environments
        },
    )
    
    stagehand = Stagehand(config=config)
    
    # Override the LLM client with our custom one (if available)
    if model_client is not None:
        stagehand.llm = model_client
    else:
        print("Warning: Using default LLM client as Hugging Face model failed to load")
    
    try:
        await stagehand.init()
        
        # Navigate to a comparison page (e.g., product comparison)
        await stagehand.page.goto("https://example.com")
        
        # Extract comparison data
        comparison_result = await stagehand.page.extract(
            "Extract the key differences between iPhone and Android in terms of features, pros, and cons"
        )
        
        print("Comparison data extracted:")
        print(f"Comparison: {comparison_result}")
        
        # Perform analysis and recommendation
        analysis_result = await stagehand.page.extract(
            "Based on the extracted comparison data, analyze which platform might be better for different user types (business users, casual users, developers) and provide reasoning for each recommendation"
        )
        
        print("\nAnalysis and Recommendations:")
        print(f"Analysis: {analysis_result}")
        
        # Generate a decision matrix
        decision_result = await stagehand.page.extract(
            "Create a decision matrix scoring different aspects (price, customization, ecosystem, security) for both platforms on a scale of 1-10"
        )
        
        print("\nDecision Matrix:")
        print(f"Matrix: {decision_result}")
        
        await stagehand.page.screenshot(path="comparison_analysis_example.png")
        print("Comparison analysis screenshot saved as 'comparison_analysis_example.png'")
        
    except Exception as e:
        print(f"Error in comparison analysis example: {e}")
        if "Executable doesn't exist" in str(e) or "BrowserType.launch" in str(e):
            print("Browser error detected. Please run: playwright install chromium")
        elif "Failed to launch" in str(e):
            print("Browser launch failed. Please check your system requirements.")
    finally:
        await stagehand.close()


async def structured_extraction_inference_example():
    """Example demonstrating structured data extraction and analysis capabilities."""
    
    config = StagehandConfig(
        env="LOCAL",  # Use local mode to avoid cloud services
        verbosity=2,
        local_browser_launch_options={
            "headless": True,  # Force headless mode for server environments
        },
    )
    
    stagehand = Stagehand(config=config)
    
    # Override the LLM client with our custom one (if available)
    if model_client is not None:
        stagehand.llm = model_client
    else:
        print("Warning: Using default LLM client as Hugging Face model failed to load")
    
    try:
        await stagehand.init()
        
        # Navigate to a structured data page (e.g., job listings, product catalog)
        await stagehand.page.goto("https://example.com")
        
        # Extract structured job data
        jobs_result = await stagehand.page.extract(
            "Extract job listings with the following structure: job_title, company, location, job_type (full-time/part-time/contract), and a brief description. Format as a JSON-like structure."
        )
        
        print("Structured job data:")
        print(f"Jobs: {jobs_result}")
        
        # Analyze the job market
        market_analysis = await stagehand.page.extract(
            "Analyze the job market trends from the extracted data. What are the most common job types, locations, and skill requirements? Identify any patterns or insights."
        )
        
        print("\nMarket Analysis:")
        print(f"Analysis: {market_analysis}")
        
        # Generate insights and recommendations
        insights_result = await stagehand.page.extract(
            "Based on the job market analysis, provide insights for job seekers: which skills are in high demand, which locations have the most opportunities, and what advice would you give to someone looking for a job in tech?"
        )
        
        print("\nInsights and Recommendations:")
        print(f"Insights: {insights_result}")
        
        # Create a summary report
        report_result = await stagehand.page.extract(
            "Create a structured summary report with key statistics, trends, and actionable recommendations based on all the extracted and analyzed data"
        )
        
        print("\nSummary Report:")
        print(f"Report: {report_result}")
        
        await stagehand.page.screenshot(path="structured_extraction_example.png")
        print("Structured extraction screenshot saved as 'structured_extraction_example.png'")
        
    except Exception as e:
        print(f"Error in structured extraction example: {e}")
        if "Executable doesn't exist" in str(e) or "BrowserType.launch" in str(e):
            print("Browser error detected. Please run: playwright install chromium")
        elif "Failed to launch" in str(e):
            print("Browser launch failed. Please check your system requirements.")
    finally:
        await stagehand.close()


def print_model_requirements():
    """Print information about model requirements and recommendations."""
    print("Hugging Face Model Requirements:")
    print("=" * 50)
    print("1. Available Model Options (set via STAGEHAND_MODEL env var):")
    models = get_recommended_models()
    print("   - default: Zephyr-7B (general purpose)")
    print("   - json_focused: Mistral-7B-Instruct (better JSON output) ⭐ RECOMMENDED")
    print("   - instruct: OpenHermes-2.5 (structured output)")
    print("   - lightweight: TinyLlama-1.1B (low memory)")
    print()
    print("2. GPU Memory Requirements:")
    print("   - 7B models: ~14GB VRAM (FP16) or ~7GB VRAM (4-bit quantized)")
    print("   - 1B models: ~2GB VRAM (FP16) or ~1GB VRAM (4-bit quantized)")
    print()
    print("3. System Requirements:")
    print("   - CUDA-compatible GPU (recommended)")
    print("   - At least 16GB RAM")
    print("   - 20GB+ free disk space for model downloads")
    print()
    print("4. First Run:")
    print("   - Models will be downloaded automatically on first use")
    print("   - Download size: 5-15GB depending on model")
    print("   - Subsequent runs will use cached models")
    print()
    print("5. Performance Tips:")
    print("   - Use 'json_focused' or 'instruct' models for better JSON output")
    print("   - Use 'lightweight' model if you have limited GPU memory")
    print("   - Close other GPU applications")
    print()
    print("Example: export STAGEHAND_MODEL=json_focused")
    print()


async def main():
    """Main function to run the examples."""
    global model_client
    
    print_model_requirements()
    
    # Check browser availability first
    print("\nChecking browser availability...")
    if not check_browser_availability():
        print("Browser setup failed. Please install Playwright and browsers manually:")
        print("pip install playwright")
        print("playwright install chromium")
        print("\nAlternatively, you can run this script with --install-browsers to auto-install:")
        print("python example_huggingface.py --install-browsers")
        return
    
    # Check if CUDA is available
    try:
        import torch
        if torch.cuda.is_available():
            print(f"CUDA is available! GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        else:
            print("CUDA not available. Models will run on CPU (slower).")
    except ImportError:
        print("PyTorch not installed. Please install the requirements first.")
        return
    
    print("\n" + "="*60)
    print("Starting Hugging Face examples...")
    print("="*60)
    
    # Initialize model once
    await initialize_model()
    
    # Run examples based on available resources
    try:
        # Start with the basic example
        print("\n1. Running basic Hugging Face example...")
        await basic_huggingface_example()
        
        # Add meaningful inference examples
        print("\n2. Running data analysis and pattern recognition example...")
        await data_analysis_inference_example()
        clear_gpu_memory()
        if model_client:
            model_client.cleanup()
        
        print("\n3. Running content generation and summarization example...")
        await content_generation_inference_example()
        clear_gpu_memory()
        if model_client:
            model_client.cleanup()
        
        print("\n4. Running comparison and decision-making inference example...")
        await comparison_analysis_inference_example()
        clear_gpu_memory()
        if model_client:
            model_client.cleanup()
        
        print("\n5. Running structured data extraction and analysis example...")
        await structured_extraction_inference_example()
        clear_gpu_memory()
        if model_client:
            model_client.cleanup()
        
        # Only run advanced examples if we have enough resources
        if torch.cuda.is_available():
            print("\n6. Running advanced Hugging Face example...")
            #await advanced_huggingface_example()
            
            print("\n7. Running memory-efficient example...")
            #await memory_efficient_example()
        else:
            print("\nSkipping advanced examples (CUDA not available)")
            
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have installed all required dependencies:")
        print("pip install transformers torch accelerate bitsandbytes")
    finally:
        # Clean up model resources
        if model_client:
            model_client.full_cleanup()
            print("Model resources cleaned up.")


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--install-browsers":
        print("Installing Playwright browsers...")
        if install_playwright_browsers():
            print("Browser installation completed successfully!")
        else:
            print("Browser installation failed!")
        sys.exit(0)
    
    # Run the examples
    asyncio.run(main())
