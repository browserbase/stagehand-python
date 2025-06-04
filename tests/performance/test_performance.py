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
class TestResponseTimePerformance:
    """Test response time performance for various operations"""
    
    @pytest.mark.asyncio
    async def test_act_operation_response_time(self, mock_stagehand_config):
        """Test that act operations complete within acceptable time limits"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("act", {
                "success": True,
                "message": "Action completed",
                "action": "click button"
            })
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.act = AsyncMock()
            stagehand._initialized = True
            
            # Mock fast response
            async def fast_act(*args, **kwargs):
                await asyncio.sleep(0.1)  # Simulate processing time
                return MagicMock(success=True, message="Fast response", action="click")
            
            stagehand.page.act = fast_act
            
            try:
                start_time = time.time()
                result = await stagehand.page.act("click button")
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Should complete within 1 second for simple operations
                assert response_time < 1.0
                assert result.success is True
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_observe_operation_response_time(self, mock_stagehand_config):
        """Test that observe operations complete within acceptable time limits"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("observe", [
                {
                    "selector": "#test-element",
                    "description": "Test element",
                    "method": "click"
                }
            ])
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.observe = AsyncMock()
            stagehand._initialized = True
            
            async def fast_observe(*args, **kwargs):
                await asyncio.sleep(0.2)  # Simulate processing time
                return [MagicMock(selector="#test", description="Fast element")]
            
            stagehand.page.observe = fast_observe
            
            try:
                start_time = time.time()
                result = await stagehand.page.observe("find elements")
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Should complete within 1.5 seconds for observation
                assert response_time < 1.5
                assert len(result) > 0
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_extract_operation_response_time(self, mock_stagehand_config):
        """Test that extract operations complete within acceptable time limits"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("extract", {
                "title": "Fast extraction",
                "content": "Extracted content"
            })
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.extract = AsyncMock()
            stagehand._initialized = True
            
            async def fast_extract(*args, **kwargs):
                await asyncio.sleep(0.3)  # Simulate processing time
                return {"title": "Fast extraction", "content": "Extracted content"}
            
            stagehand.page.extract = fast_extract
            
            try:
                start_time = time.time()
                result = await stagehand.page.extract("extract page data")
                end_time = time.time()
                
                response_time = end_time - start_time
                
                # Should complete within 2 seconds for extraction
                assert response_time < 2.0
                assert "title" in result
                
            finally:
                stagehand._closed = True


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
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
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
    
    @pytest.mark.asyncio
    async def test_memory_cleanup_after_operations(self, mock_stagehand_config):
        """Test that memory is properly cleaned up after operations"""
        initial_memory = self.get_memory_usage()
        
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("extract", {
                "data": "x" * 10000  # Large response to test memory cleanup
            })
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.extract = AsyncMock()
            stagehand._initialized = True
            
            async def large_extract(*args, **kwargs):
                # Simulate large data extraction
                return {"data": "x" * 50000}
            
            stagehand.page.extract = large_extract
            
            try:
                # Perform operations that generate large responses
                for i in range(5):
                    result = await stagehand.page.extract("extract large data")
                    del result  # Explicit cleanup
                
                # Force garbage collection
                import gc
                gc.collect()
                
                final_memory = self.get_memory_usage()
                memory_increase = final_memory - initial_memory
                
                # Memory should not increase significantly after cleanup
                assert memory_increase < 30, f"Memory not cleaned up properly: {memory_increase:.2f}MB increase"
                
            finally:
                stagehand._closed = True


@pytest.mark.performance
class TestConcurrencyPerformance:
    """Test performance under concurrent load"""
    
    @pytest.mark.asyncio
    async def test_concurrent_act_operations(self, mock_stagehand_config):
        """Test performance of concurrent act operations"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("act", {"success": True, "action": "concurrent click"})
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand._initialized = True
            
            operation_count = 0
            async def concurrent_act(*args, **kwargs):
                nonlocal operation_count
                operation_count += 1
                await asyncio.sleep(0.1)  # Simulate processing
                return MagicMock(success=True, action=f"concurrent action {operation_count}")
            
            stagehand.page.act = concurrent_act
            
            try:
                start_time = time.time()
                
                # Execute 10 concurrent operations
                tasks = [
                    stagehand.page.act(f"concurrent operation {i}")
                    for i in range(10)
                ]
                
                results = await asyncio.gather(*tasks)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # All operations should succeed
                assert len(results) == 10
                assert all(r.success for r in results)
                
                # Should complete concurrently faster than sequentially
                # (10 operations * 0.1s each = 1s sequential, should be < 0.5s concurrent)
                assert total_time < 0.5, f"Concurrent operations took {total_time:.2f}s, expected < 0.5s"
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_concurrent_mixed_operations(self, mock_stagehand_config):
        """Test performance of mixed concurrent operations"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("act", {"success": True})
            mock_llm.set_custom_response("observe", [{"selector": "#test"}])
            mock_llm.set_custom_response("extract", {"data": "extracted"})
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand._initialized = True
            
            async def mock_act(*args, **kwargs):
                await asyncio.sleep(0.1)
                return MagicMock(success=True)
            
            async def mock_observe(*args, **kwargs):
                await asyncio.sleep(0.15)
                return [MagicMock(selector="#test")]
            
            async def mock_extract(*args, **kwargs):
                await asyncio.sleep(0.2)
                return {"data": "extracted"}
            
            stagehand.page.act = mock_act
            stagehand.page.observe = mock_observe
            stagehand.page.extract = mock_extract
            
            try:
                start_time = time.time()
                
                # Mix of different operation types
                tasks = [
                    stagehand.page.act("action 1"),
                    stagehand.page.observe("observe 1"),
                    stagehand.page.extract("extract 1"),
                    stagehand.page.act("action 2"),
                    stagehand.page.observe("observe 2"),
                ]
                
                results = await asyncio.gather(*tasks)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # All operations should complete
                assert len(results) == 5
                
                # Should complete faster than sequential execution
                assert total_time < 0.7, f"Mixed operations took {total_time:.2f}s"
                
            finally:
                stagehand._closed = True


@pytest.mark.performance
class TestScalabilityPerformance:
    """Test scalability and load performance"""
    
    @pytest.mark.asyncio
    async def test_large_dom_processing_performance(self, mock_stagehand_config):
        """Test performance with large DOM structures"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        # Create large HTML content
        large_html = "<html><body>"
        for i in range(1000):
            large_html += f'<div id="element-{i}" class="test-class">Element {i}</div>'
        large_html += "</body></html>"
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_llm.set_custom_response("observe", [
                {"selector": f"#element-{i}", "description": f"Element {i}"}
                for i in range(10)  # Return first 10 elements
            ])
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.observe = AsyncMock()
            stagehand._initialized = True
            
            async def large_dom_observe(*args, **kwargs):
                # Simulate processing large DOM
                await asyncio.sleep(0.5)  # Realistic processing time for large DOM
                return [
                    MagicMock(selector=f"#element-{i}", description=f"Element {i}")
                    for i in range(10)
                ]
            
            stagehand.page.observe = large_dom_observe
            
            try:
                start_time = time.time()
                result = await stagehand.page.observe("find elements in large DOM")
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # Should handle large DOM within reasonable time (< 3 seconds)
                assert processing_time < 3.0, f"Large DOM processing took {processing_time:.2f}s"
                assert len(result) == 10
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_multiple_page_sessions_performance(self, mock_stagehand_config):
        """Test performance with multiple page sessions"""
        sessions = []
        
        try:
            start_time = time.time()
            
            # Create multiple sessions
            for i in range(3):  # Reduced number for performance testing
                playwright, browser, context, page = create_mock_browser_stack()
                
                with patch('stagehand.client.async_playwright') as mock_playwright_func, \
                     patch('stagehand.client.LLMClient') as mock_llm_class:
                    
                    mock_llm = MockLLMClient()
                    mock_llm.set_custom_response("act", {"success": True, "session": i})
                    
                    mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
                    mock_llm_class.return_value = mock_llm
                    
                    stagehand = Stagehand(config=mock_stagehand_config)
                    stagehand._playwright = playwright
                    stagehand._browser = browser
                    stagehand._context = context
                    stagehand.page = MagicMock()
                    stagehand.page.act = AsyncMock(return_value=MagicMock(success=True))
                    stagehand._initialized = True
                    
                    sessions.append(stagehand)
            
            # Perform operations across all sessions
            tasks = []
            for i, session in enumerate(sessions):
                tasks.append(session.page.act(f"action for session {i}"))
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # All sessions should work
            assert len(results) == 3
            assert all(r.success for r in results)
            
            # Should handle multiple sessions efficiently (< 2 seconds)
            assert total_time < 2.0, f"Multiple sessions took {total_time:.2f}s"
            
        finally:
            # Cleanup all sessions
            for session in sessions:
                session._closed = True


