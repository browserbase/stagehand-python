"""Test LLM integration functionality including different providers and response handling"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from stagehand.llm.client import LLMClient
from tests.mocks.mock_llm import MockLLMClient, MockLLMResponse


class TestLLMClientInitialization:
    """Test LLM client initialization and setup"""
    
    def test_llm_client_creation_with_openai(self):
        """Test LLM client creation with OpenAI provider"""
        client = LLMClient(
            api_key="test-openai-key",
            default_model="gpt-4o"
        )
        
        assert client.default_model == "gpt-4o"
        # Note: api_key is set globally on litellm, not stored on client
    
    def test_llm_client_creation_with_anthropic(self):
        """Test LLM client creation with Anthropic provider"""
        client = LLMClient(
            api_key="test-anthropic-key",
            default_model="claude-3-sonnet"
        )
        
        assert client.default_model == "claude-3-sonnet"
        # Note: api_key is set globally on litellm, not stored on client
    
    def test_llm_client_with_custom_options(self):
        """Test LLM client with custom configuration options"""
        client = LLMClient(
            api_key="test-key",
            default_model="gpt-4o-mini"
        )
        
        assert client.default_model == "gpt-4o-mini"
        # Note: LLMClient doesn't store temperature, max_tokens, timeout as instance attributes
        # These are passed as kwargs to the completion method


# TODO: let's do these in integration rather than simulation
class TestLLMErrorHandling:
    """Test LLM error handling and recovery"""
    
    @pytest.mark.asyncio
    async def test_api_rate_limit_error(self):
        """Test handling of API rate limit errors"""
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "Rate limit exceeded")
        
        messages = [{"role": "user", "content": "Test rate limit"}]
        
        with pytest.raises(Exception) as exc_info:
            await mock_llm.completion(messages)
        
        assert "Rate limit exceeded" in str(exc_info.value)