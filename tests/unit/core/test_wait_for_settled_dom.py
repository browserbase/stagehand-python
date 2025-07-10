"""Test the CDP-based _wait_for_settled_dom implementation"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, call
from stagehand.page import StagehandPage


@pytest.mark.asyncio
async def test_wait_for_settled_dom_basic(mock_stagehand_client, mock_playwright_page):
    """Test basic functionality of _wait_for_settled_dom"""
    # Create a StagehandPage instance
    page = StagehandPage(mock_playwright_page, mock_stagehand_client)
    
    # Mock CDP client
    mock_cdp_client = MagicMock()
    mock_cdp_client.send = AsyncMock()
    mock_cdp_client.on = MagicMock()
    mock_cdp_client.remove_listener = MagicMock()
    
    # Mock get_cdp_client to return our mock
    page.get_cdp_client = AsyncMock(return_value=mock_cdp_client)
    
    # Mock page title to simulate document exists
    mock_playwright_page.title = AsyncMock(return_value="Test Page")
    
    # Create a task that will call _wait_for_settled_dom
    async def run_wait():
        await page._wait_for_settled_dom(timeout_ms=1000)
    
    # Start the wait task
    wait_task = asyncio.create_task(run_wait())
    
    # Give it a moment to set up event handlers
    await asyncio.sleep(0.1)
    
    # Verify CDP domains were enabled
    assert mock_cdp_client.send.call_count >= 3
    mock_cdp_client.send.assert_any_call("Network.enable")
    mock_cdp_client.send.assert_any_call("Page.enable")
    mock_cdp_client.send.assert_any_call("Target.setAutoAttach", {
        "autoAttach": True,
        "waitForDebuggerOnStart": False,
        "flatten": True,
        "filter": [
            {"type": "worker", "exclude": True},
            {"type": "shared_worker", "exclude": True},
        ],
    })
    
    # Verify event handlers were registered
    assert mock_cdp_client.on.call_count >= 6
    event_names = [call[0][0] for call in mock_cdp_client.on.call_args_list]
    assert "Network.requestWillBeSent" in event_names
    assert "Network.loadingFinished" in event_names
    assert "Network.loadingFailed" in event_names
    assert "Network.requestServedFromCache" in event_names
    assert "Network.responseReceived" in event_names
    assert "Page.frameStoppedLoading" in event_names
    
    # Cancel the task (it would timeout otherwise)
    wait_task.cancel()
    try:
        await wait_task
    except asyncio.CancelledError:
        pass
    
    # Verify event handlers were unregistered
    assert mock_cdp_client.remove_listener.call_count >= 6


@pytest.mark.asyncio
async def test_wait_for_settled_dom_with_requests(mock_stagehand_client, mock_playwright_page):
    """Test _wait_for_settled_dom with network requests"""
    # Create a StagehandPage instance
    page = StagehandPage(mock_playwright_page, mock_stagehand_client)
    
    # Mock CDP client
    mock_cdp_client = MagicMock()
    mock_cdp_client.send = AsyncMock()
    
    # Store event handlers
    event_handlers = {}
    
    def mock_on(event_name, handler):
        event_handlers[event_name] = handler
    
    def mock_remove_listener(event_name, handler):
        if event_name in event_handlers:
            del event_handlers[event_name]
    
    mock_cdp_client.on = mock_on
    mock_cdp_client.remove_listener = mock_remove_listener
    
    # Mock get_cdp_client to return our mock
    page.get_cdp_client = AsyncMock(return_value=mock_cdp_client)
    
    # Mock page title to simulate document exists
    mock_playwright_page.title = AsyncMock(return_value="Test Page")
    
    # Create a task that will call _wait_for_settled_dom
    async def run_wait():
        await page._wait_for_settled_dom(timeout_ms=5000)
    
    # Start the wait task
    wait_task = asyncio.create_task(run_wait())
    
    # Give it a moment to set up event handlers
    await asyncio.sleep(0.1)
    
    # Simulate a network request
    if "Network.requestWillBeSent" in event_handlers:
        event_handlers["Network.requestWillBeSent"]({
            "requestId": "req1",
            "type": "Document",
            "frameId": "frame1",
            "request": {"url": "https://example.com"}
        })
    
    # Give it a moment
    await asyncio.sleep(0.1)
    
    # The task should still be running (request in flight)
    assert not wait_task.done()
    
    # Finish the request
    if "Network.loadingFinished" in event_handlers:
        event_handlers["Network.loadingFinished"]({"requestId": "req1"})
    
    # Wait for the quiet period (0.5s) plus a bit
    await asyncio.sleep(0.6)
    
    # The task should now be complete
    assert wait_task.done()
    await wait_task  # Should complete without error


@pytest.mark.asyncio
async def test_wait_for_settled_dom_timeout(mock_stagehand_client, mock_playwright_page):
    """Test _wait_for_settled_dom timeout behavior"""
    # Create a StagehandPage instance
    page = StagehandPage(mock_playwright_page, mock_stagehand_client)
    
    # Mock CDP client
    mock_cdp_client = MagicMock()
    mock_cdp_client.send = AsyncMock()
    mock_cdp_client.on = MagicMock()
    mock_cdp_client.remove_listener = MagicMock()
    
    # Mock get_cdp_client to return our mock
    page.get_cdp_client = AsyncMock(return_value=mock_cdp_client)
    
    # Mock page title to simulate document exists
    mock_playwright_page.title = AsyncMock(return_value="Test Page")
    
    # Set a very short timeout
    mock_stagehand_client.dom_settle_timeout_ms = 100
    
    # Run wait with timeout
    await page._wait_for_settled_dom()
    
    # Should complete without error due to timeout
    assert True  # If we get here, the timeout worked


@pytest.mark.asyncio
async def test_wait_for_settled_dom_no_document(mock_stagehand_client, mock_playwright_page):
    """Test _wait_for_settled_dom when document doesn't exist initially"""
    # Create a StagehandPage instance
    page = StagehandPage(mock_playwright_page, mock_stagehand_client)
    
    # Mock CDP client
    mock_cdp_client = MagicMock()
    mock_cdp_client.send = AsyncMock()
    mock_cdp_client.on = MagicMock()
    mock_cdp_client.remove_listener = MagicMock()
    
    # Mock get_cdp_client to return our mock
    page.get_cdp_client = AsyncMock(return_value=mock_cdp_client)
    
    # Mock page title to throw exception (no document)
    mock_playwright_page.title = AsyncMock(side_effect=Exception("No document"))
    mock_playwright_page.wait_for_load_state = AsyncMock()
    
    # Set a short timeout
    mock_stagehand_client.dom_settle_timeout_ms = 500
    
    # Run wait
    await page._wait_for_settled_dom()
    
    # Should have waited for domcontentloaded
    mock_playwright_page.wait_for_load_state.assert_called_once_with("domcontentloaded") 