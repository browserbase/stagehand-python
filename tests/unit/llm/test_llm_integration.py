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
    
    @pytest.mark.asyncio
    async def test_api_authentication_error(self):
        """Test handling of API authentication errors"""
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "Invalid API key")
        
        messages = [{"role": "user", "content": "Test auth error"}]
        
        with pytest.raises(Exception) as exc_info:
            await mock_llm.completion(messages)
        
        assert "Invalid API key" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_api_timeout_error(self):
        """Test handling of API timeout errors"""
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "Request timeout")
        
        messages = [{"role": "user", "content": "Test timeout"}]
        
        with pytest.raises(Exception) as exc_info:
            await mock_llm.completion(messages)
        
        assert "Request timeout" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses"""
        mock_llm = MockLLMClient()
        
        # Set a malformed response
        mock_llm.set_custom_response("default", None)  # Invalid response
        
        messages = [{"role": "user", "content": "Test malformed response"}]
        
        # Should handle gracefully or raise appropriate error
        try:
            response = await mock_llm.completion(messages)
            # If it succeeds, should have some default handling
            assert response is not None
        except Exception as e:
            # If it fails, should be a specific error type
            assert "malformed" in str(e).lower() or "invalid" in str(e).lower()

class TestLLMMetrics:
    """Test LLM metrics collection and monitoring"""
    
    @pytest.mark.asyncio
    async def test_call_count_tracking(self):
        """Test that LLM call count is properly tracked"""
        mock_llm = MockLLMClient()
        mock_llm.set_custom_response("default", "Count tracking test")
        
        messages = [{"role": "user", "content": "Test call counting"}]
        
        initial_count = mock_llm.call_count
        
        await mock_llm.completion(messages)
        assert mock_llm.call_count == initial_count + 1
        
        await mock_llm.completion(messages)
        assert mock_llm.call_count == initial_count + 2
    
    @pytest.mark.asyncio
    async def test_usage_statistics_aggregation(self):
        """Test aggregation of usage statistics"""
        mock_llm = MockLLMClient()
        mock_llm.set_custom_response("default", "Usage stats test")
        
        messages = [{"role": "user", "content": "Test usage statistics"}]
        
        # Make multiple calls
        await mock_llm.completion(messages)
        await mock_llm.completion(messages)
        await mock_llm.completion(messages)
        
        usage_stats = mock_llm.get_usage_stats()
        
        assert usage_stats["total_calls"] == 3
        assert usage_stats["total_prompt_tokens"] > 0
        assert usage_stats["total_completion_tokens"] > 0
        assert usage_stats["total_tokens"] > 0
    
    @pytest.mark.asyncio
    async def test_call_history_tracking(self):
        """Test that call history is properly maintained"""
        mock_llm = MockLLMClient()
        mock_llm.set_custom_response("default", "History tracking test")
        
        messages1 = [{"role": "user", "content": "First call"}]
        messages2 = [{"role": "user", "content": "Second call"}]
        
        await mock_llm.completion(messages1, model="gpt-4o")
        await mock_llm.completion(messages2, model="gpt-4o-mini")
        
        history = mock_llm.get_call_history()
        
        assert len(history) == 2
        assert history[0]["messages"] == messages1
        assert history[0]["model"] == "gpt-4o"
        assert history[1]["messages"] == messages2
        assert history[1]["model"] == "gpt-4o-mini"