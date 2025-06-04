"""Test StagehandPage wrapper functionality and AI primitives"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from stagehand.page import StagehandPage
from stagehand.schemas import (
    ActOptions,
    ActResult,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
    DEFAULT_EXTRACT_SCHEMA
)
from tests.mocks.mock_browser import MockPlaywrightPage, setup_page_with_content
from tests.mocks.mock_llm import MockLLMClient


class TestStagehandPageInitialization:
    """Test StagehandPage initialization and setup"""
    
    def test_page_initialization(self, mock_playwright_page):
        """Test basic page initialization"""
        mock_client = MagicMock()
        mock_client.env = "LOCAL"
        mock_client.logger = MagicMock()
        
        page = StagehandPage(mock_playwright_page, mock_client)
        
        assert page._page == mock_playwright_page
        assert page._stagehand == mock_client
        assert isinstance(page._page, MockPlaywrightPage)
    
    def test_page_attribute_forwarding(self, mock_playwright_page):
        """Test that page attributes are forwarded to underlying Playwright page"""
        mock_client = MagicMock()
        mock_client.env = "LOCAL"
        mock_client.logger = MagicMock()
        
        page = StagehandPage(mock_playwright_page, mock_client)
        
        # Should forward attribute access to underlying page
        assert page.url == mock_playwright_page.url
        
        # Should forward method calls
        page.keyboard.press("Enter")
        mock_playwright_page.keyboard.press.assert_called_with("Enter")


class TestDOMScriptInjection:
    """Test DOM script injection functionality"""
    
    @pytest.mark.asyncio
    async def test_ensure_injection_when_scripts_missing(self, mock_stagehand_page):
        """Test script injection when DOM functions are missing"""
        # Mock that functions don't exist
        mock_stagehand_page._page.evaluate.return_value = False
        
        # Mock DOM scripts reading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "window.testFunction = function() {};"
            
            await mock_stagehand_page.ensure_injection()
        
        # Should evaluate to check if functions exist
        mock_stagehand_page._page.evaluate.assert_called()
        
        # Should add init script
        mock_stagehand_page._page.add_init_script.assert_called()
    
    @pytest.mark.asyncio
    async def test_ensure_injection_when_scripts_exist(self, mock_stagehand_page):
        """Test that injection is skipped when scripts already exist"""
        # Mock that functions already exist
        mock_stagehand_page._page.evaluate.return_value = True
        
        await mock_stagehand_page.ensure_injection()
        
        # Should not add init script if functions already exist
        mock_stagehand_page._page.add_init_script.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_injection_script_loading_error(self, mock_stagehand_page):
        """Test graceful handling of script loading errors"""
        mock_stagehand_page._page.evaluate.return_value = False
        
        # Mock file reading error
        with patch('builtins.open', side_effect=FileNotFoundError("Script file not found")):
            await mock_stagehand_page.ensure_injection()
        
        # Should log error but not raise exception
        mock_stagehand_page._stagehand.logger.error.assert_called()


class TestPageNavigation:
    """Test page navigation functionality"""
    
    @pytest.mark.asyncio
    async def test_goto_local_mode(self, mock_stagehand_page):
        """Test navigation in LOCAL mode"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        await mock_stagehand_page.goto("https://example.com")
        
        # Should call Playwright's goto directly
        mock_stagehand_page._page.goto.assert_called_with(
            "https://example.com",
            referer=None,
            timeout=None,
            wait_until=None
        )
    
    @pytest.mark.asyncio
    async def test_goto_browserbase_mode(self, mock_stagehand_page):
        """Test navigation in BROWSERBASE mode"""
        mock_stagehand_page._stagehand.env = "BROWSERBASE"
        mock_stagehand_page._stagehand._execute = AsyncMock(return_value={"success": True})
        
        lock = AsyncMock()
        mock_stagehand_page._stagehand._get_lock_for_session.return_value = lock
        
        await mock_stagehand_page.goto("https://example.com")
        
        # Should call server execute method
        mock_stagehand_page._stagehand._execute.assert_called_with(
            "navigate",
            {"url": "https://example.com"}
        )
    
    @pytest.mark.asyncio
    async def test_goto_with_options(self, mock_stagehand_page):
        """Test navigation with additional options"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        await mock_stagehand_page.goto(
            "https://example.com",
            referer="https://google.com",
            timeout=30000,
            wait_until="networkidle"
        )
        
        mock_stagehand_page._page.goto.assert_called_with(
            "https://example.com",
            referer="https://google.com",
            timeout=30000,
            wait_until="networkidle"
        )


class TestActFunctionality:
    """Test the act() method for AI-powered actions"""
    
    @pytest.mark.asyncio
    async def test_act_with_string_instruction_local(self, mock_stagehand_page):
        """Test act() with string instruction in LOCAL mode"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        # Mock the act handler
        mock_act_handler = MagicMock()
        mock_act_handler.act = AsyncMock(return_value=ActResult(
            success=True,
            message="Button clicked successfully",
            action="click on submit button"
        ))
        mock_stagehand_page._act_handler = mock_act_handler
        
        result = await mock_stagehand_page.act("click on the submit button")
        
        assert isinstance(result, ActResult)
        assert result.success is True
        assert "clicked" in result.message
        mock_act_handler.act.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_act_with_observe_result(self, mock_stagehand_page):
        """Test act() with pre-observed ObserveResult"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        observe_result = ObserveResult(
            selector="#submit-btn",
            description="Submit button",
            method="click",
            arguments=[]
        )
        
        # Mock the act handler
        mock_act_handler = MagicMock()
        mock_act_handler.act = AsyncMock(return_value=ActResult(
            success=True,
            message="Action executed",
            action="click"
        ))
        mock_stagehand_page._act_handler = mock_act_handler
        
        result = await mock_stagehand_page.act(observe_result)
        
        assert isinstance(result, ActResult)
        mock_act_handler.act.assert_called_once()
        
        # Should pass the serialized observe result
        call_args = mock_act_handler.act.call_args[0][0]
        assert call_args["selector"] == "#submit-btn"
        assert call_args["method"] == "click"
    
    @pytest.mark.asyncio
    async def test_act_with_options_browserbase(self, mock_stagehand_page):
        """Test act() with additional options in BROWSERBASE mode"""
        mock_stagehand_page._stagehand.env = "BROWSERBASE"
        mock_stagehand_page._stagehand._execute = AsyncMock(return_value={
            "success": True,
            "message": "Action completed",
            "action": "click button"
        })
        
        lock = AsyncMock()
        mock_stagehand_page._stagehand._get_lock_for_session.return_value = lock
        
        result = await mock_stagehand_page.act(
            "click button",
            model_name="gpt-4o",
            timeout_ms=10000
        )
        
        # Should call server execute
        mock_stagehand_page._stagehand._execute.assert_called_with(
            "act",
            {
                "action": "click button",
                "modelName": "gpt-4o",
                "timeoutMs": 10000
            }
        )
        assert isinstance(result, ActResult)
    
    @pytest.mark.asyncio
    async def test_act_ignores_kwargs_with_observe_result(self, mock_stagehand_page):
        """Test that kwargs are ignored when using ObserveResult"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        observe_result = ObserveResult(
            selector="#test",
            description="test",
            method="click"
        )
        
        mock_act_handler = MagicMock()
        mock_act_handler.act = AsyncMock(return_value=ActResult(
            success=True,
            message="Done",
            action="click"
        ))
        mock_stagehand_page._act_handler = mock_act_handler
        
        # Should warn about ignored kwargs
        await mock_stagehand_page.act(observe_result, model_name="ignored")
        
        mock_stagehand_page._stagehand.logger.warning.assert_called()


