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
    
    @pytest.mark.asyncio
    async def test_act_with_pre_observed_action(self, mock_stagehand_page):
        """Test executing pre-observed action without LLM call"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock the playwright method execution
        handler._perform_playwright_method = AsyncMock()
        
        # Pre-observed action payload (ObserveResult format)
        action_payload = {
            "selector": "xpath=//button[@id='submit-btn']",
            "method": "click",
            "arguments": [],
            "description": "Submit button"
        }
        
        result = await handler.act(action_payload)
        
        assert isinstance(result, ActResult)
        assert result.success is True
        assert "performed successfully" in result.message
        
        # Should not call observe handler for pre-observed actions
        handler._perform_playwright_method.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_act_with_llm_failure(self, mock_stagehand_page):
        """Test handling of LLM API failure"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "API rate limit exceeded")
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock the observe handler to fail with LLM error
        mock_stagehand_page._observe_handler = MagicMock()
        mock_stagehand_page._observe_handler.observe = AsyncMock(side_effect=Exception("API rate limit exceeded"))
        
        result = await handler.act({"action": "click button"})
        
        assert isinstance(result, ActResult)
        assert result.success is False
        assert "Failed to perform act" in result.message


class TestSelfHealing:
    """Test self-healing functionality when actions fail"""
    
    @pytest.mark.asyncio
    async def test_self_healing_enabled_retries_on_failure(self, mock_stagehand_page):
        """Test that self-healing retries actions when enabled"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", self_heal=True)
        
        # Mock a pre-observed action that fails first time
        action_payload = {
            "selector": "xpath=//button[@id='btn']",
            "method": "click",
            "arguments": [],
            "description": "Test button"
        }
        
        # Mock self-healing by having the page.act method succeed on retry
        mock_stagehand_page.act = AsyncMock(return_value=ActResult(
            success=True,
            message="Self-heal successful",
            action="Test button"
        ))
        
        # First attempt fails, should trigger self-heal
        handler._perform_playwright_method = AsyncMock(side_effect=Exception("Element not clickable"))
        
        result = await handler.act(action_payload)
        
        assert isinstance(result, ActResult)
        assert result.success is True
        # Self-healing should have been attempted
        mock_stagehand_page.act.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_self_healing_disabled_no_retry(self, mock_stagehand_page):
        """Test that self-healing doesn't retry when disabled"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", self_heal=False)
        
        # Mock a pre-observed action that fails
        action_payload = {
            "selector": "xpath=//button[@id='btn']",
            "method": "click",
            "arguments": [],
            "description": "Test button"
        }
        
        # Mock action execution to fail
        handler._perform_playwright_method = AsyncMock(side_effect=Exception("Element not found"))
        
        result = await handler.act(action_payload)
        
        assert isinstance(result, ActResult)
        assert result.success is False
        assert "Failed to perform act" in result.message
    
    @pytest.mark.asyncio
    async def test_self_healing_max_retry_limit(self, mock_stagehand_page):
        """Test that self-healing eventually gives up after retries"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", self_heal=True)
        
        # Mock a pre-observed action that always fails
        action_payload = {
            "selector": "xpath=//button[@id='btn']",
            "method": "click",
            "arguments": [],
            "description": "Always fails button"
        }
        
        # Mock self-healing to also fail
        mock_stagehand_page.act = AsyncMock(return_value=ActResult(
            success=False,
            message="Self-heal also failed",
            action="Always fails button"
        ))
        
        # First attempt fails, triggers self-heal which also fails
        handler._perform_playwright_method = AsyncMock(side_effect=Exception("Always fails"))
        
        result = await handler.act(action_payload)
        
        assert isinstance(result, ActResult)
        # Should eventually give up and return failure
        assert result.success is False


 # TODO: move to test_act_handler_utils.py
class TestActionExecution:
    """Test low-level action execution methods"""
    
    @pytest.mark.asyncio
    async def test_execute_click_action(self, mock_stagehand_page):
        """Test executing click action through _perform_playwright_method"""
        mock_client = MagicMock()
        mock_client.logger = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock page locator and click method
        mock_locator = MagicMock()
        mock_locator.first = mock_locator
        mock_locator.click = AsyncMock()
        mock_stagehand_page._page.locator.return_value = mock_locator
        mock_stagehand_page._page.url = "http://test.com"
        mock_stagehand_page._wait_for_settled_dom = AsyncMock()
        
        # Mock method handler to just call the locator method
        with patch('stagehand.handlers.act_handler.method_handler_map', {"click": AsyncMock()}):
            await handler._perform_playwright_method("click", [], "//button[@id='submit-btn']")
        
        # Should have created locator with xpath
        mock_stagehand_page._page.locator.assert_called_with("xpath=//button[@id='submit-btn']")
    
    @pytest.mark.asyncio
    async def test_execute_type_action(self, mock_stagehand_page):
        """Test executing type action through _perform_playwright_method"""
        mock_client = MagicMock()
        mock_client.logger = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock page locator and fill method
        mock_locator = MagicMock()
        mock_locator.first = mock_locator
        mock_locator.fill = AsyncMock()
        mock_stagehand_page._page.locator.return_value = mock_locator
        mock_stagehand_page._page.url = "http://test.com"
        mock_stagehand_page._wait_for_settled_dom = AsyncMock()
        
        # Mock method handler
        with patch('stagehand.handlers.act_handler.method_handler_map', {"fill": AsyncMock()}):
            await handler._perform_playwright_method("fill", ["test text"], "//input[@id='input-field']")
        
        # Should have created locator with xpath
        mock_stagehand_page._page.locator.assert_called_with("xpath=//input[@id='input-field']")
    
    @pytest.mark.asyncio
    async def test_execute_action_with_timeout(self, mock_stagehand_page):
        """Test action execution with timeout"""
        mock_client = MagicMock()
        mock_client.logger = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock locator that times out
        mock_locator = MagicMock()
        mock_locator.first = mock_locator
        mock_stagehand_page._page.locator.return_value = mock_locator
        mock_stagehand_page._page.url = "http://test.com"
        mock_stagehand_page._wait_for_settled_dom = AsyncMock()
        
        # Mock method handler to raise timeout
        async def mock_timeout_handler(context):
            raise Exception("Timeout waiting for selector")
        
        with patch('stagehand.handlers.act_handler.method_handler_map', {"click": mock_timeout_handler}):
            with pytest.raises(Exception) as exc_info:
                await handler._perform_playwright_method("click", [], "//div[@id='missing-element']")
            
            assert "Timeout waiting for selector" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_unsupported_action(self, mock_stagehand_page):
        """Test handling of unsupported action methods"""
        mock_client = MagicMock()
        mock_client.logger = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock locator
        mock_locator = MagicMock()
        mock_locator.first = mock_locator
        mock_stagehand_page._page.locator.return_value = mock_locator
        mock_stagehand_page._page.url = "http://test.com"
        mock_stagehand_page._wait_for_settled_dom = AsyncMock()
        
        # Mock method handler map without the unsupported method
        with patch('stagehand.handlers.act_handler.method_handler_map', {}):
            # Mock fallback locator method that doesn't exist
            with patch('stagehand.handlers.act_handler.fallback_locator_method') as mock_fallback:
                mock_fallback.side_effect = AsyncMock()
                mock_locator.unsupported_method = None  # Method doesn't exist
                
                # Should handle gracefully and log warning
                await handler._perform_playwright_method("unsupported_method", [], "//div[@id='element']")
                
                # Should have logged warning about invalid method
                mock_client.logger.warning.assert_called()


class TestPromptGeneration:
    """Test prompt generation for LLM calls"""
    
    def test_prompt_includes_user_instructions(self, mock_stagehand_page):
        """Test that prompts include user-provided instructions"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        user_instructions = "Always be careful with form submissions"
        handler = ActHandler(mock_stagehand_page, mock_client, user_instructions, True)
        
        assert handler.user_provided_instructions == user_instructions


