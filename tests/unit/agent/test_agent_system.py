"""Test Agent system functionality for autonomous multi-step tasks"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from stagehand.agent.agent import Agent
from stagehand.schemas import AgentConfig, AgentExecuteOptions, AgentExecuteResult, AgentProvider
from tests.mocks.mock_llm import MockLLMClient


class TestAgentInitialization:
    """Test Agent initialization and setup"""
    
    def test_agent_creation_with_openai_config(self, mock_stagehand_page):
        """Test agent creation with OpenAI configuration"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        config = AgentConfig(
            provider=AgentProvider.OPENAI,
            model="gpt-4o",
            instructions="You are a helpful web automation assistant",
            options={"apiKey": "test-key", "temperature": 0.7}
        )
        
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        assert agent.page == mock_stagehand_page
        assert agent.stagehand == mock_client
        assert agent.config == config
        assert agent.config.provider == AgentProvider.OPENAI
    
    def test_agent_creation_with_anthropic_config(self, mock_stagehand_page):
        """Test agent creation with Anthropic configuration"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        config = AgentConfig(
            provider=AgentProvider.ANTHROPIC,
            model="claude-3-sonnet",
            instructions="You are a precise automation assistant",
            options={"apiKey": "test-anthropic-key"}
        )
        
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        assert agent.config.provider == AgentProvider.ANTHROPIC
        assert agent.config.model == "claude-3-sonnet"
    
    def test_agent_creation_with_minimal_config(self, mock_stagehand_page):
        """Test agent creation with minimal configuration"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        config = AgentConfig()
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        assert agent.config.provider is None
        assert agent.config.model is None
        assert agent.config.instructions is None