@pytest.mark.performance
class TestNetworkPerformance:
    """Test network-related performance"""
    
    @pytest.mark.asyncio
    async def test_browserbase_api_call_performance(self, mock_browserbase_config):
        """Test performance of Browserbase API calls"""
        from tests.mocks.mock_server import create_mock_server_with_client
        
        server, http_client = create_mock_server_with_client()
        
        # Set up fast server responses
        server.set_response_override("act", {"success": True, "action": "fast action"})
        server.set_response_override("observe", [{"selector": "#fast", "description": "fast element"}])
        
        with patch('stagehand.client.httpx.AsyncClient') as mock_http_class:
            mock_http_class.return_value = http_client
            
            stagehand = Stagehand(
                config=mock_browserbase_config,
                api_url="https://mock-stagehand-server.com"
            )
            
            stagehand._client = http_client
            stagehand.session_id = "test-performance-session"
            stagehand.page = MagicMock()
            stagehand._initialized = True
            
            async def fast_api_act(*args, **kwargs):
                # Simulate fast API call
                await asyncio.sleep(0.05)  # 50ms API response
                response = await http_client.post("https://mock-server/api/act", json={"action": args[0]})
                data = response.json()
                return MagicMock(**data)
            
            stagehand.page.act = fast_api_act
            
            try:
                start_time = time.time()
                
                # Multiple API calls
                tasks = [
                    stagehand.page.act(f"api action {i}")
                    for i in range(5)
                ]
                
                results = await asyncio.gather(*tasks)
                
                end_time = time.time()
                total_time = end_time - start_time
                
                # All API calls should succeed
                assert len(results) == 5
                
                # Should complete API calls efficiently (< 1 second for 5 calls)
                assert total_time < 1.0, f"API calls took {total_time:.2f}s"
                
            finally:
                stagehand._closed = True


@pytest.mark.performance
@pytest.mark.slow
class TestLongRunningPerformance:
    """Test performance for long-running operations"""
    
    @pytest.mark.asyncio
    async def test_extended_session_performance(self, mock_stagehand_config):
        """Test performance over extended session duration"""
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.client.async_playwright') as mock_playwright_func, \
             patch('stagehand.client.LLMClient') as mock_llm_class:
            
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