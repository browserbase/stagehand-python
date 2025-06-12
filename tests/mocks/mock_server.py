"""Mock Stagehand server for testing API interactions without a real server"""

import json
from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock
import httpx


class MockHttpResponse:
    """Mock HTTP response object"""
    
    def __init__(self, status_code: int, content: Any, success: bool = True):
        self.status_code = status_code
        self._content = content
        self.success = success
        
        # Create headers
        self.headers = {
            "content-type": "application/json" if isinstance(content, dict) else "text/plain"
        }
        
        # Create request object
        self.request = MagicMock()
        self.request.url = "https://mock-server.com/api/endpoint"
        self.request.method = "POST"
    
    def json(self) -> Any:
        """Return JSON content"""
        if isinstance(self._content, dict):
            return self._content
        elif isinstance(self._content, str):
            try:
                return json.loads(self._content)
            except json.JSONDecodeError:
                return {"content": self._content}
        else:
            return {"content": str(self._content)}
    
    @property
    def text(self) -> str:
        """Return text content"""
        if isinstance(self._content, str):
            return self._content
        else:
            return json.dumps(self._content)
    
    @property
    def content(self) -> bytes:
        """Return raw content as bytes"""
        return self.text.encode("utf-8")
    
    def raise_for_status(self):
        """Raise exception for bad status codes"""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}", 
                request=self.request, 
                response=self
            )


