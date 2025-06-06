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
    
    @pytest.mark.asyncio
    async def test_observe_multiple_elements(self, mock_stagehand_page):
        """Test observing multiple elements"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
        # Set up mock LLM response for multiple elements
        mock_llm.set_custom_response("observe", [
            {
                "description": "Home navigation link",
                "element_id": 100,
                "method": "click",
                "arguments": []
            },
            {
                "description": "About navigation link",
                "element_id": 101,
                "method": "click",
                "arguments": []
            },
            {
                "description": "Contact navigation link",
                "element_id": 102,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="DOM with navigation")
        
        options = ObserveOptions(instruction="find all navigation links")
        result = await handler.observe(options)
        
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Check all results are ObserveResult instances
        for obs_result in result:
            assert isinstance(obs_result, ObserveResult)
        
        # Check specific elements - should have xpath selectors generated by CDP mock
        assert result[0].selector == "xpath=//a[@id='home-link']"
        assert result[1].selector == "xpath=//a[@id='about-link']"
        assert result[2].selector == "xpath=//a[@id='contact-link']"
    
    
    @pytest.mark.asyncio
    async def test_observe_from_act_context(self, mock_stagehand_page):
        """Test observe when called from act context"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
        # When from_act=True, the function_name becomes "ACT", so set custom response for "act"
        mock_llm.set_custom_response("act", [
            {
                "description": "Element to act on",
                "element_id": 1,  # Use element_id 1 which exists in the accessibility tree
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        # Mock evaluate method for find_scrollable_element_ids
        mock_stagehand_page.evaluate = AsyncMock(return_value=["//body"])
        
        options = ObserveOptions(instruction="find target element")
        result = await handler.observe(options, from_act=True)
        
        assert len(result) == 1
        # The xpath mapping for element_id 1 should be "//div[@id='test']" based on conftest setup
        assert result[0].selector == "xpath=//div[@id='test']"
    
    @pytest.mark.asyncio
    async def test_observe_with_llm_failure(self, mock_stagehand_page):
        """Test handling of LLM API failure during observation"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "Observation API unavailable")
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        options = ObserveOptions(instruction="find elements")
        
        # The observe_inference function catches exceptions and returns empty elements list
        # So we should expect an empty result, not an exception
        result = await handler.observe(options)
        assert isinstance(result, list)
        assert len(result) == 0


class TestObserveOptions:
    """Test different observe options and configurations"""
    
    @pytest.mark.asyncio
    async def test_observe_with_draw_overlay(self, mock_stagehand_page):
        """Test observe with draw_overlay option"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
        mock_llm.set_custom_response("observe", [
            {
                "description": "Element with overlay",
                "element_id": 800,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        # Mock evaluate method for find_scrollable_element_ids
        mock_stagehand_page.evaluate = AsyncMock(return_value=["//div[@id='highlighted-element']"])
        
        options = ObserveOptions(
            instruction="find elements",
            draw_overlay=True
        )
        
        result = await handler.observe(options)
        
        # Should have drawn overlay on elements
        assert len(result) == 1
        # Should have called evaluate for finding scrollable elements
        mock_stagehand_page.evaluate.assert_called()


class TestErrorHandling:
    """Test error handling in observe operations"""
    
    @pytest.mark.asyncio
    async def test_observe_with_no_elements_found(self, mock_stagehand_page):
        """Test observe when no elements are found"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
        # Mock empty result
        mock_llm.set_custom_response("observe", [])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Empty DOM")
        
        options = ObserveOptions(instruction="find non-existent elements")
        result = await handler.observe(options)
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestMetrics:
    """Test metrics collection and logging in observe operations"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_on_successful_observation(self, mock_stagehand_page):
        """Test that metrics are collected on successful observation"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        options = ObserveOptions(instruction="find elements")
        await handler.observe(options)
        
        # Should have called update_metrics
        mock_client.update_metrics.assert_called_once()
    
# TODO: move to llm/inference tests
class TestPromptGeneration:
    """Test prompt generation for observation"""
    
    def test_prompt_includes_user_instructions(self, mock_stagehand_page):
        """Test that prompts include user-provided instructions"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        user_instructions = "Focus on finding interactive elements only"
        handler = ObserveHandler(mock_stagehand_page, mock_client, user_instructions)
        
        assert handler.user_provided_instructions == user_instructions
    
    def test_prompt_includes_observation_context(self, mock_stagehand_page):
        """Test that prompts include relevant observation context"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        # Mock DOM context
        mock_stagehand_page._page.evaluate = AsyncMock(return_value=[
            {"id": "test", "text": "Test element"}
        ])
        
        # This would test that DOM context is included in prompts
        # Actual implementation would depend on prompt structure
        assert handler.stagehand_page == mock_stagehand_page
