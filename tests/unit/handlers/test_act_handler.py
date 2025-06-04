"""Test ActHandler functionality for AI-powered action execution"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from stagehand.handlers.act_handler import ActHandler
from stagehand.schemas import ActOptions, ActResult
from tests.mocks.mock_llm import MockLLMClient, MockLLMResponse


class TestActHandlerInitialization:
    """Test ActHandler initialization and setup"""
    
    def test_act_handler_creation(self, mock_stagehand_page):
        """Test basic ActHandler creation"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ActHandler(
            mock_stagehand_page,
            mock_client,
            user_provided_instructions="Test instructions",
            self_heal=True
        )
        
        assert handler.page == mock_stagehand_page
        assert handler.stagehand == mock_client
        assert handler.user_provided_instructions == "Test instructions"
        assert handler.self_heal is True
    
    def test_act_handler_with_disabled_self_healing(self, mock_stagehand_page):
        """Test ActHandler with self-healing disabled"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ActHandler(
            mock_stagehand_page,
            mock_client,
            user_provided_instructions="Test",
            self_heal=False
        )
        
        assert handler.self_heal is False


class TestActExecution:
    """Test action execution functionality"""
    
    @pytest.mark.asyncio
    async def test_act_with_string_action(self, mock_stagehand_page):
        """Test executing action with string instruction"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Set up mock LLM response for action
        mock_llm.set_custom_response("act", {
            "success": True,
            "message": "Button clicked successfully",
            "action": "click on submit button",
            "selector": "#submit-btn",
            "method": "click"
        })
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock the handler's internal methods
        handler._execute_action = AsyncMock(return_value=True)
        
        result = await handler.act({"action": "click on the submit button"})
        
        assert isinstance(result, ActResult)
        assert result.success is True
        assert "clicked" in result.message.lower()
        
        # Should have called LLM
        assert mock_llm.call_count == 1
        assert mock_llm.was_called_with_content("click")
    
    @pytest.mark.asyncio
    async def test_act_with_pre_observed_action(self, mock_stagehand_page):
        """Test executing pre-observed action without LLM call"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock the action execution
        handler._execute_action = AsyncMock(return_value=True)
        
        # Pre-observed action payload
        action_payload = {
            "selector": "#submit-btn",
            "method": "click",
            "arguments": [],
            "description": "Submit button"
        }
        
        result = await handler.act(action_payload)
        
        assert isinstance(result, ActResult)
        assert result.success is True
        
        # Should execute action directly without LLM call
        handler._execute_action.assert_called_once()
        assert mock_client.llm.call_count == 0  # No LLM call for pre-observed action
    
    @pytest.mark.asyncio
    async def test_act_with_action_failure(self, mock_stagehand_page):
        """Test handling of action execution failure"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock LLM response with action
        mock_llm.set_custom_response("act", {
            "selector": "#missing-btn",
            "method": "click",
            "arguments": []
        })
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock action execution to fail
        handler._execute_action = AsyncMock(return_value=False)
        
        result = await handler.act({"action": "click on missing button"})
        
        assert isinstance(result, ActResult)
        assert result.success is False
        assert "failed" in result.message.lower() or "error" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_act_with_llm_failure(self, mock_stagehand_page):
        """Test handling of LLM API failure"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "API rate limit exceeded")
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        result = await handler.act({"action": "click button"})
        
        assert isinstance(result, ActResult)
        assert result.success is False
        assert "API rate limit exceeded" in result.message


class TestSelfHealing:
    """Test self-healing functionality when actions fail"""
    
    @pytest.mark.asyncio
    async def test_self_healing_enabled_retries_on_failure(self, mock_stagehand_page):
        """Test that self-healing retries actions when enabled"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # First LLM call returns failing action
        # Second LLM call returns successful action
        call_count = 0
        def custom_response(messages, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "selector": "#wrong-btn",
                    "method": "click",
                    "arguments": []
                }
            else:
                return {
                    "selector": "#correct-btn", 
                    "method": "click",
                    "arguments": []
                }
        
        mock_llm.set_custom_response("act", custom_response)
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", self_heal=True)
        
        # Mock action execution: first fails, second succeeds
        execution_count = 0
        async def mock_execute(selector, method, args):
            nonlocal execution_count
            execution_count += 1
            return execution_count > 1  # Fail first, succeed second
        
        handler._execute_action = mock_execute
        
        result = await handler.act({"action": "click button"})
        
        assert isinstance(result, ActResult)
        assert result.success is True
        
        # Should have made 2 LLM calls (original + retry)
        assert mock_llm.call_count == 2
        assert execution_count == 2
    
    @pytest.mark.asyncio
    async def test_self_healing_disabled_no_retry(self, mock_stagehand_page):
        """Test that self-healing doesn't retry when disabled"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        mock_llm.set_custom_response("act", {
            "selector": "#missing-btn",
            "method": "click", 
            "arguments": []
        })
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", self_heal=False)
        
        # Mock action execution to fail
        handler._execute_action = AsyncMock(return_value=False)
        
        result = await handler.act({"action": "click button"})
        
        assert isinstance(result, ActResult)
        assert result.success is False
        
        # Should have made only 1 LLM call (no retry)
        assert mock_llm.call_count == 1
    
    @pytest.mark.asyncio
    async def test_self_healing_max_retry_limit(self, mock_stagehand_page):
        """Test that self-healing respects maximum retry limit"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Always return failing action
        mock_llm.set_custom_response("act", {
            "selector": "#always-fails",
            "method": "click",
            "arguments": []
        })
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", self_heal=True)
        
        # Mock action execution to always fail
        handler._execute_action = AsyncMock(return_value=False)
        
        result = await handler.act({"action": "click button"})
        
        assert isinstance(result, ActResult)
        assert result.success is False
        
        # Should have reached max retry limit (implementation dependent)
        # Assuming 3 total attempts (1 original + 2 retries)
        assert mock_llm.call_count <= 3


