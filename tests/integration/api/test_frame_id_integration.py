"""
Integration tests for frame ID functionality with the API.
Tests that frame IDs are properly tracked and sent to the server.
"""

import pytest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from stagehand import Stagehand


@pytest.mark.skipif(
    not os.getenv("BROWSERBASE_API_KEY") or not os.getenv("BROWSERBASE_PROJECT_ID"),
    reason="Browserbase credentials not configured"
)
@pytest.mark.asyncio
class TestFrameIdIntegration:
    """Integration tests for frame ID tracking with the API."""
    
    async def test_frame_id_initialization_and_api_calls(self):
        """Test that frame IDs are initialized and included in API calls."""
        # Mock the HTTP client to capture API calls
        with patch('stagehand.main.httpx.AsyncClient') as MockClient:
            mock_client = AsyncMock()
            MockClient.return_value = mock_client
            
            # Mock session creation response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "data": {
                    "sessionId": "test-session-123",
                    "available": True
                }
            }
            mock_client.post = AsyncMock(return_value=mock_response)
            
            # Mock streaming response for execute calls
            mock_stream_response = AsyncMock()
            mock_stream_response.status_code = 200
            mock_stream_response.__aenter__ = AsyncMock(return_value=mock_stream_response)
            mock_stream_response.__aexit__ = AsyncMock()
            
            # Mock the async iterator for streaming lines
            async def mock_aiter_lines():
                yield 'data: {"type": "system", "data": {"status": "finished", "result": {"success": true}}}'
            
            mock_stream_response.aiter_lines = mock_aiter_lines
            mock_client.stream = MagicMock(return_value=mock_stream_response)
            
            # Initialize Stagehand
            stagehand = Stagehand(
                env="BROWSERBASE",
                use_api=True,
                browserbase_api_key="test-api-key",
                browserbase_project_id="test-project",
                model_api_key="test-model-key"
            )
            
            try:
                # Initialize browser (this will create session via API)
                await stagehand.init()
                
                # Verify session was created
                assert mock_client.post.called
                
                # Get the page and context
                page = stagehand.page
                context = stagehand.context
                
                # Verify frame tracking attributes exist
                assert hasattr(page, 'frame_id')
                assert hasattr(context, 'frame_id_map')
                
                # Simulate setting a frame ID (normally done by CDP listener)
                test_frame_id = "test-frame-456"
                page.update_root_frame_id(test_frame_id)
                context.register_frame_id(test_frame_id, page)
                
                # Test that frame ID is included in navigate call
                await page.goto("https://example.com")
                
                # Check the stream call was made with frameId
                stream_call_args = mock_client.stream.call_args
                if stream_call_args:
                    payload = stream_call_args[1].get('json', {})
                    assert 'frameId' in payload
                    assert payload['frameId'] == test_frame_id
                
            finally:
                await stagehand.close()
    
    async def test_multiple_pages_frame_id_tracking(self):
        """Test frame ID tracking with multiple pages."""
        with patch('stagehand.main.httpx.AsyncClient') as MockClient:
            mock_client = AsyncMock()
            MockClient.return_value = mock_client
            
            # Setup mocks as in previous test
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "data": {
                    "sessionId": "test-session-789",
                    "available": True
                }
            }
            mock_client.post = AsyncMock(return_value=mock_response)
            
            stagehand = Stagehand(
                env="BROWSERBASE",
                use_api=True,
                browserbase_api_key="test-api-key",
                browserbase_project_id="test-project",
                model_api_key="test-model-key"
            )
            
            try:
                await stagehand.init()
                
                # Get first page
                page1 = stagehand.page
                context = stagehand.context
                
                # Simulate frame IDs for testing
                frame_id_1 = "frame-page1"
                page1.update_root_frame_id(frame_id_1)
                context.register_frame_id(frame_id_1, page1)
                
                # Create second page
                page2 = await context.new_page()
                frame_id_2 = "frame-page2"
                page2.update_root_frame_id(frame_id_2)
                context.register_frame_id(frame_id_2, page2)
                
                # Verify both pages are tracked
                assert len(context.frame_id_map) == 2
                assert context.get_stagehand_page_by_frame_id(frame_id_1) == page1
                assert context.get_stagehand_page_by_frame_id(frame_id_2) == page2
                
                # Verify each page has its own frame ID
                assert page1.frame_id == frame_id_1
                assert page2.frame_id == frame_id_2
                
            finally:
                await stagehand.close()
    
    async def test_frame_id_persistence_across_navigation(self):
        """Test that frame IDs are updated when navigating to new pages."""
        with patch('stagehand.main.httpx.AsyncClient') as MockClient:
            mock_client = AsyncMock()
            MockClient.return_value = mock_client
            
            # Setup basic mocks
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "data": {
                    "sessionId": "test-session-nav",
                    "available": True
                }
            }
            mock_client.post = AsyncMock(return_value=mock_response)
            
            stagehand = Stagehand(
                env="BROWSERBASE",
                use_api=True,
                browserbase_api_key="test-api-key",
                browserbase_project_id="test-project",
                model_api_key="test-model-key"
            )
            
            try:
                await stagehand.init()
                
                page = stagehand.page
                context = stagehand.context
                
                # Initial frame ID
                initial_frame_id = "frame-initial"
                page.update_root_frame_id(initial_frame_id)
                context.register_frame_id(initial_frame_id, page)
                
                assert page.frame_id == initial_frame_id
                assert initial_frame_id in context.frame_id_map
                
                # Simulate navigation causing frame ID change
                # (In real scenario, CDP listener would handle this)
                new_frame_id = "frame-after-nav"
                context.unregister_frame_id(initial_frame_id)
                page.update_root_frame_id(new_frame_id)
                context.register_frame_id(new_frame_id, page)
                
                # Verify frame ID was updated
                assert page.frame_id == new_frame_id
                assert initial_frame_id not in context.frame_id_map
                assert new_frame_id in context.frame_id_map
                assert context.get_stagehand_page_by_frame_id(new_frame_id) == page
                
            finally:
                await stagehand.close()