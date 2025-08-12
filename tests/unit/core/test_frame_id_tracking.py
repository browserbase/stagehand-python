"""
Unit tests for frame ID tracking functionality.
Tests the implementation of frame ID map in StagehandContext and StagehandPage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from stagehand.context import StagehandContext
from stagehand.page import StagehandPage


@pytest.fixture
def mock_stagehand():
    """Create a mock Stagehand client."""
    mock = MagicMock()
    mock.logger = MagicMock()
    mock.logger.debug = MagicMock()
    mock.logger.error = MagicMock()
    mock._page_switch_lock = AsyncMock()
    return mock


@pytest.fixture
def mock_browser_context():
    """Create a mock Playwright BrowserContext."""
    mock_context = MagicMock()
    mock_context.pages = []
    mock_context.new_page = AsyncMock()
    mock_context.new_cdp_session = AsyncMock()
    return mock_context


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page."""
    page = MagicMock()
    page.url = "https://example.com"
    page.evaluate = AsyncMock(return_value=False)
    page.add_init_script = AsyncMock()
    page.context = MagicMock()
    page.once = MagicMock()
    return page


class TestFrameIdTracking:
    """Test suite for frame ID tracking functionality."""
    
    def test_stagehand_context_initialization(self, mock_browser_context, mock_stagehand):
        """Test that StagehandContext initializes with frame_id_map."""
        context = StagehandContext(mock_browser_context, mock_stagehand)
        
        assert hasattr(context, 'frame_id_map')
        assert isinstance(context.frame_id_map, dict)
        assert len(context.frame_id_map) == 0
    
    def test_register_frame_id(self, mock_browser_context, mock_stagehand, mock_page):
        """Test registering a frame ID."""
        context = StagehandContext(mock_browser_context, mock_stagehand)
        stagehand_page = StagehandPage(mock_page, mock_stagehand, context)
        
        # Register frame ID
        frame_id = "frame-123"
        context.register_frame_id(frame_id, stagehand_page)
        
        assert frame_id in context.frame_id_map
        assert context.frame_id_map[frame_id] == stagehand_page
    
    def test_unregister_frame_id(self, mock_browser_context, mock_stagehand, mock_page):
        """Test unregistering a frame ID."""
        context = StagehandContext(mock_browser_context, mock_stagehand)
        stagehand_page = StagehandPage(mock_page, mock_stagehand, context)
        
        # Register and then unregister
        frame_id = "frame-456"
        context.register_frame_id(frame_id, stagehand_page)
        context.unregister_frame_id(frame_id)
        
        assert frame_id not in context.frame_id_map
    
    def test_get_stagehand_page_by_frame_id(self, mock_browser_context, mock_stagehand, mock_page):
        """Test retrieving a StagehandPage by frame ID."""
        context = StagehandContext(mock_browser_context, mock_stagehand)
        stagehand_page = StagehandPage(mock_page, mock_stagehand, context)
        
        frame_id = "frame-789"
        context.register_frame_id(frame_id, stagehand_page)
        
        retrieved_page = context.get_stagehand_page_by_frame_id(frame_id)
        assert retrieved_page == stagehand_page
        
        # Test non-existent frame ID
        non_existent = context.get_stagehand_page_by_frame_id("non-existent")
        assert non_existent is None
    
    def test_stagehand_page_frame_id_property(self, mock_page, mock_stagehand):
        """Test StagehandPage frame_id property and update method."""
        stagehand_page = StagehandPage(mock_page, mock_stagehand)
        
        # Initially None
        assert stagehand_page.frame_id is None
        
        # Update frame ID
        new_frame_id = "frame-abc"
        stagehand_page.update_root_frame_id(new_frame_id)
        
        assert stagehand_page.frame_id == new_frame_id
        mock_stagehand.logger.debug.assert_called_with(
            f"Updated frame ID to {new_frame_id}", category="page"
        )
    
    @pytest.mark.asyncio
    async def test_attach_frame_navigated_listener(self, mock_browser_context, mock_stagehand, mock_page):
        """Test attaching CDP frame navigation listener."""
        context = StagehandContext(mock_browser_context, mock_stagehand)
        stagehand_page = StagehandPage(mock_page, mock_stagehand, context)
        
        # Mock CDP session
        mock_cdp_session = MagicMock()
        mock_cdp_session.send = AsyncMock()
        mock_cdp_session.on = MagicMock()
        mock_browser_context.new_cdp_session = AsyncMock(return_value=mock_cdp_session)
        
        # Mock frame tree response
        mock_cdp_session.send.return_value = {
            "frameTree": {
                "frame": {
                    "id": "initial-frame-id"
                }
            }
        }
        
        # Attach listener
        await context._attach_frame_navigated_listener(mock_page, stagehand_page)
        
        # Verify CDP session was created and Page domain was enabled
        mock_browser_context.new_cdp_session.assert_called_once_with(mock_page)
        mock_cdp_session.send.assert_any_call("Page.enable")
        mock_cdp_session.send.assert_any_call("Page.getFrameTree")
        
        # Verify frame ID was set
        assert stagehand_page.frame_id == "initial-frame-id"
        assert "initial-frame-id" in context.frame_id_map
        
        # Verify event listener was registered
        mock_cdp_session.on.assert_called_once()
        assert mock_cdp_session.on.call_args[0][0] == "Page.frameNavigated"
    
    @pytest.mark.asyncio
    async def test_frame_id_in_api_calls(self, mock_page, mock_stagehand):
        """Test that frame ID is included in API payloads."""
        stagehand_page = StagehandPage(mock_page, mock_stagehand)
        stagehand_page.update_root_frame_id("test-frame-123")
        
        # Mock the stagehand client for API mode
        mock_stagehand.use_api = True
        mock_stagehand._get_lock_for_session = MagicMock()
        mock_stagehand._get_lock_for_session.return_value = AsyncMock()
        mock_stagehand._execute = AsyncMock(return_value={"success": True})
        
        # Test goto with frame ID
        await stagehand_page.goto("https://example.com")
        
        # Verify frame ID was included in the payload
        call_args = mock_stagehand._execute.call_args
        assert call_args[0][0] == "navigate"
        assert "frameId" in call_args[0][1]
        assert call_args[0][1]["frameId"] == "test-frame-123"
    
    @pytest.mark.asyncio
    async def test_frame_navigation_event_handling(self, mock_browser_context, mock_stagehand, mock_page):
        """Test handling of frame navigation events."""
        context = StagehandContext(mock_browser_context, mock_stagehand)
        stagehand_page = StagehandPage(mock_page, mock_stagehand, context)
        
        # Set initial frame ID
        initial_frame_id = "frame-initial"
        stagehand_page.update_root_frame_id(initial_frame_id)
        context.register_frame_id(initial_frame_id, stagehand_page)
        
        # Mock CDP session
        mock_cdp_session = MagicMock()
        mock_cdp_session.send = AsyncMock()
        mock_cdp_session.on = MagicMock()
        mock_browser_context.new_cdp_session = AsyncMock(return_value=mock_cdp_session)
        
        # Mock initial frame tree
        mock_cdp_session.send.return_value = {
            "frameTree": {
                "frame": {
                    "id": initial_frame_id
                }
            }
        }
        
        await context._attach_frame_navigated_listener(mock_page, stagehand_page)
        
        # Get the registered event handler
        event_handler = mock_cdp_session.on.call_args[0][1]
        
        # Simulate frame navigation event
        new_frame_id = "frame-new"
        event_handler({
            "frame": {
                "id": new_frame_id,
                "parentId": None  # Root frame has no parent
            }
        })
        
        # Verify old frame ID was unregistered and new one registered
        assert initial_frame_id not in context.frame_id_map
        assert new_frame_id in context.frame_id_map
        assert stagehand_page.frame_id == new_frame_id
        assert context.frame_id_map[new_frame_id] == stagehand_page