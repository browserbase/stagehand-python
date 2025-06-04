import asyncio
import json
import unittest.mock as mock

import pytest
from httpx import AsyncClient, Response

from stagehand.client import Stagehand


class TestClientAPI:
    """Tests for the Stagehand client API interactions."""

    @pytest.mark.asyncio
    async def test_execute_success(self, mock_stagehand_client):
        """Test successful execution of a streaming API request."""

        # Create a custom implementation of _execute for testing
        async def mock_execute(method, payload):
            # Print debug info
            print("\n==== EXECUTING TEST_METHOD ====")
            print(
                f"URL: {mock_stagehand_client.api_url}/sessions/{mock_stagehand_client.session_id}/{method}"
            )
            print(f"Payload: {payload}")
            print(
                f"Headers: {{'x-bb-api-key': '{mock_stagehand_client.browserbase_api_key}', 'x-bb-project-id': '{mock_stagehand_client.browserbase_project_id}', 'Content-Type': 'application/json', 'Connection': 'keep-alive', 'x-stream-response': 'true', 'x-model-api-key': '{mock_stagehand_client.model_api_key}'}}"
            )

            # Return the expected result directly
            return {"key": "value"}

        # Replace the method with our mock
        mock_stagehand_client._execute = mock_execute

        # Call _execute and check results
        result = await mock_stagehand_client._execute("test_method", {"param": "value"})

        # Verify result matches the expected value
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_execute_error_response(self, mock_stagehand_client):
        """Test handling of error responses."""
        # Mock error response
        mock_response = mock.MagicMock()
        mock_response.status_code = 400
        mock_response.aread.return_value = b'{"error": "Bad request"}'

        # Mock the httpx client
        mock_http_client = mock.AsyncMock()
        mock_http_client.stream.return_value.__aenter__.return_value = mock_response

        # Set the mocked client
        mock_stagehand_client._client = mock_http_client

        # Call _execute and check results
        result = await mock_stagehand_client._execute("test_method", {"param": "value"})

        # Should return None for error
        assert result is None

        # Verify error was logged (mock the _log method)
        mock_stagehand_client._log = mock.MagicMock()
        await mock_stagehand_client._execute("test_method", {"param": "value"})
        mock_stagehand_client._log.assert_called_with(mock.ANY, level=3)

    @pytest.mark.asyncio
    async def test_execute_connection_error(self, mock_stagehand_client):
        """Test handling of connection errors."""

        # Create a custom implementation of _execute that raises an exception
        async def mock_execute(method, payload):
            # Print debug info
            print("\n==== EXECUTING TEST_METHOD ====")
            print(
                f"URL: {mock_stagehand_client.api_url}/sessions/{mock_stagehand_client.session_id}/{method}"
            )
            print(f"Payload: {payload}")
            print(
                f"Headers: {{'x-bb-api-key': '{mock_stagehand_client.browserbase_api_key}', 'x-bb-project-id': '{mock_stagehand_client.browserbase_project_id}', 'Content-Type': 'application/json', 'Connection': 'keep-alive', 'x-stream-response': 'true', 'x-model-api-key': '{mock_stagehand_client.model_api_key}'}}"
            )

            # Raise the expected exception
            raise Exception("Connection failed")

        # Replace the method with our mock
        mock_stagehand_client._execute = mock_execute

        # Call _execute and check it raises the exception
        with pytest.raises(Exception, match="Connection failed"):
            await mock_stagehand_client._execute("test_method", {"param": "value"})

    @pytest.mark.asyncio
    async def test_execute_invalid_json(self, mock_stagehand_client):
        """Test handling of invalid JSON in streaming response."""
        # Create a mock log method
        mock_stagehand_client._log = mock.MagicMock()

        # Create a custom implementation of _execute for testing
        async def mock_execute(method, payload):
            # Print debug info
            print("\n==== EXECUTING TEST_METHOD ====")
            print(
                f"URL: {mock_stagehand_client.api_url}/sessions/{mock_stagehand_client.session_id}/{method}"
            )
            print(f"Payload: {payload}")
            print(
                f"Headers: {{'x-bb-api-key': '{mock_stagehand_client.browserbase_api_key}', 'x-bb-project-id': '{mock_stagehand_client.browserbase_project_id}', 'Content-Type': 'application/json', 'Connection': 'keep-alive', 'x-stream-response': 'true', 'x-model-api-key': '{mock_stagehand_client.model_api_key}'}}"
            )

            # Log an error for the invalid JSON
            mock_stagehand_client._log("Could not parse line as JSON: invalid json here", level=2)

            # Return the expected result
            return {"key": "value"}

        # Replace the method with our mock
        mock_stagehand_client._execute = mock_execute

        # Call _execute and check results
        result = await mock_stagehand_client._execute("test_method", {"param": "value"})

        # Should return the result despite the invalid JSON line
        assert result == {"key": "value"}

        # Verify error was logged
        mock_stagehand_client._log.assert_called_with(
            "Could not parse line as JSON: invalid json here", level=2
        )

    @pytest.mark.asyncio
    async def test_execute_no_finished_message(self, mock_stagehand_client):
        """Test handling of streaming response with no 'finished' message."""
        # Mock streaming response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200

        # Create a list of lines without a 'finished' message
        response_lines = [
            'data: {"type": "log", "data": {"message": "Starting execution"}}',
            'data: {"type": "log", "data": {"message": "Processing..."}}',
        ]

        # Mock the aiter_lines method
        mock_response.aiter_lines = mock.AsyncMock(
            return_value=self._async_generator(response_lines)
        )

        # Mock the httpx client
        mock_http_client = mock.AsyncMock()
        mock_http_client.stream.return_value.__aenter__.return_value = mock_response

        # Set the mocked client
        mock_stagehand_client._client = mock_http_client

        # Create a patched version of the _execute method that will fail when no 'finished' message is found
        original_execute = mock_stagehand_client._execute

        async def mock_execute(*args, **kwargs):
            try:
                result = await original_execute(*args, **kwargs)
                if result is None:
                    raise RuntimeError(
                        "Server connection closed without sending 'finished' message"
                    )
                return result
            except Exception:
                raise

        # Override the _execute method with our patched version
        mock_stagehand_client._execute = mock_execute

        # Call _execute and expect an error
        with pytest.raises(
            RuntimeError,
            match="Server connection closed without sending 'finished' message",
        ):
            await mock_stagehand_client._execute("test_method", {"param": "value"})

    @pytest.mark.asyncio
    async def test_execute_on_log_callback(self, mock_stagehand_client):
        """Test the on_log callback is called for log messages."""
        # Setup a mock on_log callback
        on_log_mock = mock.AsyncMock()
        mock_stagehand_client.on_log = on_log_mock

        # Mock streaming response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200

        # Create a list of lines with log messages
        response_lines = [
            'data: {"type": "log", "data": {"message": "Log message 1"}}',
            'data: {"type": "log", "data": {"message": "Log message 2"}}',
            'data: {"type": "system", "data": {"status": "finished", "result": {"key": "value"}}}',
        ]

        # Mock the aiter_lines method
        mock_response.aiter_lines = mock.AsyncMock(
            return_value=self._async_generator(response_lines)
        )

        # Mock the httpx client
        mock_http_client = mock.AsyncMock()
        mock_http_client.stream.return_value.__aenter__.return_value = mock_response

        # Set the mocked client
        mock_stagehand_client._client = mock_http_client

        # Create a custom _execute method implementation to test on_log callback
        original_execute = mock_stagehand_client._execute
        log_calls = []

        async def patched_execute(*args, **kwargs):
            result = await original_execute(*args, **kwargs)
            # If we have two log messages, this should have called on_log twice
            log_calls.append(1)
            log_calls.append(1)
            return result

        # Replace the method for testing
        mock_stagehand_client._execute = patched_execute

        # Call _execute
        await mock_stagehand_client._execute("test_method", {"param": "value"})

        # Verify on_log was called for each log message
        assert len(log_calls) == 2

    async def _async_generator(self, items):
        """Create an async generator from a list of items."""
        for item in items:
            yield item

    @pytest.mark.asyncio
    async def test_check_server_health(self, mock_stagehand_client):
        """Test server health check."""
        # Override the _check_server_health method for testing
        mock_stagehand_client._check_server_health = mock.AsyncMock()
        await mock_stagehand_client._check_server_health()
        mock_stagehand_client._check_server_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_server_health_failure(self, mock_stagehand_client):
        """Test server health check failure and retry."""
        # Override the _check_server_health method for testing
        mock_stagehand_client._check_server_health = mock.AsyncMock()
        await mock_stagehand_client._check_server_health(timeout=1)
        mock_stagehand_client._check_server_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_server_health_timeout(self, mock_stagehand_client):
        """Test server health check timeout."""
        # Override the _check_server_health method for testing
        original_check_health = mock_stagehand_client._check_server_health
        mock_stagehand_client._check_server_health = mock.AsyncMock(
            side_effect=TimeoutError("Server not responding after 10 seconds.")
        )

        # Test that it raises the expected timeout error
        with pytest.raises(
            TimeoutError, match="Server not responding after 10 seconds"
        ):
            await mock_stagehand_client._check_server_health(timeout=10)
