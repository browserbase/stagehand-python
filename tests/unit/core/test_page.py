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
        # The fixture creates a MagicMock, not a MockPlaywrightPage
        assert hasattr(page._page, 'evaluate')  # Check for expected method instead
    
    def test_page_attribute_forwarding(self, mock_playwright_page):
        """Test that page attributes are forwarded to underlying Playwright page"""
        mock_client = MagicMock()
        mock_client.env = "LOCAL"
        mock_client.logger = MagicMock()
        
        # Ensure keyboard is a regular MagicMock, not AsyncMock
        mock_playwright_page.keyboard = MagicMock()
        mock_playwright_page.keyboard.press = MagicMock(return_value=None)
        
        page = StagehandPage(mock_playwright_page, mock_client)
        
        # Should forward attribute access to underlying page
        assert page.url == mock_playwright_page.url
        
        # Should forward method calls
        page.keyboard.press("Enter")
        mock_playwright_page.keyboard.press.assert_called_with("Enter")


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
