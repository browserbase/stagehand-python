"""Mock browser implementations for testing without real browser instances"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock


class MockPlaywrightPage:
    """Mock Playwright page for testing"""
    
    def __init__(self, url: str = "https://example.com", content: str = "<html><body>Test</body></html>"):
        self.url = url
        self._content = content
        self._title = "Test Page"
        
        # Mock async methods
        self.goto = AsyncMock()
        self.evaluate = AsyncMock(return_value=True)
        self.wait_for_load_state = AsyncMock()
        self.wait_for_selector = AsyncMock()
        self.add_init_script = AsyncMock()
        self.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
        self.content = AsyncMock(return_value=self._content)
        self.title = AsyncMock(return_value=self._title)
        self.reload = AsyncMock()
        self.close = AsyncMock()
        
        # Mock input methods
        self.click = AsyncMock()
        self.fill = AsyncMock()
        self.type = AsyncMock()
        self.press = AsyncMock()
        self.select_option = AsyncMock()
        self.check = AsyncMock()
        self.uncheck = AsyncMock()
        
        # Mock query methods
        self.query_selector = AsyncMock()
        self.query_selector_all = AsyncMock(return_value=[])
        self.is_visible = AsyncMock(return_value=True)
        self.is_enabled = AsyncMock(return_value=True)
        self.is_checked = AsyncMock(return_value=False)
        
        # Mock keyboard and mouse
        self.keyboard = MagicMock()
        self.keyboard.press = AsyncMock()
        self.keyboard.type = AsyncMock()
        self.mouse = MagicMock()
        self.mouse.click = AsyncMock()
        self.mouse.move = AsyncMock()
        
        # Mock context
        self.context = MagicMock()
        self.context.new_cdp_session = AsyncMock(return_value=MockCDPSession())
        
        # State tracking
        self.navigation_history = [url]
        self.script_injections = []
        self.evaluation_results = {}
        
    async def goto(self, url: str, **kwargs):
        """Mock navigation"""
        self.url = url
        self.navigation_history.append(url)
        return MagicMock(status=200, ok=True)
    
    async def evaluate(self, script: str, *args):
        """Mock script evaluation"""
        # Store the script for test verification
        self.script_injections.append(script)
        
        # Return different results based on script content
        if "getScrollableElementXpaths" in script:
            return ["//body", "//div[@class='content']"]
        elif "getElementInfo" in script:
            return {
                "selector": args[0] if args else "#test",
                "visible": True,
                "bounds": {"x": 0, "y": 0, "width": 100, "height": 50}
            }
        elif "typeof window." in script:
            # For checking if functions exist
            return True
        else:
            return self.evaluation_results.get(script, True)
    
    async def add_init_script(self, script: str):
        """Mock init script addition"""
        self.script_injections.append(f"INIT: {script}")
    
    def set_content(self, content: str):
        """Set mock page content"""
        self._content = content
        self.content = AsyncMock(return_value=content)
    
    def set_title(self, title: str):
        """Set mock page title"""
        self._title = title
        self.title = AsyncMock(return_value=title)
    
    def set_evaluation_result(self, script: str, result: Any):
        """Set custom evaluation result for specific script"""
        self.evaluation_results[script] = result


class MockCDPSession:
    """Mock CDP session for testing"""
    
    def __init__(self):
        self.send = AsyncMock()
        self.detach = AsyncMock()
        self._connected = True
        self.events = []
    
    def is_connected(self) -> bool:
        """Check if CDP session is connected"""
        return self._connected
    
    async def send(self, method: str, params: Optional[Dict] = None):
        """Mock CDP command sending"""
        self.events.append({"method": method, "params": params or {}})
        
        # Return appropriate responses for common CDP methods
        if method == "Runtime.enable":
            return {"success": True}
        elif method == "DOM.enable":
            return {"success": True}
        elif method.endswith(".disable"):
            return {"success": True}
        else:
            return {"success": True, "result": {}}
    
    async def detach(self):
        """Mock CDP session detachment"""
        self._connected = False


class MockBrowserContext:
    """Mock browser context for testing"""
    
    def __init__(self):
        self.new_page = AsyncMock()
        self.close = AsyncMock()
        self.new_cdp_session = AsyncMock(return_value=MockCDPSession())
        
        # Context state
        self.pages = []
        self._closed = False
        
        # Set up new_page to return a MockPlaywrightPage
        self.new_page.return_value = MockPlaywrightPage()
    
    async def new_page(self) -> MockPlaywrightPage:
        """Create a new mock page"""
        page = MockPlaywrightPage()
        self.pages.append(page)
        return page
    
    async def close(self):
        """Close the mock context"""
        self._closed = True
        for page in self.pages:
            await page.close()


class MockBrowser:
    """Mock browser for testing"""
    
    def __init__(self):
        self.new_context = AsyncMock()
        self.close = AsyncMock()
        self.new_page = AsyncMock()
        
        # Browser state
        self.contexts = []
        self._closed = False
        self.version = "123.0.0"
        
        # Set up new_context to return a MockBrowserContext
        self.new_context.return_value = MockBrowserContext()
    
    async def new_context(self, **kwargs) -> MockBrowserContext:
        """Create a new mock context"""
        context = MockBrowserContext()
        self.contexts.append(context)
        return context
    
    async def new_page(self, **kwargs) -> MockPlaywrightPage:
        """Create a new mock page"""
        return MockPlaywrightPage()
    
    async def close(self):
        """Close the mock browser"""
        self._closed = True
        for context in self.contexts:
            await context.close()


class MockPlaywright:
    """Mock Playwright instance for testing"""
    
    def __init__(self):
        self.chromium = MagicMock()
        self.firefox = MagicMock()
        self.webkit = MagicMock()
        
        # Set up chromium methods
        self.chromium.launch = AsyncMock(return_value=MockBrowser())
        self.chromium.launch_persistent_context = AsyncMock(return_value=MockBrowserContext())
        self.chromium.connect_over_cdp = AsyncMock(return_value=MockBrowser())
        
        # Similar setup for other browsers
        self.firefox.launch = AsyncMock(return_value=MockBrowser())
        self.webkit.launch = AsyncMock(return_value=MockBrowser())
        
        self._started = False
    
    async def start(self):
        """Mock start method"""
        self._started = True
        return self
    
    async def stop(self):
        """Mock stop method"""
        self._started = False


class MockWebSocket:
    """Mock WebSocket for CDP connections"""
    
    def __init__(self):
        self.send = AsyncMock()
        self.recv = AsyncMock()
        self.close = AsyncMock()
        self.ping = AsyncMock()
        self.pong = AsyncMock()
        
        self._closed = False
        self.messages = []
    
    async def send(self, message: str):
        """Mock send message"""
        self.messages.append(("sent", message))
    
    async def recv(self) -> str:
        """Mock receive message"""
        # Return a default CDP response
        return '{"id": 1, "result": {}}'
    
    async def close(self):
        """Mock close connection"""
        self._closed = True
    
    @property
    def closed(self) -> bool:
        """Check if connection is closed"""
        return self._closed


# Utility functions for setting up browser mocks

def create_mock_browser_stack():
    """Create a complete mock browser stack for testing"""
    playwright = MockPlaywright()
    browser = MockBrowser()
    context = MockBrowserContext()
    page = MockPlaywrightPage()
    
    # Wire them together
    playwright.chromium.launch.return_value = browser
    browser.new_context.return_value = context
    context.new_page.return_value = page
    
    return playwright, browser, context, page


def setup_page_with_content(page: MockPlaywrightPage, html_content: str, url: str = "https://example.com"):
    """Set up a mock page with specific content"""
    page.set_content(html_content)
    page.url = url
    page.goto.return_value = MagicMock(status=200, ok=True)
    
    # Extract title from HTML if present
    if "<title>" in html_content:
        import re
        title_match = re.search(r"<title>(.*?)</title>", html_content)
        if title_match:
            page.set_title(title_match.group(1))
    
    return page 