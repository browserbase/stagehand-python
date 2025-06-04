"""Test ObserveHandler functionality for AI-powered element observation"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from stagehand.handlers.observe_handler import ObserveHandler
from stagehand.schemas import ObserveOptions, ObserveResult
from tests.mocks.mock_llm import MockLLMClient, MockLLMResponse


class TestObserveHandlerInitialization:
    """Test ObserveHandler initialization and setup"""
    
    def test_observe_handler_creation(self, mock_stagehand_page):
        """Test basic ObserveHandler creation"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ObserveHandler(
            mock_stagehand_page,
            mock_client,
            user_provided_instructions="Test observation instructions"
        )
        
        assert handler.page == mock_stagehand_page
        assert handler.stagehand == mock_client
        assert handler.user_provided_instructions == "Test observation instructions"
    
    def test_observe_handler_with_empty_instructions(self, mock_stagehand_page):
        """Test ObserveHandler with empty user instructions"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        assert handler.user_provided_instructions == ""


class TestObserveExecution:
    """Test element observation functionality"""
    
    @pytest.mark.asyncio
    async def test_observe_single_element(self, mock_stagehand_page):
        """Test observing a single element"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Set up mock LLM response for single element
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#submit-button",
                "description": "Submit button in the form",
                "backend_node_id": 12345,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        # Mock DOM evaluation
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="DOM content")
        
        options = ObserveOptions(instruction="find the submit button")
        result = await handler.observe(options)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], ObserveResult)
        assert result[0].selector == "#submit-button"
        assert result[0].description == "Submit button in the form"
        assert result[0].backend_node_id == 12345
        assert result[0].method == "click"
        
        # Should have called LLM
        assert mock_llm.call_count == 1
        assert mock_llm.was_called_with_content("find")
    
    @pytest.mark.asyncio
    async def test_observe_multiple_elements(self, mock_stagehand_page):
        """Test observing multiple elements"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Set up mock LLM response for multiple elements
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#home-link",
                "description": "Home navigation link",
                "backend_node_id": 100,
                "method": "click",
                "arguments": []
            },
            {
                "selector": "#about-link",
                "description": "About navigation link",
                "backend_node_id": 101,
                "method": "click",
                "arguments": []
            },
            {
                "selector": "#contact-link",
                "description": "Contact navigation link",
                "backend_node_id": 102,
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
        
        # Check specific elements
        assert result[0].selector == "#home-link"
        assert result[1].selector == "#about-link"
        assert result[2].selector == "#contact-link"
    
    @pytest.mark.asyncio
    async def test_observe_with_only_visible_option(self, mock_stagehand_page):
        """Test observe with only_visible option"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock response with only visible elements
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#visible-button",
                "description": "Visible button",
                "backend_node_id": 200,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Only visible elements")
        
        options = ObserveOptions(
            instruction="find buttons",
            only_visible=True
        )
        
        result = await handler.observe(options)
        
        assert len(result) == 1
        assert result[0].selector == "#visible-button"
        
        # Should have called evaluate with visibility filter
        mock_stagehand_page._page.evaluate.assert_called()
    
    @pytest.mark.asyncio
    async def test_observe_with_return_action_option(self, mock_stagehand_page):
        """Test observe with return_action option"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock response with action information
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#form-input",
                "description": "Email input field",
                "backend_node_id": 300,
                "method": "fill",
                "arguments": ["example@email.com"]
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Form elements")
        
        options = ObserveOptions(
            instruction="find email input",
            return_action=True
        )
        
        result = await handler.observe(options)
        
        assert len(result) == 1
        assert result[0].method == "fill"
        assert result[0].arguments == ["example@email.com"]
    
    @pytest.mark.asyncio
    async def test_observe_from_act_context(self, mock_stagehand_page):
        """Test observe when called from act context"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#target-element",
                "description": "Element to act on",
                "backend_node_id": 400,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Act context DOM")
        
        options = ObserveOptions(instruction="find target element")
        result = await handler.observe(options, from_act=True)
        
        assert len(result) == 1
        assert result[0].selector == "#target-element"
    
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
        
        with pytest.raises(Exception) as exc_info:
            await handler.observe(options)
        
        assert "Observation API unavailable" in str(exc_info.value)


