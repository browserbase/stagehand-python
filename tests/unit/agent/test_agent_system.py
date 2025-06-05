"""Test Agent system functionality for autonomous multi-step tasks"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from stagehand.agent.agent import Agent
from stagehand.schemas import AgentConfig, AgentExecuteOptions, AgentExecuteResult, AgentProvider
from stagehand.types.agent import AgentActionType, ClickAction, TypeAction, WaitAction
from tests.mocks.mock_llm import MockLLMClient


class TestAgentInitialization:
    """Test Agent initialization and setup"""
    
    @patch('stagehand.agent.agent.Agent._get_client')
    def test_agent_creation_with_openai_config(self, mock_get_client, mock_stagehand_page):
        """Test agent creation with OpenAI configuration"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(
            mock_client,
            model="computer-use-preview",
            instructions="You are a helpful web automation assistant",
            options={"apiKey": "test-key", "temperature": 0.7}
        )
        
        assert agent.stagehand == mock_client
        assert agent.config.model == "computer-use-preview"
        assert agent.config.instructions == "You are a helpful web automation assistant"
        assert agent.client == mock_agent_client
    
    @patch('stagehand.agent.agent.Agent._get_client')
    def test_agent_creation_with_anthropic_config(self, mock_get_client, mock_stagehand_page):
        """Test agent creation with Anthropic configuration"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(
            mock_client,
            model="claude-3-5-sonnet-latest",
            instructions="You are a precise automation assistant",
            options={"apiKey": "test-anthropic-key"}
        )
        
        assert agent.config.model == "claude-3-5-sonnet-latest"
        assert agent.config.instructions == "You are a precise automation assistant"
        assert agent.client == mock_agent_client
    
    @patch('stagehand.agent.agent.Agent._get_client')
    def test_agent_creation_with_minimal_config(self, mock_get_client, mock_stagehand_page):
        """Test agent creation with minimal configuration"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation - need to provide a valid model
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        assert agent.config.model == "computer-use-preview"
        assert agent.config.instructions is None
        assert agent.client == mock_agent_client


class TestAgentExecution:
    """Test agent execution functionality"""
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_simple_agent_execution(self, mock_get_client, mock_stagehand_page):
        """Test simple agent task execution"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation and run_task method
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(
            mock_client,
            model="computer-use-preview",
            instructions="Complete web automation tasks"
        )
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Task completed successfully"
        mock_result.completed = True
        mock_result.usage = MagicMock()
        mock_result.usage.input_tokens = 100
        mock_result.usage.output_tokens = 50
        mock_result.usage.inference_time_ms = 1000
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Navigate to example.com and click submit")
        
        assert result.message == "Task completed successfully"
        assert result.completed is True
        assert isinstance(result.actions, list)
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_agent_execution_with_max_steps(self, mock_get_client, mock_stagehand_page):
        """Test agent execution with step limit"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview", max_steps=5)
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Task completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Perform long task")
        
        # Should have called run_task with max_steps
        agent.client.run_task.assert_called_once()
        call_args = agent.client.run_task.call_args
        assert call_args[1]['max_steps'] == 5
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_agent_execution_with_auto_screenshot(self, mock_get_client, mock_stagehand_page):
        """Test agent execution with auto screenshot enabled"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock screenshot functionality
        mock_stagehand_page.screenshot = AsyncMock(return_value="screenshot_data")
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Task completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        from stagehand.types.agent import AgentExecuteOptions
        options = AgentExecuteOptions(
            instruction="Click button with screenshots",
            auto_screenshot=True
        )
        
        result = await agent.execute(options)
        
        assert result.completed is True
        # Should have called run_task with auto_screenshot option
        agent.client.run_task.assert_called_once()
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_agent_execution_with_context(self, mock_get_client, mock_stagehand_page):
        """Test agent execution with additional context"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(
            mock_client,
            model="computer-use-preview",
            instructions="Use provided context to complete tasks"
        )
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Task completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Complete the booking")
        
        assert result.completed is True
        # Should have called run_task
        agent.client.run_task.assert_called_once()
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_agent_execution_failure_handling(self, mock_get_client, mock_stagehand_page):
        """Test agent execution with action failures"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock failing execution
        agent.client.run_task = AsyncMock(side_effect=Exception("Action failed"))
        
        result = await agent.execute("Click missing button")
        
        # Should handle failure gracefully
        assert result.completed is True
        assert "Error:" in result.message


class TestAgentPlanning:
    """Test agent task planning functionality"""
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_task_planning_with_llm(self, mock_get_client, mock_stagehand_page):
        """Test task planning using LLM"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(
            mock_client,
            model="computer-use-preview",
            instructions="Plan web automation tasks step by step"
        )
        
        # Mock the client's run_task method to return a realistic result with proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=ClickAction(type="click", x=100, y=200, button="left")),
            AgentActionType(root=TypeAction(type="type", text="New York", x=50, y=100)),
            AgentActionType(root=ClickAction(type="click", x=150, y=250, button="left"))
        ]
        mock_result.message = "Plan completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Book a hotel in New York")
        
        assert result.completed is True
        assert len(result.actions) == 3
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_task_planning_with_context(self, mock_get_client, mock_stagehand_page):
        """Test task planning with additional context"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Reservation planned"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Make a restaurant reservation")
        
        assert result.completed is True
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_adaptive_planning_with_page_state(self, mock_get_client, mock_stagehand_page):
        """Test planning that adapts to current page state"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock page content extraction
        mock_stagehand_page.extract = AsyncMock(return_value={
            "current_page": "login",
            "elements": ["username_field", "password_field", "login_button"]
        })
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Login planned"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Log into the application")
        
        assert result.completed is True