class TestObserveFunctionality:
    """Test the observe() method for AI-powered element observation"""
    
    @pytest.mark.asyncio
    async def test_observe_with_string_instruction_local(self, mock_stagehand_page):
        """Test observe() with string instruction in LOCAL mode"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        # Mock the observe handler
        mock_observe_handler = MagicMock()
        mock_observe_handler.observe = AsyncMock(return_value=[
            ObserveResult(
                selector="#submit-btn",
                description="Submit button",
                backend_node_id=123,
                method="click",
                arguments=[]
            )
        ])
        mock_stagehand_page._observe_handler = mock_observe_handler
        
        result = await mock_stagehand_page.observe("find the submit button")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ObserveResult)
        assert result[0].selector == "#submit-btn"
        mock_observe_handler.observe.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_observe_with_options_object(self, mock_stagehand_page):
        """Test observe() with ObserveOptions object"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        options = ObserveOptions(
            instruction="find buttons",
            only_visible=True,
            return_action=True
        )
        
        mock_observe_handler = MagicMock()
        mock_observe_handler.observe = AsyncMock(return_value=[])
        mock_stagehand_page._observe_handler = mock_observe_handler
        
        result = await mock_stagehand_page.observe(options)
        
        assert isinstance(result, list)
        mock_observe_handler.observe.assert_called_with(options, from_act=False)
    
    @pytest.mark.asyncio
    async def test_observe_browserbase_mode(self, mock_stagehand_page):
        """Test observe() in BROWSERBASE mode"""
        mock_stagehand_page._stagehand.env = "BROWSERBASE"
        mock_stagehand_page._stagehand._execute = AsyncMock(return_value=[
            {
                "selector": "#test-btn",
                "description": "Test button",
                "backend_node_id": 456
            }
        ])
        
        lock = AsyncMock()
        mock_stagehand_page._stagehand._get_lock_for_session.return_value = lock
        
        result = await mock_stagehand_page.observe("find test button")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ObserveResult)
        assert result[0].selector == "#test-btn"
    
    @pytest.mark.asyncio
    async def test_observe_with_none_options(self, mock_stagehand_page):
        """Test observe() with None options"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        mock_observe_handler = MagicMock()
        mock_observe_handler.observe = AsyncMock(return_value=[])
        mock_stagehand_page._observe_handler = mock_observe_handler
        
        result = await mock_stagehand_page.observe(None)
        
        assert isinstance(result, list)
        # Should create empty ObserveOptions
        call_args = mock_observe_handler.observe.call_args[0][0]
        assert isinstance(call_args, ObserveOptions)


class TestExtractFunctionality:
    """Test the extract() method for AI-powered data extraction"""
    
    @pytest.mark.asyncio
    async def test_extract_with_string_instruction_local(self, mock_stagehand_page):
        """Test extract() with string instruction in LOCAL mode"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        # Mock the extract handler
        mock_extract_handler = MagicMock()
        mock_extract_result = MagicMock()
        mock_extract_result.data = {"title": "Sample Title", "description": "Sample description"}
        mock_extract_handler.extract = AsyncMock(return_value=mock_extract_result)
        mock_stagehand_page._extract_handler = mock_extract_handler
        
        result = await mock_stagehand_page.extract("extract the page title")
        
        assert result == {"title": "Sample Title", "description": "Sample description"}
        mock_extract_handler.extract.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_with_pydantic_schema(self, mock_stagehand_page):
        """Test extract() with Pydantic model schema"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        class ProductSchema(BaseModel):
            name: str
            price: float
            description: str = None
        
        options = ExtractOptions(
            instruction="extract product info",
            schema_definition=ProductSchema
        )
        
        mock_extract_handler = MagicMock()
        mock_extract_result = MagicMock()
        mock_extract_result.data = {"name": "Product", "price": 99.99}
        mock_extract_handler.extract = AsyncMock(return_value=mock_extract_result)
        mock_stagehand_page._extract_handler = mock_extract_handler
        
        result = await mock_stagehand_page.extract(options)
        
        assert result == {"name": "Product", "price": 99.99}
        
        # Should pass the Pydantic model to handler
        call_args = mock_extract_handler.extract.call_args
        assert call_args[1] == ProductSchema  # schema_to_pass_to_handler
    
    @pytest.mark.asyncio
    async def test_extract_with_dict_schema(self, mock_stagehand_page):
        """Test extract() with dictionary schema"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"}
            }
        }
        
        options = ExtractOptions(
            instruction="extract content",
            schema_definition=schema
        )
        
        mock_extract_handler = MagicMock()
        mock_extract_result = MagicMock()
        mock_extract_result.data = {"title": "Test", "content": "Test content"}
        mock_extract_handler.extract = AsyncMock(return_value=mock_extract_result)
        mock_stagehand_page._extract_handler = mock_extract_handler
        
        result = await mock_stagehand_page.extract(options)
        
        assert result == {"title": "Test", "content": "Test content"}
    
    @pytest.mark.asyncio
    async def test_extract_with_none_options(self, mock_stagehand_page):
        """Test extract() with None options (extract entire page)"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        mock_extract_handler = MagicMock()
        mock_extract_result = MagicMock()
        mock_extract_result.data = {"extraction": "Full page content"}
        mock_extract_handler.extract = AsyncMock(return_value=mock_extract_result)
        mock_stagehand_page._extract_handler = mock_extract_handler
        
        result = await mock_stagehand_page.extract(None)
        
        assert result == {"extraction": "Full page content"}
        
        # Should call extract with None for both parameters
        mock_extract_handler.extract.assert_called_with(None, None)
    
    @pytest.mark.asyncio
    async def test_extract_browserbase_mode(self, mock_stagehand_page):
        """Test extract() in BROWSERBASE mode"""
        mock_stagehand_page._stagehand.env = "BROWSERBASE"
        mock_stagehand_page._stagehand._execute = AsyncMock(return_value={
            "title": "Extracted Title",
            "price": "$99.99"
        })
        
        lock = AsyncMock()
        mock_stagehand_page._stagehand._get_lock_for_session.return_value = lock
        
        result = await mock_stagehand_page.extract("extract product info")
        
        assert isinstance(result, ExtractResult)
        assert result.title == "Extracted Title"
        assert result.price == "$99.99"


class TestScreenshotFunctionality:
    """Test screenshot functionality"""
    
    @pytest.mark.asyncio
    async def test_screenshot_local_mode_not_implemented(self, mock_stagehand_page):
        """Test that screenshot in LOCAL mode shows warning"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        result = await mock_stagehand_page.screenshot()
        
        assert result is None
        mock_stagehand_page._stagehand.logger.warning.assert_called()
    
    @pytest.mark.asyncio
    async def test_screenshot_browserbase_mode(self, mock_stagehand_page):
        """Test screenshot in BROWSERBASE mode"""
        mock_stagehand_page._stagehand.env = "BROWSERBASE"
        mock_stagehand_page._stagehand._execute = AsyncMock(return_value="base64_screenshot_data")
        
        lock = AsyncMock()
        mock_stagehand_page._stagehand._get_lock_for_session.return_value = lock
        
        result = await mock_stagehand_page.screenshot({"fullPage": True})
        
        assert result == "base64_screenshot_data"
        mock_stagehand_page._stagehand._execute.assert_called_with(
            "screenshot",
            {"fullPage": True}
        )