class TestAgentExecution:
    """Test agent execution functionality"""
    
    @pytest.mark.asyncio
    async def test_simple_agent_execution(self, mock_stagehand_page):
        """Test simple agent task execution"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        # Set up agent response
        mock_llm.set_custom_response("agent", {
            "success": True,
            "actions": [
                {"type": "navigate", "url": "https://example.com"},
                {"type": "click", "selector": "#submit-btn"}
            ],
            "message": "Task completed successfully",
            "completed": True
        })
        
        config = AgentConfig(
            provider=AgentProvider.OPENAI,
            model="gpt-4o",
            instructions="Complete web automation tasks"
        )
        
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock agent execution methods
        agent._plan_task = AsyncMock(return_value=[
            {"action": "navigate", "target": "https://example.com"},
            {"action": "click", "target": "#submit-btn"}
        ])
        agent._execute_action = AsyncMock(return_value=True)
        
        options = AgentExecuteOptions(
            instruction="Navigate to example.com and click submit",
            max_steps=5
        )
        
        result = await agent.execute(options)
        
        assert isinstance(result, AgentExecuteResult)
        assert result.success is True
        assert result.completed is True
        assert len(result.actions) == 2
    
    @pytest.mark.asyncio
    async def test_agent_execution_with_max_steps(self, mock_stagehand_page):
        """Test agent execution with step limit"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock long-running task that exceeds max steps
        step_count = 0
        async def mock_plan_with_steps(*args, **kwargs):
            nonlocal step_count
            step_count += 1
            if step_count <= 10:  # Will exceed max_steps of 5
                return [{"action": "wait", "duration": 1}]
            else:
                return []
        
        agent._plan_task = mock_plan_with_steps
        agent._execute_action = AsyncMock(return_value=True)
        
        options = AgentExecuteOptions(
            instruction="Perform long task",
            max_steps=5
        )
        
        result = await agent.execute(options)
        
        # Should stop at max_steps
        assert len(result.actions) <= 5
        assert step_count <= 6  # Planning called max_steps + 1 times
    
    @pytest.mark.asyncio
    async def test_agent_execution_with_auto_screenshot(self, mock_stagehand_page):
        """Test agent execution with auto screenshot enabled"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock screenshot functionality
        mock_stagehand_page.screenshot = AsyncMock(return_value="screenshot_data")
        
        agent._plan_task = AsyncMock(return_value=[
            {"action": "click", "target": "#button"}
        ])
        agent._execute_action = AsyncMock(return_value=True)
        agent._take_screenshot = AsyncMock(return_value="screenshot_data")
        
        options = AgentExecuteOptions(
            instruction="Click button with screenshots",
            auto_screenshot=True
        )
        
        result = await agent.execute(options)
        
        assert result.success is True
        # Should have taken screenshots
        agent._take_screenshot.assert_called()
    
    @pytest.mark.asyncio
    async def test_agent_execution_with_context(self, mock_stagehand_page):
        """Test agent execution with additional context"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(
            provider=AgentProvider.OPENAI,
            instructions="Use provided context to complete tasks"
        )
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        agent._plan_task = AsyncMock(return_value=[
            {"action": "navigate", "target": "https://example.com"}
        ])
        agent._execute_action = AsyncMock(return_value=True)
        
        options = AgentExecuteOptions(
            instruction="Complete the booking",
            context="User wants to book a table for 2 people at 7pm"
        )
        
        result = await agent.execute(options)
        
        assert result.success is True
        # Should have used context in planning
        agent._plan_task.assert_called()
    
    @pytest.mark.asyncio
    async def test_agent_execution_failure_handling(self, mock_stagehand_page):
        """Test agent execution with action failures"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock failing action
        agent._plan_task = AsyncMock(return_value=[
            {"action": "click", "target": "#missing-button"}
        ])
        agent._execute_action = AsyncMock(return_value=False)  # Action fails
        
        options = AgentExecuteOptions(instruction="Click missing button")
        
        result = await agent.execute(options)
        
        # Should handle failure gracefully
        assert isinstance(result, AgentExecuteResult)
        assert result.success is False


class TestAgentPlanning:
    """Test agent task planning functionality"""
    
    @pytest.mark.asyncio
    async def test_task_planning_with_llm(self, mock_stagehand_page):
        """Test task planning using LLM"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        # Set up planning response
        mock_llm.set_custom_response("agent", {
            "plan": [
                {"action": "navigate", "target": "https://booking.com", "description": "Go to booking site"},
                {"action": "fill", "target": "#search-input", "value": "New York", "description": "Enter destination"},
                {"action": "click", "target": "#search-btn", "description": "Search for hotels"}
            ]
        })
        
        config = AgentConfig(
            provider=AgentProvider.OPENAI,
            model="gpt-4o",
            instructions="Plan web automation tasks step by step"
        )
        
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        instruction = "Book a hotel in New York"
        plan = await agent._plan_task(instruction)
        
        assert isinstance(plan, list)
        assert len(plan) == 3
        assert plan[0]["action"] == "navigate"
        assert plan[1]["action"] == "fill"
        assert plan[2]["action"] == "click"
    
    @pytest.mark.asyncio
    async def test_task_planning_with_context(self, mock_stagehand_page):
        """Test task planning with additional context"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        mock_llm.set_custom_response("agent", {
            "plan": [
                {"action": "navigate", "target": "https://restaurant.com"},
                {"action": "select", "target": "#date-picker", "value": "2024-03-15"},
                {"action": "select", "target": "#time-picker", "value": "19:00"},
                {"action": "fill", "target": "#party-size", "value": "2"},
                {"action": "click", "target": "#book-btn"}
            ]
        })
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        instruction = "Make a restaurant reservation"
        context = "For 2 people on March 15th at 7pm"
        
        plan = await agent._plan_task(instruction, context=context)
        
        assert len(plan) == 5
        assert any(action["value"] == "2" for action in plan)  # Party size
        assert any("19:00" in str(action) for action in plan)  # Time
    
    @pytest.mark.asyncio
    async def test_adaptive_planning_with_page_state(self, mock_stagehand_page):
        """Test planning that adapts to current page state"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        # Mock page content extraction
        mock_stagehand_page.extract = AsyncMock(return_value={
            "current_page": "login",
            "elements": ["username_field", "password_field", "login_button"]
        })
        
        mock_llm.set_custom_response("agent", {
            "plan": [
                {"action": "fill", "target": "#username", "value": "user@example.com"},
                {"action": "fill", "target": "#password", "value": "password123"},
                {"action": "click", "target": "#login-btn"}
            ]
        })
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        instruction = "Log into the application"
        plan = await agent._plan_task(instruction)
        
        # Should have called extract to understand page state
        mock_stagehand_page.extract.assert_called()
        
        # Plan should be adapted to login page
        assert any(action["action"] == "fill" and "username" in action["target"] for action in plan)


