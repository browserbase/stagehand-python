"""Test ActHandler functionality for AI-powered action execution"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from stagehand.handlers.act_handler import ActHandler
from stagehand.types import ActOptions, ActResult, ObserveResult
from tests.mocks.mock_llm import MockLLMClient, MockLLMResponse


class TestActHandlerInitialization:
    """Test ActHandler initialization and setup"""
    
    def test_act_handler_creation(self, mock_stagehand_page):
        """Test basic ActHandler creation"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(
            mock_stagehand_page,
            mock_client,
            user_provided_instructions="Test instructions",
            self_heal=True
        )
        
        assert handler.stagehand_page == mock_stagehand_page
        assert handler.stagehand == mock_client
        assert handler.user_provided_instructions == "Test instructions"
        assert handler.self_heal is True


class TestActExecution:
    """Test action execution functionality"""
    
    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_act_with_string_action(self, mock_stagehand_page):
        """Test executing action with string instruction"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock the observe handler to return a successful result
        mock_observe_result = ObserveResult(
            selector="xpath=//button[@id='submit-btn']",
            description="Submit button",
            method="click",
            arguments=[]
        )
        mock_stagehand_page._observe_handler = MagicMock()
        mock_stagehand_page._observe_handler.observe = AsyncMock(return_value=[mock_observe_result])
        
        # Mock the playwright method execution
        handler._perform_playwright_method = AsyncMock()
        
        result = await handler.act({"action": "click on the submit button"})
        
        assert isinstance(result, ActResult)
        assert result.success is True
        assert "performed successfully" in result.message
        assert result.action == "Submit button"
    

    