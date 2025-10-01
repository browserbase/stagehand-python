"""Test Hugging Face LLM client functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import torch

from stagehand.llm.huggingface_client import HuggingFaceLLMClient
from stagehand.logging import StagehandLogger


class TestHuggingFaceLLMClient:
    """Test Hugging Face LLM client functionality."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        return MagicMock(spec=StagehandLogger)
    
    @pytest.fixture
    def mock_model_and_tokenizer(self):
        """Mock the model and tokenizer for testing."""
        with patch('stagehand.llm.huggingface_client.AutoTokenizer') as mock_tokenizer_class, \
             patch('stagehand.llm.huggingface_client.AutoModelForCausalLM') as mock_model_class, \
             patch('stagehand.llm.huggingface_client.pipeline') as mock_pipeline:
            
            # Mock tokenizer
            mock_tokenizer = MagicMock()
            mock_tokenizer.pad_token = None
            mock_tokenizer.eos_token = "<|endoftext|>"
            mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
            
            # Mock model
            mock_model = MagicMock()
            mock_model_class.from_pretrained.return_value = mock_model
            
            # Mock pipeline
            mock_pipe = MagicMock()
            mock_pipe.return_value = [{"generated_text": "This is a test response"}]
            mock_pipeline.return_value = mock_pipe
            
            yield mock_tokenizer, mock_model, mock_pipe
    
    def test_client_initialization(self, mock_logger, mock_model_and_tokenizer):
        """Test Hugging Face client initialization."""
        mock_tokenizer, mock_model, mock_pipeline = mock_model_and_tokenizer
        
        client = HuggingFaceLLMClient(
            stagehand_logger=mock_logger,
            model_name="test-model",
            device="cpu"
        )
        
        assert client.model_name == "test-model"
        assert client.device == "cpu"
        assert client.logger == mock_logger
        
        # Verify model and tokenizer were loaded
        mock_tokenizer_class = mock_model_and_tokenizer[0].__class__
        mock_tokenizer_class.from_pretrained.assert_called_once()
        mock_model_class = mock_model_and_tokenizer[1].__class__
        mock_model_class.from_pretrained.assert_called_once()
    
    def test_format_messages(self, mock_logger, mock_model_and_tokenizer):
        """Test message formatting."""
        client = HuggingFaceLLMClient(
            stagehand_logger=mock_logger,
            model_name="test-model",
            device="cpu"
        )
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]
        
        formatted = client._format_messages(messages)
        
        expected = "System: You are a helpful assistant.\n\nHuman: Hello, how are you?\n\nAssistant: I'm doing well, thank you!\n\nAssistant:"
        assert formatted == expected
    
    def test_parse_response(self, mock_logger, mock_model_and_tokenizer):
        """Test response parsing."""
        client = HuggingFaceLLMClient(
            stagehand_logger=mock_logger,
            model_name="test-model",
            device="cpu"
        )
        
        response = "Human: Hello\nAssistant: Hi there! How can I help you?"
        parsed = client._parse_response(response)
        
        assert hasattr(parsed, 'choices')
        assert hasattr(parsed, 'usage')
        assert len(parsed.choices) == 1
        assert parsed.choices[0].message.content == "Hi there! How can I help you?"
        assert parsed.usage.prompt_tokens > 0
        assert parsed.usage.completion_tokens > 0
    
    @pytest.mark.asyncio
    async def test_create_response(self, mock_logger, mock_model_and_tokenizer):
        """Test response creation."""
        client = HuggingFaceLLMClient(
            stagehand_logger=mock_logger,
            model_name="test-model",
            device="cpu"
        )
        
        messages = [
            {"role": "user", "content": "Hello, world!"}
        ]
        
        # Mock the _generate_text method to avoid actual model inference
        with patch.object(client, '_generate_text', return_value="Hello! How can I help you?"):
            response = await client.create_response(
                messages=messages,
                temperature=0.7,
                max_tokens=100
            )
        
        assert hasattr(response, 'choices')
        assert hasattr(response, 'usage')
        assert len(response.choices) == 1
        assert "Hello! How can I help you?" in response.choices[0].message.content
    
    def test_cleanup(self, mock_logger, mock_model_and_tokenizer):
        """Test resource cleanup."""
        client = HuggingFaceLLMClient(
            stagehand_logger=mock_logger,
            model_name="test-model",
            device="cpu"
        )
        
        # Mock torch.cuda.is_available to avoid CUDA dependency in tests
        with patch('torch.cuda.is_available', return_value=False):
            client.cleanup()
        
        # Verify cleanup was called (attributes should be deleted)
        assert not hasattr(client, 'model')
        assert not hasattr(client, 'tokenizer')
        assert not hasattr(client, 'pipeline')
    
    def test_generate_text(self, mock_logger, mock_model_and_tokenizer):
        """Test text generation."""
        client = HuggingFaceLLMClient(
            stagehand_logger=mock_logger,
            model_name="test-model",
            device="cpu"
        )
        
        # Mock the pipeline call
        mock_pipeline = mock_model_and_tokenizer[2]
        mock_pipeline.return_value = [{"generated_text": "Input textThis is a generated response"}]
        
        result = client._generate_text(
            input_text="Input text",
            temperature=0.7,
            max_tokens=50
        )
        
        assert result == "This is a generated response"
        mock_pipeline.assert_called_once()
    
    def test_device_auto_detection(self, mock_logger, mock_model_and_tokenizer):
        """Test automatic device detection."""
        with patch('torch.cuda.is_available', return_value=True):
            client = HuggingFaceLLMClient(
                stagehand_logger=mock_logger,
                model_name="test-model"
            )
            assert client.device == "cuda"
        
        with patch('torch.cuda.is_available', return_value=False):
            client = HuggingFaceLLMClient(
                stagehand_logger=mock_logger,
                model_name="test-model"
            )
            assert client.device == "cpu"


class TestHuggingFaceIntegration:
    """Test integration with the main LLM client."""
    
    def test_llm_client_create_huggingface_client(self):
        """Test the static method to create Hugging Face clients."""
        from stagehand.llm.client import LLMClient
        from stagehand.logging import StagehandLogger
        
        mock_logger = MagicMock(spec=StagehandLogger)
        
        with patch('stagehand.llm.client.HuggingFaceLLMClient') as mock_hf_client:
            client = LLMClient.create_huggingface_client(
                stagehand_logger=mock_logger,
                model_name="test-model",
                device="cpu"
            )
            
            mock_hf_client.assert_called_once_with(
                stagehand_logger=mock_logger,
                model_name="test-model",
                device="cpu",
                metrics_callback=None
            )
