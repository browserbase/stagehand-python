"""Test ObserveHandler functionality for AI-powered element observation"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from stagehand.handlers.observe_handler import ObserveHandler
from stagehand.schemas import ObserveOptions, ObserveResult
from tests.mocks.mock_llm import MockLLMClient


def setup_observe_mocks(mock_stagehand_page):
    """Set up common mocks for observe handler tests"""
    mock_stagehand_page._wait_for_settled_dom = AsyncMock()
    mock_stagehand_page.send_cdp = AsyncMock()
    mock_stagehand_page.get_cdp_client = AsyncMock()
    
    # Mock the accessibility tree and xpath utilities
    with patch('stagehand.handlers.observe_handler.get_accessibility_tree') as mock_tree, \
         patch('stagehand.handlers.observe_handler.get_xpath_by_resolved_object_id') as mock_xpath:
        
        mock_tree.return_value = {"simplified": "mocked tree", "iframes": []}
        mock_xpath.return_value = "//button[@id='test']"
        
        return mock_tree, mock_xpath


class TestObserveHandlerInitialization:
    """Test ObserveHandler initialization"""
    
    def test_observe_handler_creation(self, mock_stagehand_page):
        """Test basic handler creation"""
        mock_client = MagicMock()
        mock_client.logger = MagicMock()
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        assert handler.stagehand_page == mock_stagehand_page
        assert handler.stagehand == mock_client
        assert handler.user_provided_instructions == ""


class TestObserveExecution:
    """Test observe execution and response processing"""
    
    @pytest.mark.smoke
    @pytest.mark.asyncio
    async def test_observe_single_element(self, mock_stagehand_page):
        """Test observing a single element"""
        # Set up mock client with proper LLM response
        mock_client = MagicMock()
        mock_client.logger = MagicMock()
        mock_client.logger.info = MagicMock()
        mock_client.logger.debug = MagicMock()
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
        # Create a MockLLMClient instance
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        # Set up the LLM to return the observe response in the format expected by observe_inference
        # The MockLLMClient should return this when the response_type is "observe"
        mock_llm.set_custom_response("observe", [
            {
                "element_id": 12345,
                "description": "Submit button in the form", 
                "method": "click",
                "arguments": []
            }
        ])
        
        # Mock the CDP and accessibility tree functions
        with patch('stagehand.handlers.observe_handler.get_accessibility_tree') as mock_get_tree, \
             patch('stagehand.handlers.observe_handler.get_xpath_by_resolved_object_id') as mock_get_xpath:
            
            mock_get_tree.return_value = {
                "simplified": "[1] button: Submit button",
                "iframes": []
            }
            mock_get_xpath.return_value = "//button[@id='submit-button']"
            
            # Mock CDP responses
            mock_stagehand_page.send_cdp = AsyncMock(return_value={
                "object": {"objectId": "mock-object-id"}
            })
            mock_cdp_client = AsyncMock()
            mock_stagehand_page.get_cdp_client = AsyncMock(return_value=mock_cdp_client)
            
            # Create handler and run observe
            handler = ObserveHandler(mock_stagehand_page, mock_client, "")
            options = ObserveOptions(instruction="find the submit button")
            result = await handler.observe(options)
        
        # Verify results
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ObserveResult)
        assert result[0].selector == "xpath=//button[@id='submit-button']"
        assert result[0].description == "Submit button in the form"
        assert result[0].method == "click"
        
        # Verify that LLM was called
        assert mock_llm.call_count == 1