class TestCDPFunctionality:
    """Test Chrome DevTools Protocol functionality"""
    
    @pytest.mark.asyncio
    async def test_get_cdp_client_creation(self, mock_stagehand_page):
        """Test CDP client creation"""
        mock_cdp_session = MagicMock()
        mock_stagehand_page._page.context.new_cdp_session = AsyncMock(return_value=mock_cdp_session)
        
        client = await mock_stagehand_page.get_cdp_client()
        
        assert client == mock_cdp_session
        assert mock_stagehand_page._cdp_client == mock_cdp_session
        mock_stagehand_page._page.context.new_cdp_session.assert_called_with(mock_stagehand_page._page)
    
    @pytest.mark.asyncio
    async def test_get_cdp_client_reuse_existing(self, mock_stagehand_page):
        """Test that existing CDP client is reused"""
        existing_client = MagicMock()
        mock_stagehand_page._cdp_client = existing_client
        
        client = await mock_stagehand_page.get_cdp_client()
        
        assert client == existing_client
        # Should not create new session
        mock_stagehand_page._page.context.new_cdp_session.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_cdp_command(self, mock_stagehand_page):
        """Test sending CDP commands"""
        mock_cdp_session = MagicMock()
        mock_cdp_session.send = AsyncMock(return_value={"success": True})
        mock_stagehand_page._cdp_client = mock_cdp_session
        
        result = await mock_stagehand_page.send_cdp("Runtime.enable", {"param": "value"})
        
        assert result == {"success": True}
        mock_cdp_session.send.assert_called_with("Runtime.enable", {"param": "value"})
    
    @pytest.mark.asyncio
    async def test_send_cdp_with_session_recovery(self, mock_stagehand_page):
        """Test CDP command with session recovery after failure"""
        # First call fails with session closed error
        mock_cdp_session = MagicMock()
        mock_cdp_session.send = AsyncMock(side_effect=Exception("Session closed"))
        mock_stagehand_page._cdp_client = mock_cdp_session
        
        # New session for recovery
        new_cdp_session = MagicMock()
        new_cdp_session.send = AsyncMock(return_value={"success": True})
        mock_stagehand_page._page.context.new_cdp_session = AsyncMock(return_value=new_cdp_session)
        
        result = await mock_stagehand_page.send_cdp("Runtime.enable")
        
        assert result == {"success": True}
        # Should have created new session and retried
        assert mock_stagehand_page._cdp_client == new_cdp_session
    
    @pytest.mark.asyncio
    async def test_enable_cdp_domain(self, mock_stagehand_page):
        """Test enabling CDP domain"""
        mock_stagehand_page.send_cdp = AsyncMock(return_value={"success": True})
        
        await mock_stagehand_page.enable_cdp_domain("Runtime")
        
        mock_stagehand_page.send_cdp.assert_called_with("Runtime.enable")
    
    @pytest.mark.asyncio
    async def test_detach_cdp_client(self, mock_stagehand_page):
        """Test detaching CDP client"""
        mock_cdp_session = MagicMock()
        mock_cdp_session.is_connected.return_value = True
        mock_cdp_session.detach = AsyncMock()
        mock_stagehand_page._cdp_client = mock_cdp_session
        
        await mock_stagehand_page.detach_cdp_client()
        
        mock_cdp_session.detach.assert_called_once()
        assert mock_stagehand_page._cdp_client is None