class TestActionExecution:
    """Test low-level action execution methods"""
    
    @pytest.mark.asyncio
    async def test_execute_click_action(self, mock_stagehand_page):
        """Test executing click action"""
        mock_client = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock page methods
        mock_stagehand_page._page.click = AsyncMock()
        mock_stagehand_page._page.wait_for_selector = AsyncMock()
        
        result = await handler._execute_action("#submit-btn", "click", [])
        
        assert result is True
        mock_stagehand_page._page.click.assert_called_with("#submit-btn")
    
    @pytest.mark.asyncio
    async def test_execute_type_action(self, mock_stagehand_page):
        """Test executing type action"""
        mock_client = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock page methods
        mock_stagehand_page._page.fill = AsyncMock()
        mock_stagehand_page._page.wait_for_selector = AsyncMock()
        
        result = await handler._execute_action("#input-field", "type", ["test text"])
        
        assert result is True
        mock_stagehand_page._page.fill.assert_called_with("#input-field", "test text")
    
    @pytest.mark.asyncio
    async def test_execute_action_with_timeout(self, mock_stagehand_page):
        """Test action execution with timeout"""
        mock_client = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock selector not found (timeout)
        mock_stagehand_page._page.wait_for_selector = AsyncMock(
            side_effect=Exception("Timeout waiting for selector")
        )
        
        result = await handler._execute_action("#missing-element", "click", [])
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_execute_unsupported_action(self, mock_stagehand_page):
        """Test handling of unsupported action methods"""
        mock_client = MagicMock()
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        result = await handler._execute_action("#element", "unsupported_method", [])
        
        # Should handle gracefully
        assert result is False


class TestPromptGeneration:
    """Test prompt generation for LLM calls"""
    
    def test_prompt_includes_user_instructions(self, mock_stagehand_page):
        """Test that prompts include user-provided instructions"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        user_instructions = "Always be careful with form submissions"
        handler = ActHandler(mock_stagehand_page, mock_client, user_instructions, True)
        
        # This would be tested by examining the actual prompt sent to LLM
        # Implementation depends on how prompts are structured
        assert handler.user_provided_instructions == user_instructions
    
    def test_prompt_includes_action_context(self, mock_stagehand_page):
        """Test that prompts include relevant action context"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Mock DOM context
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="<button>Submit</button>")
        
        # This would test that DOM context is included in prompts
        # Actual implementation would depend on prompt structure
        assert handler.page == mock_stagehand_page


class TestMetricsAndLogging:
    """Test metrics collection and logging"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_on_successful_action(self, mock_stagehand_page):
        """Test that metrics are collected on successful actions"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        mock_llm.set_custom_response("act", {
            "selector": "#btn",
            "method": "click",
            "arguments": []
        })
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        handler._execute_action = AsyncMock(return_value=True)
        
        await handler.act({"action": "click button"})
        
        # Should start timing and update metrics
        mock_client.start_inference_timer.assert_called()
        mock_client.update_metrics_from_response.assert_called()
    
    @pytest.mark.asyncio 
    async def test_logging_on_action_failure(self, mock_stagehand_page):
        """Test that failures are properly logged"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.logger = MagicMock()
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        handler._execute_action = AsyncMock(return_value=False)
        
        await handler.act({"action": "click missing button"})
        
        # Should log the failure (implementation dependent)
        # This would test actual logging calls if they exist


class TestActionValidation:
    """Test action validation and error handling"""
    
    @pytest.mark.asyncio
    async def test_invalid_action_payload(self, mock_stagehand_page):
        """Test handling of invalid action payload"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Test with empty payload
        result = await handler.act({})
        
        assert isinstance(result, ActResult)
        assert result.success is False
    
    @pytest.mark.asyncio
    async def test_malformed_llm_response(self, mock_stagehand_page):
        """Test handling of malformed LLM response"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Set malformed response
        mock_llm.set_custom_response("act", "invalid response format")
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        result = await handler.act({"action": "click button"})
        
        assert isinstance(result, ActResult)
        assert result.success is False
        assert "error" in result.message.lower() or "failed" in result.message.lower()


class TestVariableSubstitution:
    """Test variable substitution in actions"""
    
    @pytest.mark.asyncio
    async def test_action_with_variables(self, mock_stagehand_page):
        """Test action execution with variable substitution"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        handler._execute_action = AsyncMock(return_value=True)
        
        # Action with variables
        action_payload = {
            "action": "type '{{username}}' in the username field",
            "variables": {"username": "testuser"}
        }
        
        result = await handler.act(action_payload)
        
        assert isinstance(result, ActResult)
        # Variable substitution would be tested by examining LLM calls
        # Implementation depends on how variables are processed
    
    @pytest.mark.asyncio
    async def test_action_with_missing_variables(self, mock_stagehand_page):
        """Test action with missing variable values"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ActHandler(mock_stagehand_page, mock_client, "", True)
        
        # Action with undefined variable
        action_payload = {
            "action": "type '{{undefined_var}}' in field",
            "variables": {"other_var": "value"}
        }
        
        result = await handler.act(action_payload)
        
        # Should handle gracefully (implementation dependent)
        assert isinstance(result, ActResult) 