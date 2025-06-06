"""Performance tests for Stagehand functionality"""

import pytest
import asyncio
import time
import psutil
import os
from unittest.mock import AsyncMock, MagicMock, patch

from stagehand import Stagehand, StagehandConfig
from tests.mocks.mock_llm import MockLLMClient
from tests.mocks.mock_browser import create_mock_browser_stack


@pytest.mark.performance
class TestMemoryUsagePerformance:
    """Test memory usage performance for various operations"""
    
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)  # Convert to MB
    
    @pytest.mark.asyncio
    async def test_memory_usage_during_operations(self, mock_stagehand_config):
        """Test that memory usage stays within acceptable bounds during operations"""
        initial_memory = self.get_memory_usage()
        
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("act", {"success": True, "action": "click"})
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.act = AsyncMock(return_value=MagicMock(success=True))
            stagehand._initialized = True
            
            try:
                # Perform multiple operations
                for i in range(10):
                    await stagehand.page.act(f"operation {i}")
                
                final_memory = self.get_memory_usage()
                memory_increase = final_memory - initial_memory
                
                # Memory increase should be reasonable (< 50MB for 10 operations)
                assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"
                
            finally:
                stagehand._closed = True
    

# TODO: account for init()
@pytest.mark.performance
@pytest.mark.slow
class TestLongRunningPerformance:
    """Test performance for long-running operations"""
    
    @pytest.mark.asyncio
    async def test_extended_session_performance(self, mock_stagehand_config):
        """Test performance over extended session duration"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("act", {"success": True})
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.act = AsyncMock(return_value=MagicMock(success=True))
            stagehand._initialized = True
            
            try:
                initial_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                response_times = []
                
                # Perform many operations over time
                for i in range(50):  # Reduced for testing
                    start_time = time.time()
                    result = await stagehand.page.act(f"extended operation {i}")
                    end_time = time.time()
                    
                    response_times.append(end_time - start_time)
                    
                    # Small delay between operations
                    await asyncio.sleep(0.01)
                
                final_memory = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
                memory_increase = final_memory - initial_memory
                
                # Performance should remain consistent
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                assert avg_response_time < 0.1, f"Average response time degraded: {avg_response_time:.3f}s"
                assert max_response_time < 0.5, f"Max response time too high: {max_response_time:.3f}s"
                assert memory_increase < 100, f"Memory leak detected: {memory_increase:.2f}MB increase"
                
            finally:
                stagehand._closed = True 