class TestDOMSettling:
    """Test DOM settling functionality"""
    
    @pytest.mark.asyncio
    async def test_wait_for_settled_dom_default_timeout(self, mock_stagehand_page):
        """Test DOM settling with default timeout"""
        mock_stagehand_page._stagehand.dom_settle_timeout_ms = 5000
        
        await mock_stagehand_page._wait_for_settled_dom()
        
        # Should wait for domcontentloaded
        mock_stagehand_page._page.wait_for_load_state.assert_called_with("domcontentloaded")
        
        # Should evaluate DOM settle script
        mock_stagehand_page._page.evaluate.assert_called()
    
    @pytest.mark.asyncio
    async def test_wait_for_settled_dom_custom_timeout(self, mock_stagehand_page):
        """Test DOM settling with custom timeout"""
        await mock_stagehand_page._wait_for_settled_dom(timeout_ms=10000)
        
        # Should still work with custom timeout
        mock_stagehand_page._page.wait_for_load_state.assert_called()
    
    @pytest.mark.asyncio
    async def test_wait_for_settled_dom_error_handling(self, mock_stagehand_page):
        """Test DOM settling error handling"""
        mock_stagehand_page._page.evaluate.side_effect = Exception("Evaluation failed")
        
        # Should not raise exception
        await mock_stagehand_page._wait_for_settled_dom()
        
        mock_stagehand_page._stagehand.logger.warning.assert_called()


