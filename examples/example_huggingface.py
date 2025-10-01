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
from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import AvailableModel


async def basic_huggingface_example():
    """Basic example using a Hugging Face model for web automation."""
    
    # Configure Stagehand to use a Hugging Face model
    config = StagehandConfig(
        env="LOCAL",  # Use local mode for Hugging Face models
        model_name=AvailableModel.HUGGINGFACE_ZEPHYR_7B,  # Use Zephyr 7B model
        verbose=2,  # Enable detailed logging
        use_api=False,  # Disable API mode for local models
    )
    
    # Initialize Stagehand with Hugging Face model
    stagehand = Stagehand(config=config)
    
    try:
        # Initialize the browser
        await stagehand.init()
        
        # Navigate to a webpage
        await stagehand.navigate("https://example.com")
        
        # Take a screenshot to see the page
        await stagehand.screenshot("huggingface_example.png")
        print("Screenshot saved as 'huggingface_example.png'")
        
        # Extract some basic information using the Hugging Face model
        result = await stagehand.extract(
            instruction="Extract the main heading and any paragraph text from this page"
        )
        
        print("Extraction result:")
        print(f"Data: {result.data}")
        print(f"Metadata: {result.metadata}")
        
        # Observe elements on the page
        observe_result = await stagehand.observe(
            instruction="Find all clickable elements on this page"
        )
        
        print("Observed elements:")
        for element in observe_result.elements:
            print(f"- {element.get('description', 'No description')}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up resources
        await stagehand.close()


async def advanced_huggingface_example():
    """Advanced example with custom Hugging Face model configuration."""
    
    # Configure with a more powerful model and custom settings
    config = StagehandConfig(
        env="LOCAL",
        model_name=AvailableModel.HUGGINGFACE_LLAMA_2_7B,  # Use Llama 2 7B
        verbose=2,
        use_api=False,
        # Custom model client options for Hugging Face
        model_client_options={
            "device": "cuda",  # Use GPU if available
            "trust_remote_code": True,
            "torch_dtype": "float16",  # Use half precision for memory efficiency
        }
    )
    
    stagehand = Stagehand(config=config)
    
    try:
        await stagehand.init()
        
        # Navigate to a more complex page
        await stagehand.navigate("https://httpbin.org/forms/post")
        
        # Fill out a form using the Hugging Face model
        await stagehand.act(
            action="Fill in the form with the following information: name='John Doe', email='john@example.com', comments='This is a test comment'"
        )
        
        # Take a screenshot of the filled form
        await stagehand.screenshot("filled_form.png")
        print("Filled form screenshot saved as 'filled_form.png'")
        
        # Extract the form data to verify it was filled correctly
        result = await stagehand.extract(
            instruction="Extract all the form field values that were filled in"
        )
        
        print("Form data extracted:")
        print(f"Data: {result.data}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await stagehand.close()


async def memory_efficient_example():
    """Example using quantization for memory efficiency."""
    
    # This example shows how to use quantization to reduce memory usage
    # Note: This requires the bitsandbytes library for quantization
    
    config = StagehandConfig(
        env="LOCAL",
        model_name=AvailableModel.HUGGINGFACE_MISTRAL_7B,
        verbose=2,
        use_api=False,
        model_client_options={
            "device": "cuda",
            "quantization_config": {
                "load_in_4bit": True,  # Use 4-bit quantization
                "bnb_4bit_compute_dtype": "float16",
                "bnb_4bit_use_double_quant": True,
            }
        }
    )
    
    stagehand = Stagehand(config=config)
    
    try:
        await stagehand.init()
        
        # Navigate to a news website
        await stagehand.navigate("https://news.ycombinator.com")
        
        # Extract the top story titles
        result = await stagehand.extract(
            instruction="Extract the titles of the top 5 stories on this page"
        )
        
        print("Top stories:")
        if isinstance(result.data, dict) and 'stories' in result.data:
            for i, story in enumerate(result.data['stories'], 1):
                print(f"{i}. {story}")
        else:
            print(f"Extracted data: {result.data}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await stagehand.close()


def print_model_requirements():
    """Print information about model requirements and recommendations."""
    print("Hugging Face Model Requirements:")
    print("=" * 50)
    print("1. GPU Memory Requirements:")
    print("   - Zephyr 7B: ~14GB VRAM (FP16) or ~7GB VRAM (4-bit quantized)")
    print("   - Llama 2 7B: ~14GB VRAM (FP16) or ~7GB VRAM (4-bit quantized)")
    print("   - Mistral 7B: ~14GB VRAM (FP16) or ~7GB VRAM (4-bit quantized)")
    print("   - CodeGen 2.5B: ~5GB VRAM (FP16) or ~3GB VRAM (4-bit quantized)")
    print()
    print("2. System Requirements:")
    print("   - CUDA-compatible GPU (recommended)")
    print("   - At least 16GB RAM")
    print("   - 20GB+ free disk space for model downloads")
    print()
    print("3. First Run:")
    print("   - Models will be downloaded automatically on first use")
    print("   - Download size: 5-15GB depending on model")
    print("   - Subsequent runs will use cached models")
    print()
    print("4. Performance Tips:")
    print("   - Use quantization for lower memory usage")
    print("   - Close other GPU applications")
    print("   - Consider using smaller models for testing")
    print()


async def main():
    """Main function to run the examples."""
    print_model_requirements()
    
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
    
    # Run examples based on available resources
    try:
        # Start with the basic example
        print("\n1. Running basic Hugging Face example...")
        await basic_huggingface_example()
        
        # Only run advanced examples if we have enough resources
        if torch.cuda.is_available():
            print("\n2. Running advanced Hugging Face example...")
            await advanced_huggingface_example()
            
            print("\n3. Running memory-efficient example...")
            await memory_efficient_example()
        else:
            print("\nSkipping advanced examples (CUDA not available)")
            
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("Make sure you have installed all required dependencies:")
        print("pip install transformers torch accelerate bitsandbytes")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