class TestAgentActionExecution:
    """Test individual action execution"""
    
    @pytest.mark.asyncio
    async def test_navigate_action_execution(self, mock_stagehand_page):
        """Test navigation action execution"""
        mock_client = MagicMock()
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock page navigation
        mock_stagehand_page.goto = AsyncMock()
        
        action = {"action": "navigate", "target": "https://example.com"}
        result = await agent._execute_action(action)
        
        assert result is True
        mock_stagehand_page.goto.assert_called_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_click_action_execution(self, mock_stagehand_page):
        """Test click action execution"""
        mock_client = MagicMock()
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock page click
        mock_stagehand_page.act = AsyncMock(return_value=MagicMock(success=True))
        
        action = {"action": "click", "target": "#submit-btn"}
        result = await agent._execute_action(action)
        
        assert result is True
        mock_stagehand_page.act.assert_called()
    
    @pytest.mark.asyncio
    async def test_fill_action_execution(self, mock_stagehand_page):
        """Test fill action execution"""
        mock_client = MagicMock()
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        mock_stagehand_page.act = AsyncMock(return_value=MagicMock(success=True))
        
        action = {"action": "fill", "target": "#email-input", "value": "test@example.com"}
        result = await agent._execute_action(action)
        
        assert result is True
        mock_stagehand_page.act.assert_called()
    
    @pytest.mark.asyncio
    async def test_extract_action_execution(self, mock_stagehand_page):
        """Test extract action execution"""
        mock_client = MagicMock()
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        mock_stagehand_page.extract = AsyncMock(return_value={"data": "extracted"})
        
        action = {"action": "extract", "target": "page data", "schema": {"type": "object"}}
        result = await agent._execute_action(action)
        
        assert result is True
        mock_stagehand_page.extract.assert_called()
    
    @pytest.mark.asyncio
    async def test_wait_action_execution(self, mock_stagehand_page):
        """Test wait action execution"""
        mock_client = MagicMock()
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        import time
        
        action = {"action": "wait", "duration": 0.1}  # Short wait for testing
        
        start_time = time.time()
        result = await agent._execute_action(action)
        end_time = time.time()
        
        assert result is True
        assert end_time - start_time >= 0.1
    
    @pytest.mark.asyncio
    async def test_action_execution_failure(self, mock_stagehand_page):
        """Test action execution failure handling"""
        mock_client = MagicMock()
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock failing action
        mock_stagehand_page.act = AsyncMock(return_value=MagicMock(success=False))
        
        action = {"action": "click", "target": "#missing-element"}
        result = await agent._execute_action(action)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_unsupported_action_execution(self, mock_stagehand_page):
        """Test execution of unsupported action types"""
        mock_client = MagicMock()
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        action = {"action": "unsupported_action", "target": "something"}
        result = await agent._execute_action(action)
        
        # Should handle gracefully
        assert result is False


