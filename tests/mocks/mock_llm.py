"""Mock LLM client for testing without actual API calls"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock


class MockLLMResponse:
    """Mock LLM response object that mimics the structure of real LLM responses"""
    
    def __init__(
        self, 
        content: str, 
        data: Any = None, 
        usage: Optional[Dict[str, int]] = None,
        model: str = "gpt-4o-mini"
    ):
        self.content = content
        self.data = data
        self.model = model
        
        # Create usage statistics
        self.usage = MagicMock()
        usage_data = usage or {"prompt_tokens": 100, "completion_tokens": 50}
        self.usage.prompt_tokens = usage_data.get("prompt_tokens", 100)
        self.usage.completion_tokens = usage_data.get("completion_tokens", 50)
        self.usage.total_tokens = self.usage.prompt_tokens + self.usage.completion_tokens
        
        # Create choices structure for compatibility with different LLM clients
        choice = MagicMock()
        choice.message = MagicMock()
        choice.message.content = content
        choice.finish_reason = "stop"
        self.choices = [choice]
        
        # For some libraries that expect different structure
        self.text = content
        self.message = MagicMock()
        self.message.content = content
        
        # Hidden params for some litellm compatibility
        self._hidden_params = {
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens
            }
        }


class MockLLMClient:
    """Mock LLM client for testing without actual API calls"""
    
    def __init__(self, api_key: str = "test-api-key", default_model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.default_model = default_model
        self.call_count = 0
        self.last_messages = None
        self.last_model = None
        self.last_kwargs = None
        self.call_history = []
        
        # Configurable responses for different scenarios
        self.response_mapping = {
            "act": self._default_act_response,
            "extract": self._default_extract_response,
            "observe": self._default_observe_response,
            "agent": self._default_agent_response
        }
        
        # Custom responses that can be set by tests
        self.custom_responses = {}
        
        # Simulate failures
        self.should_fail = False
        self.failure_message = "Mock API failure"
        
        # Metrics callback for tracking
        self.metrics_callback = None
    
    async def completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> MockLLMResponse:
        """Mock completion method"""
        self.call_count += 1
        self.last_messages = messages
        self.last_model = model or self.default_model
        self.last_kwargs = kwargs
        
        # Store call in history
        call_info = {
            "messages": messages,
            "model": self.last_model,
            "kwargs": kwargs,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.call_history.append(call_info)
        
        # Simulate failure if configured
        if self.should_fail:
            raise Exception(self.failure_message)
        
        # Determine response type based on messages content
        content = str(messages).lower()
        response_type = self._determine_response_type(content)
        
        # Check for custom responses first
        if response_type in self.custom_responses:
            response_data = self.custom_responses[response_type]
            if callable(response_data):
                response_data = response_data(messages, **kwargs)
            return self._create_response(response_data, model=self.last_model)
        
        # Use default response mapping
        response_generator = self.response_mapping.get(response_type, self._default_response)
        response_data = response_generator(messages, **kwargs)
        
        response = self._create_response(response_data, model=self.last_model)
        
        # Call metrics callback if set
        if self.metrics_callback:
            self.metrics_callback(response, 100, response_type)  # 100ms mock inference time
        
        return response
    
    def _determine_response_type(self, content: str) -> str:
        """Determine the type of response based on message content"""
        if "click" in content or "type" in content or "scroll" in content:
            return "act"
        elif "extract" in content or "data" in content:
            return "extract"
        elif "observe" in content or "find" in content or "locate" in content:
            return "observe"
        elif "agent" in content or "execute" in content:
            return "agent"
        else:
            return "default"
    
    def _create_response(self, data: Any, model: str) -> MockLLMResponse:
        """Create a MockLLMResponse from data"""
        if isinstance(data, str):
            return MockLLMResponse(data, model=model)
        elif isinstance(data, dict):
            # For extract responses, convert dict to JSON string for content
            import json
            content = json.dumps(data)
            return MockLLMResponse(content, data=data, model=model)
        elif isinstance(data, list):
            # For observe responses, convert list to JSON string for content
            import json
            # Wrap the list in the expected format for observe responses
            response_dict = {"elements": data}
            content = json.dumps(response_dict)
            return MockLLMResponse(content, data=response_dict, model=model)
        else:
            return MockLLMResponse(str(data), data=data, model=model)
    
    def _default_act_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Default response for act operations"""
        return {
            "success": True,
            "message": "Successfully performed the action",
            "action": "mock action execution",
            "selector": "#mock-element",
            "method": "click"
        }
    
    def _default_extract_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Default response for extract operations"""
        return {
            "extraction": "Mock extracted data",
            "title": "Sample Title",
            "description": "Sample description for testing"
        }
    
    def _default_observe_response(self, messages: List[Dict], **kwargs) -> List[Dict[str, Any]]:
        """Default response for observe operations"""
        return [
            {
                "selector": "#mock-element-1",
                "description": "Mock element for testing",
                "backend_node_id": 123,
                "method": "click",
                "arguments": []
            },
            {
                "selector": "#mock-element-2", 
                "description": "Another mock element",
                "backend_node_id": 124,
                "method": "click",
                "arguments": []
            }
        ]
    
    def _default_agent_response(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Default response for agent operations"""
        return {
            "success": True,
            "actions": [
                {"type": "navigate", "url": "https://example.com"},
                {"type": "click", "selector": "#test-button"}
            ],
            "message": "Agent task completed successfully",
            "completed": True
        }
    
    def _default_response(self, messages: List[Dict], **kwargs) -> str:
        """Default fallback response"""
        return "Mock LLM response for testing"
    
    def set_custom_response(self, response_type: str, response_data: Union[str, Dict, callable]):
        """Set a custom response for a specific response type"""
        self.custom_responses[response_type] = response_data
    
    def clear_custom_responses(self):
        """Clear all custom responses"""
        self.custom_responses.clear()
    
    def simulate_failure(self, should_fail: bool = True, message: str = "Mock API failure"):
        """Configure the client to simulate API failures"""
        self.should_fail = should_fail
        self.failure_message = message
    
    def reset(self):
        """Reset the mock client state"""
        self.call_count = 0
        self.last_messages = None
        self.last_model = None
        self.last_kwargs = None
        self.call_history.clear()
        self.custom_responses.clear()
        self.should_fail = False
        self.failure_message = "Mock API failure"
    
    def get_call_history(self) -> List[Dict]:
        """Get the history of all calls made to this client"""
        return self.call_history.copy()
    
    def was_called_with_content(self, content: str) -> bool:
        """Check if the client was called with messages containing specific content"""
        for call in self.call_history:
            if content.lower() in str(call["messages"]).lower():
                return True
        return False
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get aggregated usage statistics"""
        total_prompt_tokens = self.call_count * 100  # Mock 100 tokens per call
        total_completion_tokens = self.call_count * 50  # Mock 50 tokens per response
        
        return {
            "total_calls": self.call_count,
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens
        }
    
    async def create_response(
        self,
        *,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        function_name: Optional[str] = None,
        **kwargs
    ) -> MockLLMResponse:
        """Create a response using the same interface as the real LLMClient"""
        # Use function_name to determine response type if available
        if function_name:
            response_type = function_name.lower()
        else:
            # Fall back to content-based detection
            content = str(messages).lower()
            response_type = self._determine_response_type(content)

        # Track the call
        self.call_count += 1
        self.last_messages = messages
        self.last_model = model or self.default_model
        self.last_kwargs = kwargs

        # Store call in history
        call_info = {
            "messages": messages,
            "model": self.last_model,
            "kwargs": kwargs,
            "function_name": function_name,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.call_history.append(call_info)

        # Simulate failure if configured
        if self.should_fail:
            raise Exception(self.failure_message)

        # Check for custom responses first
        if response_type in self.custom_responses:
            response_data = self.custom_responses[response_type]
            if callable(response_data):
                response_data = response_data(messages, **kwargs)
            return self._create_response(response_data, model=self.last_model)

        # Use default response mapping
        response_generator = self.response_mapping.get(response_type, self._default_response)
        response_data = response_generator(messages, **kwargs)

        response = self._create_response(response_data, model=self.last_model)

        # Call metrics callback if set
        if self.metrics_callback:
            self.metrics_callback(response, 100, response_type)  # 100ms mock inference time

        return response 