class TestAgentActionExecution:
    """Test individual action execution"""
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_navigate_action_execution(self, mock_get_client, mock_stagehand_page):
        """Test navigation action execution"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method with proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=ClickAction(type="click", x=100, y=200, button="left"))
        ]
        mock_result.message = "Navigation completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Navigate to example.com")
        
        assert result.completed is True
        assert len(result.actions) == 1
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_click_action_execution(self, mock_get_client, mock_stagehand_page):
        """Test click action execution"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method with proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=ClickAction(type="click", x=100, y=200, button="left"))
        ]
        mock_result.message = "Click completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Click submit button")
        
        assert result.completed is True
        assert len(result.actions) == 1
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_fill_action_execution(self, mock_get_client, mock_stagehand_page):
        """Test fill action execution"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method with proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=TypeAction(type="type", text="test@example.com", x=50, y=100))
        ]
        mock_result.message = "Fill completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Fill email field")
        
        assert result.completed is True
        assert len(result.actions) == 1
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_extract_action_execution(self, mock_get_client, mock_stagehand_page):
        """Test extract action execution"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method with proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=TypeAction(type="type", text="extracted data", x=50, y=100))
        ]
        mock_result.message = "Extraction completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Extract page data")
        
        assert result.completed is True
        assert len(result.actions) == 1
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_wait_action_execution(self, mock_get_client, mock_stagehand_page):
        """Test wait action execution"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method with proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=WaitAction(type="wait", miliseconds=100))
        ]
        mock_result.message = "Wait completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Wait for element")
        
        assert result.completed is True
        assert len(result.actions) == 1
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_action_execution_failure(self, mock_get_client, mock_stagehand_page):
        """Test action execution failure handling"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock failing execution
        agent.client.run_task = AsyncMock(side_effect=Exception("Element not found"))
        
        result = await agent.execute("Click missing element")
        
        assert result.completed is True
        assert "Error:" in result.message
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_unsupported_action_execution(self, mock_get_client, mock_stagehand_page):
        """Test execution of unsupported action types"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method to handle unsupported actions
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Unsupported action handled"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Perform unsupported action")
        
        assert result.completed is True


class TestAgentErrorHandling:
    """Test agent error handling and recovery"""
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_llm_failure_during_planning(self, mock_get_client, mock_stagehand_page):
        """Test handling of LLM failure during planning"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "LLM API unavailable")
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock client failure
        agent.client.run_task = AsyncMock(side_effect=Exception("LLM API unavailable"))
        
        result = await agent.execute("Complete task")
        
        assert result.completed is True
        assert "LLM API unavailable" in result.message
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_page_error_during_execution(self, mock_get_client, mock_stagehand_page):
        """Test handling of page errors during execution"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock page error
        agent.client.run_task = AsyncMock(side_effect=Exception("Page navigation failed"))
        
        result = await agent.execute("Navigate to example")
        
        assert result.completed is True
        assert "Page navigation failed" in result.message
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_partial_execution_recovery(self, mock_get_client, mock_stagehand_page):
        """Test recovery from partial execution failures"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock partial success with proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=ClickAction(type="click", x=100, y=200, button="left")),
            AgentActionType(root=TypeAction(type="type", text="failed", x=50, y=100)),
            AgentActionType(root=ClickAction(type="click", x=150, y=250, button="left"))
        ]
        mock_result.message = "Partial execution completed"
        mock_result.completed = False  # Partial completion
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Complex multi-step task")
        
        assert len(result.actions) == 3
        assert result.completed is False


