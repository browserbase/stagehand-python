"""Test the LivePageProxy functionality"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from stagehand.main import LivePageProxy, Stagehand
from stagehand.page import StagehandPage


@pytest.mark.asyncio
async def test_live_page_proxy_basic_delegation(mock_stagehand_config):
    """Test that LivePageProxy delegates to the active page"""
    # Create a Stagehand instance
    stagehand = Stagehand(config=mock_stagehand_config)
    
    # Mock page
    mock_page = MagicMock(spec=StagehandPage)
    mock_page.url = "https://active.com"
    mock_page.title = AsyncMock(return_value="Active Page")
    
    # Set up the page
    stagehand._page = mock_page
    stagehand._initialized = True
    
    # Get the proxy
    proxy = stagehand.page
    
    # Test that it delegates to the page
    assert proxy.url == "https://active.com"
    title = await proxy.title()
    assert title == "Active Page"


@pytest.mark.asyncio
async def test_live_page_proxy_no_page_fallback(mock_stagehand_config):
    """Test that LivePageProxy raises error when no page is set"""
    # Create a Stagehand instance
    stagehand = Stagehand(config=mock_stagehand_config)
    
    # No page set
    stagehand._page = None
    stagehand._initialized = True
    
    # Get the proxy
    proxy = stagehand.page
    
    # Accessing attributes should raise RuntimeError
    with pytest.raises(RuntimeError, match="No active page available"):
        _ = proxy.url


@pytest.mark.asyncio
async def test_live_page_proxy_page_stability(mock_stagehand_config):
    """Test that LivePageProxy waits for page stability on async operations"""
    # Create a Stagehand instance
    stagehand = Stagehand(config=mock_stagehand_config)
    
    # Track lock acquisition
    lock_acquired = False
    lock_released = False
    
    class TestLock:
        async def __aenter__(self):
            nonlocal lock_acquired
            lock_acquired = True
            await asyncio.sleep(0.1)  # Simulate some work
            return self
            
        async def __aexit__(self, *args):
            nonlocal lock_released
            lock_released = True
    
    stagehand._page_switch_lock = TestLock()
    
    # Mock page with async method
    mock_page = MagicMock(spec=StagehandPage)
    mock_page.click = AsyncMock(return_value=None)
    
    # Set up the page
    stagehand._page = mock_page
    stagehand._initialized = True
    
    # Get the proxy
    proxy = stagehand.page
    
    # Call an async method (should wait for stability)
    await proxy.click("button")
    
    # Verify lock was acquired and released
    assert lock_acquired
    assert lock_released
    mock_page.click.assert_called_once_with("button")


@pytest.mark.asyncio
async def test_live_page_proxy_navigation_no_stability_check(mock_stagehand_config):
    """Test that navigation methods don't wait for page stability"""
    # Create a Stagehand instance
    stagehand = Stagehand(config=mock_stagehand_config)
    
    # Track lock acquisition (should not happen)
    lock_acquired = False
    
    class TestLock:
        async def __aenter__(self):
            nonlocal lock_acquired
            lock_acquired = True
            return self
            
        async def __aexit__(self, *args):
            pass
    
    stagehand._page_switch_lock = TestLock()
    
    # Mock page with navigation methods
    mock_page = MagicMock(spec=StagehandPage)
    mock_page.goto = AsyncMock(return_value=None)
    mock_page.reload = AsyncMock(return_value=None)
    mock_page.go_back = AsyncMock(return_value=None)
    mock_page.go_forward = AsyncMock(return_value=None)
    
    # Set up the page
    stagehand._page = mock_page
    stagehand._initialized = True
    
    # Get the proxy
    proxy = stagehand.page
    
    # Call navigation methods (should NOT wait for stability)
    await proxy.goto("https://example.com")
    await proxy.reload()
    await proxy.go_back()
    await proxy.go_forward()
    
    # Verify lock was NOT acquired
    assert not lock_acquired
    
    # Verify methods were called
    mock_page.goto.assert_called_once_with("https://example.com")
    mock_page.reload.assert_called_once()
    mock_page.go_back.assert_called_once()
    mock_page.go_forward.assert_called_once()


@pytest.mark.asyncio
async def test_live_page_proxy_dynamic_page_switching(mock_stagehand_config):
    """Test that LivePageProxy dynamically switches between pages"""
    # Create a Stagehand instance
    stagehand = Stagehand(config=mock_stagehand_config)
    
    # Mock pages
    page1 = MagicMock(spec=StagehandPage)
    page1.url = "https://page1.com"
    
    page2 = MagicMock(spec=StagehandPage)
    page2.url = "https://page2.com"
    
    # Set up initial state
    stagehand._page = page1
    stagehand._initialized = True
    
    # Get the proxy
    proxy = stagehand.page
    
    # Initially points to page1
    assert proxy.url == "https://page1.com"
    
    # Switch page
    stagehand._page = page2
    
    # Now points to page2 without creating a new proxy
    assert proxy.url == "https://page2.com"


def test_live_page_proxy_no_page_error(mock_stagehand_config):
    """Test that LivePageProxy raises error when no page is available"""
    # Create a Stagehand instance
    stagehand = Stagehand(config=mock_stagehand_config)
    
    # No page set
    stagehand._page = None
    stagehand._initialized = True
    
    # Get the proxy
    proxy = stagehand.page
    
    # Accessing attributes should raise RuntimeError
    with pytest.raises(RuntimeError, match="No active page available"):
        _ = proxy.url


def test_live_page_proxy_not_initialized(mock_stagehand_config):
    """Test that page property returns None when not initialized"""
    # Create a Stagehand instance
    stagehand = Stagehand(config=mock_stagehand_config)
    stagehand._initialized = False
    
    # Should return None
    assert stagehand.page is None