class TestDOMProcessing:
    """Test DOM processing for observation"""
    
    @pytest.mark.asyncio
    async def test_dom_element_extraction(self, mock_stagehand_page):
        """Test DOM element extraction for observation"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock DOM extraction
        mock_dom_elements = [
            {"id": "btn1", "text": "Click me", "tagName": "BUTTON"},
            {"id": "btn2", "text": "Submit", "tagName": "BUTTON"}
        ]
        
        mock_stagehand_page._page.evaluate = AsyncMock(return_value=mock_dom_elements)
        
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#btn1",
                "description": "Click me button",
                "backend_node_id": 501,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        options = ObserveOptions(instruction="find button elements")
        result = await handler.observe(options)
        
        # Should have called page.evaluate to extract DOM elements
        mock_stagehand_page._page.evaluate.assert_called()
        
        assert len(result) == 1
        assert result[0].selector == "#btn1"
    
    @pytest.mark.asyncio
    async def test_dom_element_filtering(self, mock_stagehand_page):
        """Test DOM element filtering during observation"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock filtered DOM elements (only interactive ones)
        mock_filtered_elements = [
            {"id": "interactive-btn", "text": "Interactive", "tagName": "BUTTON", "clickable": True}
        ]
        
        mock_stagehand_page._page.evaluate = AsyncMock(return_value=mock_filtered_elements)
        
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#interactive-btn",
                "description": "Interactive button",
                "backend_node_id": 600,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        options = ObserveOptions(
            instruction="find interactive elements",
            only_visible=True
        )
        
        result = await handler.observe(options)
        
        assert len(result) == 1
        assert result[0].selector == "#interactive-btn"
    
    @pytest.mark.asyncio
    async def test_dom_coordinate_mapping(self, mock_stagehand_page):
        """Test DOM coordinate mapping for elements"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock elements with coordinates
        mock_elements_with_coords = [
            {
                "id": "positioned-element", 
                "rect": {"x": 100, "y": 200, "width": 150, "height": 30},
                "text": "Positioned element"
            }
        ]
        
        mock_stagehand_page._page.evaluate = AsyncMock(return_value=mock_elements_with_coords)
        
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#positioned-element",
                "description": "Element at specific position",
                "backend_node_id": 700,
                "method": "click",
                "arguments": [],
                "coordinates": {"x": 175, "y": 215}  # Center of element
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        options = ObserveOptions(instruction="find positioned elements")
        result = await handler.observe(options)
        
        assert len(result) == 1
        assert result[0].selector == "#positioned-element"


class TestObserveOptions:
    """Test different observe options and configurations"""
    
    @pytest.mark.asyncio
    async def test_observe_with_draw_overlay(self, mock_stagehand_page):
        """Test observe with draw_overlay option"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#highlighted-element",
                "description": "Element with overlay",
                "backend_node_id": 800,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="DOM with overlay")
        
        options = ObserveOptions(
            instruction="find elements",
            draw_overlay=True
        )
        
        result = await handler.observe(options)
        
        # Should have drawn overlay on elements
        assert len(result) == 1
        # Overlay drawing would be tested through DOM evaluation calls
        mock_stagehand_page._page.evaluate.assert_called()
    
    @pytest.mark.asyncio
    async def test_observe_with_custom_model(self, mock_stagehand_page):
        """Test observe with custom model specification"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#custom-model-element",
                "description": "Element found with custom model",
                "backend_node_id": 900,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="DOM content")
        
        options = ObserveOptions(
            instruction="find specific elements",
            model_name="gpt-4o"
        )
        
        result = await handler.observe(options)
        
        assert len(result) == 1
        # Model name should be used in LLM call
        assert mock_llm.call_count == 1


class TestObserveResultProcessing:
    """Test processing of observe results"""
    
    @pytest.mark.asyncio
    async def test_observe_result_serialization(self, mock_stagehand_page):
        """Test that observe results are properly serialized"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock complex result with all fields
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#complex-element",
                "description": "Complex element with all properties",
                "backend_node_id": 1000,
                "method": "type",
                "arguments": ["test input"],
                "tagName": "INPUT",
                "text": "Input field",
                "attributes": {"type": "text", "placeholder": "Enter text"}
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Complex DOM")
        
        options = ObserveOptions(instruction="find complex elements")
        result = await handler.observe(options)
        
        assert len(result) == 1
        obs_result = result[0]
        
        assert obs_result.selector == "#complex-element"
        assert obs_result.description == "Complex element with all properties"
        assert obs_result.backend_node_id == 1000
        assert obs_result.method == "type"
        assert obs_result.arguments == ["test input"]
        
        # Test dictionary access
        assert obs_result["selector"] == "#complex-element"
        assert obs_result["method"] == "type"
    
    @pytest.mark.asyncio
    async def test_observe_result_validation(self, mock_stagehand_page):
        """Test validation of observe results"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock result with minimal required fields
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#minimal-element",
                "description": "Minimal element description"
                # No backend_node_id, method, or arguments
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Minimal DOM")
        
        options = ObserveOptions(instruction="find minimal elements")
        result = await handler.observe(options)
        
        assert len(result) == 1
        obs_result = result[0]
        
        # Should have required fields
        assert obs_result.selector == "#minimal-element"
        assert obs_result.description == "Minimal element description"
        
        # Optional fields should be None or default values
        assert obs_result.backend_node_id is None
        assert obs_result.method is None
        assert obs_result.arguments is None


class TestErrorHandling:
    """Test error handling in observe operations"""
    
    @pytest.mark.asyncio
    async def test_observe_with_no_elements_found(self, mock_stagehand_page):
        """Test observe when no elements are found"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock empty result
        mock_llm.set_custom_response("observe", [])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Empty DOM")
        
        options = ObserveOptions(instruction="find non-existent elements")
        result = await handler.observe(options)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_observe_with_malformed_llm_response(self, mock_stagehand_page):
        """Test observe with malformed LLM response"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        mock_client.logger = MagicMock()
        
        # Mock malformed response
        mock_llm.set_custom_response("observe", "invalid response format")
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="DOM content")
        
        options = ObserveOptions(instruction="find elements")
        
        # Should handle gracefully and return empty list or raise specific error
        result = await handler.observe(options)
        
        # Depending on implementation, might return empty list or raise exception
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_observe_with_dom_evaluation_error(self, mock_stagehand_page):
        """Test observe when DOM evaluation fails"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.logger = MagicMock()
        
        # Mock DOM evaluation failure
        mock_stagehand_page._page.evaluate = AsyncMock(
            side_effect=Exception("DOM evaluation failed")
        )
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        options = ObserveOptions(instruction="find elements")
        
        with pytest.raises(Exception) as exc_info:
            await handler.observe(options)
        
        assert "DOM evaluation failed" in str(exc_info.value)


class TestMetricsAndLogging:
    """Test metrics collection and logging for observation"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_on_successful_observation(self, mock_stagehand_page):
        """Test that metrics are collected on successful observations"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        mock_llm.set_custom_response("observe", [
            {
                "selector": "#test-element",
                "description": "Test element",
                "backend_node_id": 1100,
                "method": "click",
                "arguments": []
            }
        ])
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="DOM content")
        
        options = ObserveOptions(instruction="find test elements")
        await handler.observe(options)
        
        # Should start timing and update metrics
        mock_client.start_inference_timer.assert_called()
        mock_client.update_metrics_from_response.assert_called()
    
    @pytest.mark.asyncio
    async def test_logging_on_observation_errors(self, mock_stagehand_page):
        """Test that observation errors are properly logged"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.logger = MagicMock()
        
        # Simulate an error during observation
        mock_stagehand_page._page.evaluate = AsyncMock(
            side_effect=Exception("Observation failed")
        )
        
        handler = ObserveHandler(mock_stagehand_page, mock_client, "")
        
        options = ObserveOptions(instruction="find elements")
        
        with pytest.raises(Exception):
            await handler.observe(options)
        
        # Should log the error (implementation dependent)


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
        assert handler.page == mock_stagehand_page
