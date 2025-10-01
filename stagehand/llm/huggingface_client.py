"""Hugging Face LLM client for local model interactions."""

import asyncio
import json
import time
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)

from stagehand.metrics import get_inference_time_ms, start_inference_timer

if TYPE_CHECKING:
    from ..logging import StagehandLogger


class HuggingFaceLLMClient:
    """
    Client for making LLM calls using Hugging Face transformers library.
    Provides a simplified interface for chat completions with local models.
    """

    def __init__(
        self,
        stagehand_logger: "StagehandLogger",
        model_name: str,
        device: Optional[str] = None,
        quantization_config: Optional[BitsAndBytesConfig] = None,
        trust_remote_code: bool = False,
        metrics_callback: Optional[Callable[[Any, int, Optional[str]], None]] = None,
        **kwargs: Any,
    ):
        """
        Initialize the Hugging Face LLM client.

        Args:
            stagehand_logger: StagehandLogger instance for centralized logging
            model_name: The Hugging Face model name (e.g., "meta-llama/Llama-2-7b-chat-hf")
            device: Device to run the model on ("cpu", "cuda", "auto")
            quantization_config: Quantization configuration for memory optimization
            trust_remote_code: Whether to trust remote code in model loading
            metrics_callback: Optional callback to track metrics from responses
            **kwargs: Additional parameters for model loading
        """
        self.logger = stagehand_logger
        self.model_name = model_name
        self.metrics_callback = metrics_callback
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        self.logger.info(f"Loading Hugging Face model: {model_name} on {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=trust_remote_code,
            **kwargs
        )
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        model_kwargs = {
            "trust_remote_code": trust_remote_code,
            "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
        }
        
        if quantization_config:
            model_kwargs["quantization_config"] = quantization_config
            model_kwargs["device_map"] = "auto"
        else:
            model_kwargs["device_map"] = self.device
            
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs,
            **kwargs
        )
        
        # Create text generation pipeline
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device_map=self.device if not quantization_config else "auto",
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        )
        
        self.logger.info(f"Successfully loaded model: {model_name}")

    def _format_messages(self, messages: list[dict[str, str]]) -> str:
        """
        Format messages for the model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Formatted string for the model
        """
        formatted_text = ""
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                formatted_text += f"System: {content}\n\n"
            elif role == "user":
                formatted_text += f"Human: {content}\n\n"
            elif role == "assistant":
                formatted_text += f"Assistant: {content}\n\n"
        
        # Add assistant prompt for completion
        if not formatted_text.endswith("Assistant:"):
            formatted_text += "Assistant:"
            
        return formatted_text

    def _parse_response(self, response: str) -> dict[str, Any]:
        """
        Parse the model response into the expected format.
        
        Args:
            response: Raw response from the model
            
        Returns:
            Parsed response in litellm-compatible format
        """
        # Extract the assistant's response
        if "Assistant:" in response:
            content = response.split("Assistant:")[-1].strip()
        else:
            content = response.strip()
        
        # Create a mock response object that matches litellm's format
        class MockUsage:
            def __init__(self, prompt_tokens: int, completion_tokens: int):
                self.prompt_tokens = prompt_tokens
                self.completion_tokens = completion_tokens
                self.total_tokens = prompt_tokens + completion_tokens
        
        class MockChoice:
            def __init__(self, content: str):
                self.message = type('Message', (), {'content': content})()
        
        class MockResponse:
            def __init__(self, content: str, prompt_tokens: int, completion_tokens: int):
                self.choices = [MockChoice(content)]
                self.usage = MockUsage(prompt_tokens, completion_tokens)
        
        # Estimate token counts (rough approximation)
        prompt_tokens = len(self.tokenizer.encode(response, add_special_tokens=False))
        completion_tokens = len(self.tokenizer.encode(content, add_special_tokens=False))
        
        return MockResponse(content, prompt_tokens, completion_tokens)

    async def create_response(
        self,
        *,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        function_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate a chat completion response using Hugging Face model.

        Args:
            messages: A list of message dictionaries, e.g., [{"role": "user", "content": "Hello"}].
            model: The specific model to use (ignored, uses the loaded model)
            function_name: The name of the Stagehand function calling this method (ACT, OBSERVE, etc.)
            temperature: Sampling temperature for generation
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional parameters for text generation

        Returns:
            A dictionary containing the completion response in litellm-compatible format
        """
        if model and model != self.model_name:
            self.logger.warning(f"Model {model} requested but using loaded model {self.model_name}")
        
        # Format messages for the model
        formatted_input = self._format_messages(messages)
        
        self.logger.debug(
            f"Generating response with Hugging Face model: {self.model_name}",
            category="llm"
        )
        
        try:
            # Start tracking inference time
            start_time = start_inference_timer()
            
            # Run generation in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_text,
                formatted_input,
                temperature,
                max_tokens,
                **kwargs
            )
            
            # Calculate inference time
            inference_time_ms = get_inference_time_ms(start_time)
            
            # Parse response
            parsed_response = self._parse_response(response)
            
            # Update metrics if callback is provided
            if self.metrics_callback:
                self.metrics_callback(parsed_response, inference_time_ms, function_name)
            
            return parsed_response
            
        except Exception as e:
            self.logger.error(f"Error generating response with Hugging Face model: {e}", category="llm")
            raise

    def _generate_text(
        self,
        input_text: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using the Hugging Face pipeline.
        
        Args:
            input_text: Input text for generation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        generation_kwargs = {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            **kwargs
        }
        
        # Generate response
        outputs = self.pipeline(
            input_text,
            **generation_kwargs
        )
        
        # Extract the generated text
        if isinstance(outputs, list) and len(outputs) > 0:
            generated_text = outputs[0].get("generated_text", "")
            # Remove the input text from the generated text
            if generated_text.startswith(input_text):
                generated_text = generated_text[len(input_text):].strip()
            return generated_text
        else:
            return ""

    def cleanup(self):
        """Clean up model resources."""
        if hasattr(self, 'model'):
            del self.model
        if hasattr(self, 'tokenizer'):
            del self.tokenizer
        if hasattr(self, 'pipeline'):
            del self.pipeline
        
        # Clear CUDA cache if using GPU
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("Cleaned up Hugging Face model resources")