class TestPageIntegration:
    """Test integration between different page methods"""
    
    @pytest.mark.asyncio
    async def test_observe_then_act_workflow(self, mock_stagehand_page):
        """Test complete observe -> act workflow"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        # Setup observe handler
        observe_result = ObserveResult(
            selector="#submit-btn",
            description="Submit button",
            method="click",
            arguments=[]
        )
        mock_observe_handler = MagicMock()
        mock_observe_handler.observe = AsyncMock(return_value=[observe_result])
        mock_stagehand_page._observe_handler = mock_observe_handler
        
        # Setup act handler
        mock_act_handler = MagicMock()
        mock_act_handler.act = AsyncMock(return_value=ActResult(
            success=True,
            message="Clicked successfully",
            action="click"
        ))
        mock_stagehand_page._act_handler = mock_act_handler
        
        # Execute workflow
        observed = await mock_stagehand_page.observe("find submit button")
        act_result = await mock_stagehand_page.act(observed[0])
        
        assert len(observed) == 1
        assert observed[0].selector == "#submit-btn"
        assert act_result.success is True
    
    @pytest.mark.asyncio
    async def test_navigation_then_extraction_workflow(self, mock_stagehand_page, sample_html_content):
        """Test navigate -> extract workflow"""
        mock_stagehand_page._stagehand.env = "LOCAL"
        
        # Setup page content
        setup_page_with_content(mock_stagehand_page._page, sample_html_content)
        
        # Setup extract handler
        mock_extract_handler = MagicMock()
        mock_extract_result = MagicMock()
        mock_extract_result.data = {"title": "Test Page"}
        mock_extract_handler.extract = AsyncMock(return_value=mock_extract_result)
        mock_stagehand_page._extract_handler = mock_extract_handler
        
        # Execute workflow
        await mock_stagehand_page.goto("https://example.com")
        result = await mock_stagehand_page.extract("extract the page title")
        
        assert result == {"title": "Test Page"}
        mock_stagehand_page._page.goto.assert_called()
        mock_extract_handler.extract.assert_called() 