class MockStagehandServer:
    """Mock Stagehand server for testing API interactions"""
    
    def __init__(self):
        self.sessions = {}
        self.call_history = []
        self.response_overrides = {}
        self.should_fail = False
        self.failure_status = 500
        self.failure_message = "Mock server error"
        
        # Default responses for different endpoints
        self.default_responses = {
            "create_session": {
                "success": True,
                "sessionId": "mock-session-123",
                "browserbaseSessionId": "bb-session-456"
            },
            "navigate": {
                "success": True,
                "url": "https://example.com",
                "title": "Test Page"
            },
            "act": {
                "success": True,
                "message": "Action completed successfully",
                "action": "clicked button"
            },
            "observe": [
                {
                    "selector": "#test-button",
                    "description": "Test button element",
                    "backend_node_id": 123,
                    "method": "click",
                    "arguments": []
                }
            ],
            "extract": {
                "extraction": "Sample extracted data",
                "title": "Test Title"
            },
            "screenshot": "base64_encoded_screenshot_data"
        }
    
    def create_mock_http_client(self) -> MagicMock:
        """Create a mock HTTP client that routes calls to this server"""
        client = MagicMock(spec=httpx.AsyncClient)
        
        # Set up async context manager methods
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock()
        client.close = AsyncMock()
        
        # Set up request methods
        client.post = AsyncMock(side_effect=self._handle_post_request)
        client.get = AsyncMock(side_effect=self._handle_get_request)
        client.put = AsyncMock(side_effect=self._handle_put_request)
        client.delete = AsyncMock(side_effect=self._handle_delete_request)
        
        return client
    
    async def _handle_post_request(self, url: str, **kwargs) -> MockHttpResponse:
        """Handle mock POST requests"""
        return await self._handle_request("POST", url, **kwargs)
    
    async def _handle_get_request(self, url: str, **kwargs) -> MockHttpResponse:
        """Handle mock GET requests"""
        return await self._handle_request("GET", url, **kwargs)
    
    async def _handle_put_request(self, url: str, **kwargs) -> MockHttpResponse:
        """Handle mock PUT requests"""
        return await self._handle_request("PUT", url, **kwargs)
    
    async def _handle_delete_request(self, url: str, **kwargs) -> MockHttpResponse:
        """Handle mock DELETE requests"""
        return await self._handle_request("DELETE", url, **kwargs)
    
    async def _handle_request(self, method: str, url: str, **kwargs) -> MockHttpResponse:
        """Handle mock HTTP requests"""
        # Record the call
        call_info = {
            "method": method,
            "url": url,
            "kwargs": kwargs
        }
        self.call_history.append(call_info)
        
        # Check if we should simulate failure
        if self.should_fail:
            return MockHttpResponse(
                status_code=self.failure_status,
                content={"error": self.failure_message},
                success=False
            )
        
        # Extract endpoint from URL
        endpoint = self._extract_endpoint(url)
        
        # Check for response overrides
        if endpoint in self.response_overrides:
            response_data = self.response_overrides[endpoint]
            if callable(response_data):
                response_data = response_data(method, url, **kwargs)
            return MockHttpResponse(
                status_code=200,
                content=response_data,
                success=True
            )
        
        # Use default responses
        if endpoint in self.default_responses:
            response_data = self.default_responses[endpoint]
            
            # Handle session creation specially
            if endpoint == "create_session":
                session_id = response_data["sessionId"]
                self.sessions[session_id] = {
                    "id": session_id,
                    "browserbase_id": response_data["browserbaseSessionId"],
                    "created": True
                }
            
            return MockHttpResponse(
                status_code=200,
                content=response_data,
                success=True
            )
        
        # Default fallback response
        return MockHttpResponse(
            status_code=200,
            content={"success": True, "message": f"Mock response for {endpoint}"},
            success=True
        )
    
    def _extract_endpoint(self, url: str) -> str:
        """Extract endpoint name from URL"""
        # Remove base URL and extract the last path component
        path = url.split("/")[-1]
        
        # Handle common Stagehand endpoints - check exact matches to avoid substring issues
        if "session" in url and "create" in url:
            endpoint = "create_session"
        elif path == "navigate":
            endpoint = "navigate"
        elif path == "act":
            endpoint = "act"
        elif path == "observe":
            endpoint = "observe"
        elif path == "extract":
            endpoint = "extract"
        elif path == "screenshot":
            endpoint = "screenshot"
        else:
            endpoint = path or "unknown"
            
        return endpoint
    
    def set_response_override(self, endpoint: str, response: Union[Dict, callable]):
        """Override the default response for a specific endpoint"""
        self.response_overrides[endpoint] = response
    
    def clear_response_overrides(self):
        """Clear all response overrides"""
        self.response_overrides.clear()
    
    def simulate_failure(self, should_fail: bool = True, status: int = 500, message: str = "Mock server error"):
        """Configure the server to simulate failures"""
        self.should_fail = should_fail
        self.failure_status = status
        self.failure_message = message
    
    def reset(self):
        """Reset the mock server state"""
        self.sessions.clear()
        self.call_history.clear()
        self.response_overrides.clear()
        self.should_fail = False
        self.failure_status = 500
        self.failure_message = "Mock server error"
    
    def get_call_history(self) -> List[Dict]:
        """Get the history of all calls made to this server"""
        return self.call_history.copy()
    
    def was_called_with_endpoint(self, endpoint: str) -> bool:
        """Check if the server was called with a specific endpoint"""
        for call in self.call_history:
            if endpoint in call["url"]:
                return True
        return False
    
    def get_session_count(self) -> int:
        """Get the number of sessions created"""
        return len(self.sessions)


# Utility functions for setting up server mocks

def create_mock_server_with_client() -> tuple[MockStagehandServer, MagicMock]:
    """Create a mock server and its associated HTTP client"""
    server = MockStagehandServer()
    client = server.create_mock_http_client()
    return server, client


def setup_successful_session_flow(server: MockStagehandServer, session_id: str = "test-session-123"):
    """Set up a mock server with a successful session creation flow"""
    server.set_response_override("create_session", {
        "success": True,
        "sessionId": session_id,
        "browserbaseSessionId": f"bb-{session_id}"
    })
    
    server.set_response_override("navigate", {
        "success": True,
        "url": "https://example.com",
        "title": "Test Page"
    })
    
    return server


def setup_extraction_responses(server: MockStagehandServer, extraction_data: Dict[str, Any]):
    """Set up mock server with custom extraction responses"""
    server.set_response_override("extract", extraction_data)
    return server


def setup_observation_responses(server: MockStagehandServer, observe_results: List[Dict[str, Any]]):
    """Set up mock server with custom observation responses"""
    server.set_response_override("observe", observe_results)
    return server 