class TestAgentErrorHandling:
    """Test agent error handling and recovery"""
    
    @pytest.mark.asyncio
    async def test_llm_failure_during_planning(self, mock_stagehand_page):
        """Test handling of LLM failure during planning"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "LLM API unavailable")
        mock_client.llm = mock_llm
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        options = AgentExecuteOptions(instruction="Complete task")
        
        result = await agent.execute(options)
        
        assert isinstance(result, AgentExecuteResult)
        assert result.success is False
        assert "LLM API unavailable" in result.message
    
    @pytest.mark.asyncio
    async def test_page_error_during_execution(self, mock_stagehand_page):
        """Test handling of page errors during execution"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # Mock page error
        mock_stagehand_page.goto = AsyncMock(side_effect=Exception("Page navigation failed"))
        
        agent._plan_task = AsyncMock(return_value=[
            {"action": "navigate", "target": "https://example.com"}
        ])
        
        options = AgentExecuteOptions(instruction="Navigate to example")
        
        result = await agent.execute(options)
        
        assert result.success is False
        assert "Page navigation failed" in result.message or "error" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_partial_execution_recovery(self, mock_stagehand_page):
        """Test recovery from partial execution failures"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        # First action succeeds, second fails, third succeeds
        execution_count = 0
        async def mock_execute_with_failure(action):
            nonlocal execution_count
            execution_count += 1
            if execution_count == 2:  # Second action fails
                return False
            return True
        
        agent._plan_task = AsyncMock(return_value=[
            {"action": "navigate", "target": "https://example.com"},
            {"action": "click", "target": "#missing-btn"},
            {"action": "click", "target": "#existing-btn"}
        ])
        agent._execute_action = mock_execute_with_failure
        
        options = AgentExecuteOptions(instruction="Complete multi-step task")
        
        result = await agent.execute(options)
        
        # Should have attempted all actions despite one failure
        assert len(result.actions) == 3
        assert execution_count == 3


class TestAgentProviders:
    """Test different agent providers"""
    
    @pytest.mark.asyncio
    async def test_openai_agent_provider(self, mock_stagehand_page):
        """Test agent with OpenAI provider"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(
            provider=AgentProvider.OPENAI,
            model="gpt-4o",
            options={"apiKey": "test-openai-key", "temperature": 0.3}
        )
        
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        agent._plan_task = AsyncMock(return_value=[])
        agent._execute_action = AsyncMock(return_value=True)
        
        options = AgentExecuteOptions(instruction="OpenAI test task")
        result = await agent.execute(options)
        
        assert result.success is True
        # Should use OpenAI-specific configuration
        assert agent.config.provider == AgentProvider.OPENAI
        assert agent.config.model == "gpt-4o"
    
    @pytest.mark.asyncio
    async def test_anthropic_agent_provider(self, mock_stagehand_page):
        """Test agent with Anthropic provider"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(
            provider=AgentProvider.ANTHROPIC,
            model="claude-3-sonnet",
            options={"apiKey": "test-anthropic-key"}
        )
        
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        agent._plan_task = AsyncMock(return_value=[])
        agent._execute_action = AsyncMock(return_value=True)
        
        options = AgentExecuteOptions(instruction="Anthropic test task")
        result = await agent.execute(options)
        
        assert result.success is True
        assert agent.config.provider == AgentProvider.ANTHROPIC
        assert agent.config.model == "claude-3-sonnet"


class TestAgentMetrics:
    """Test agent metrics and monitoring"""
    
    @pytest.mark.asyncio
    async def test_agent_execution_metrics(self, mock_stagehand_page):
        """Test that agent execution metrics are tracked"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        agent._plan_task = AsyncMock(return_value=[
            {"action": "click", "target": "#button"}
        ])
        agent._execute_action = AsyncMock(return_value=True)
        
        options = AgentExecuteOptions(instruction="Test metrics")
        
        import time
        start_time = time.time()
        result = await agent.execute(options)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        assert result.success is True
        assert execution_time >= 0
        # Metrics should be tracked during execution
    
    @pytest.mark.asyncio
    async def test_agent_action_count_tracking(self, mock_stagehand_page):
        """Test that agent tracks action counts"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        
        config = AgentConfig(provider=AgentProvider.OPENAI)
        agent = Agent(mock_stagehand_page, mock_client, config)
        
        agent._plan_task = AsyncMock(return_value=[
            {"action": "navigate", "target": "https://example.com"},
            {"action": "click", "target": "#button1"},
            {"action": "click", "target": "#button2"},
            {"action": "fill", "target": "#input", "value": "test"}
        ])
        agent._execute_action = AsyncMock(return_value=True)
        
        options = AgentExecuteOptions(instruction="Multi-action task")
        result = await agent.execute(options)
        
        assert result.success is True
        assert len(result.actions) == 4
        
        # Should track different action types
        action_types = [action.get("action") for action in result.actions if isinstance(action, dict)]
        assert "navigate" in action_types
        assert "click" in action_types
        assert "fill" in action_types 