class TestMetricsAndLogging:
    """Test metrics collection and logging"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_on_successful_action(self, mock_stagehand_page):
        """Test that metrics are collected on successful actions"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        mock_client.get_inference_time_ms = MagicMock(return_value=100)
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock the observe handler to return a successful result
        mock_observe_result = ObserveResult(
            selector="xpath=//button[@id='btn']",
            description="Test button",
            method="click",
            arguments=[]
        )
        mock_stagehand_page._observe_handler = MagicMock()
        mock_stagehand_page._observe_handler.observe = AsyncMock(return_value=[mock_observe_result])
        
        # Mock successful execution
        handler._perform_playwright_method = AsyncMock()
        
        await handler.act({"action": "click button"})
        
        # Should start timing
        mock_client.start_inference_timer.assert_called()
        # Metrics are updated in the observe handler, so just check timing was called
        mock_client.get_inference_time_ms.assert_called()


class TestActionValidation:
    """Test action validation and error handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_action_payload(self, mock_stagehand_page):
        """Test handling of invalid action payload"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.logger = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock the observe handler to return empty results
        mock_stagehand_page._observe_handler = MagicMock()
        mock_stagehand_page._observe_handler.observe = AsyncMock(return_value=[])
        
        # Test with payload that has empty action string
        result = await handler.act({"action": ""})
        
        assert isinstance(result, ActResult)
        assert result.success is False
        assert "No observe results found" in result.message
    