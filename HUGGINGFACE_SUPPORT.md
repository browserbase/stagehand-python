# Hugging Face Model Support

Stagehand now supports using open-source Hugging Face models for local inference! This allows you to run web automation tasks without relying on external API services.

## Supported Models

The following Hugging Face models are pre-configured and ready to use:

- **Llama 2 7B Chat** (`huggingface/meta-llama/Llama-2-7b-chat-hf`)
- **Llama 2 13B Chat** (`huggingface/meta-llama/Llama-2-13b-chat-hf`)
- **Mistral 7B Instruct** (`huggingface/mistralai/Mistral-7B-Instruct-v0.1`)
- **Zephyr 7B Beta** (`huggingface/HuggingFaceH4/zephyr-7b-beta`)
- **CodeGen 2.5B Mono** (`huggingface/Salesforce/codegen-2B-mono`)
- **StarCoder2 7B** (`huggingface/bigcode/starcoder2-7b`)

## Requirements

### Hardware Requirements
- **GPU**: CUDA-compatible GPU with at least 8GB VRAM (recommended)
- **RAM**: At least 16GB system RAM
- **Storage**: 20GB+ free space for model downloads

### Software Requirements
- Python 3.9+
- CUDA toolkit (for GPU acceleration)
- PyTorch with CUDA support

## Installation

Install the required dependencies:

```bash
pip install transformers torch accelerate bitsandbytes
```

For GPU support, make sure you have the appropriate CUDA version installed.

## Basic Usage

```python
import asyncio
from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import AvailableModel

async def main():
    # Configure Stagehand to use a Hugging Face model
    config = StagehandConfig(
        env="LOCAL",
        model_name=AvailableModel.HUGGINGFACE_ZEPHYR_7B,
        verbose=2,
        use_api=False,
    )
    
    stagehand = Stagehand(config=config)
    
    try:
        await stagehand.init()
        await stagehand.navigate("https://example.com")
        
        # Extract data using the Hugging Face model
        result = await stagehand.extract(
            instruction="Extract the main heading from this page"
        )
        
        print(f"Extracted: {result.data}")
        
    finally:
        await stagehand.close()

asyncio.run(main())
```

## Advanced Configuration

### Memory Optimization

For systems with limited GPU memory, you can use quantization:

```python
config = StagehandConfig(
    env="LOCAL",
    model_name=AvailableModel.HUGGINGFACE_LLAMA_2_7B,
    use_api=False,
    model_client_options={
        "device": "cuda",
        "quantization_config": {
            "load_in_4bit": True,
            "bnb_4bit_compute_dtype": "float16",
            "bnb_4bit_use_double_quant": True,
        }
    }
)
```

### Custom Models

You can also use any Hugging Face model by specifying the full model name:

```python
config = StagehandConfig(
    env="LOCAL",
    model_name="huggingface/your-username/your-model",
    use_api=False,
)
```

## Performance Tips

1. **Use GPU**: Always use CUDA if available for significantly faster inference
2. **Quantization**: Use 4-bit or 8-bit quantization to reduce memory usage
3. **Model Size**: Start with smaller models (7B parameters) for testing
4. **Batch Processing**: Process multiple tasks in sequence rather than parallel
5. **Memory Management**: Close other GPU applications when running large models

## Troubleshooting

### Out of Memory Errors
- Use quantization (`load_in_4bit=True`)
- Try a smaller model
- Close other GPU applications
- Use CPU mode (slower but uses less memory)

### Slow Performance
- Ensure CUDA is properly installed
- Use GPU instead of CPU
- Try a smaller model
- Check if other processes are using GPU

### Model Download Issues
- Check internet connection
- Ensure sufficient disk space
- Try downloading manually from Hugging Face Hub

## Examples

See `examples/example_huggingface.py` for comprehensive examples including:
- Basic usage with different models
- Memory-efficient configurations
- Form filling and data extraction
- Error handling and troubleshooting

## Limitations

- **First Run**: Models are downloaded on first use (5-15GB)
- **Memory**: Large models require significant GPU memory
- **Speed**: Local inference is slower than API calls
- **Model Quality**: Some models may not perform as well as commercial APIs

## Contributing

To add support for new Hugging Face models:

1. Add the model to `AvailableModel` enum in `schemas.py`
2. Test the model with various web automation tasks
3. Update this documentation
4. Add tests for the new model

## Support

For issues related to Hugging Face model support:
- Check the [Hugging Face documentation](https://huggingface.co/docs)
- Review the example file for usage patterns
- Open an issue on the GitHub repository