class TestAgentProviders:
    """Test different agent providers"""
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_openai_agent_provider(self, mock_get_client, mock_stagehand_page):
        """Test OpenAI agent provider functionality"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(
            mock_client,
            model="computer-use-preview",
            options={"apiKey": "test-openai-key"}
        )
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "OpenAI task completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Test OpenAI provider")
        
        assert result.completed is True
        assert "OpenAI" in result.message
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_anthropic_agent_provider(self, mock_get_client, mock_stagehand_page):
        """Test Anthropic agent provider functionality"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(
            mock_client,
            model="claude-3-5-sonnet-latest",
            options={"apiKey": "test-anthropic-key"}
        )
        
        # Mock the client's run_task method
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Anthropic task completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Test Anthropic provider")
        
        assert result.completed is True
        assert "Anthropic" in result.message


class TestAgentMetrics:
    """Test agent metrics collection"""
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_agent_execution_metrics(self, mock_get_client, mock_stagehand_page):
        """Test that agent execution collects metrics"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method with usage data
        mock_result = MagicMock()
        mock_result.actions = []
        mock_result.message = "Task completed"
        mock_result.completed = True
        mock_result.usage = MagicMock()
        mock_result.usage.input_tokens = 150
        mock_result.usage.output_tokens = 75
        mock_result.usage.inference_time_ms = 2000
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Test metrics collection")
        
        assert result.completed is True
        assert result.usage is not None
        # Metrics should be collected through the client
    
    @patch('stagehand.agent.agent.Agent._get_client')
    @pytest.mark.asyncio
    async def test_agent_action_count_tracking(self, mock_get_client, mock_stagehand_page):
        """Test that agent execution tracks action counts"""
        mock_client = MagicMock()
        mock_client.page = mock_stagehand_page
        mock_client.logger = MagicMock()
        
        # Mock the client creation
        mock_agent_client = MagicMock()
        mock_get_client.return_value = mock_agent_client
        
        agent = Agent(mock_client, model="computer-use-preview")
        
        # Mock the client's run_task method with multiple actions as proper AgentActionType objects
        mock_result = MagicMock()
        mock_result.actions = [
            AgentActionType(root=ClickAction(type="click", x=100, y=200, button="left")),
            AgentActionType(root=TypeAction(type="type", text="test", x=50, y=100)),
            AgentActionType(root=ClickAction(type="click", x=150, y=250, button="left"))
        ]
        mock_result.message = "Multiple actions completed"
        mock_result.completed = True
        mock_result.usage = None
        
        agent.client.run_task = AsyncMock(return_value=mock_result)
        
        result = await agent.execute("Perform multiple actions")
        
        assert result.completed is True
        assert len(result.actions) == 3 