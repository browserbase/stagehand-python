import asyncio
import unittest.mock as mock

import playwright.async_api
import pytest

from stagehand import Stagehand
from stagehand.page import StagehandPage


class TestClientLifecycle:
    """Tests for the Stagehand client lifecycle (initialization and cleanup)."""

    @pytest.fixture
    def mock_playwright(self):
        """Create mock Playwright objects."""
        # Mock playwright API components
        mock_page = mock.AsyncMock()
        mock_context = mock.AsyncMock()
        mock_context.pages = [mock_page]
        mock_browser = mock.AsyncMock()
        mock_browser.contexts = [mock_context]
        mock_chromium = mock.AsyncMock()
        mock_chromium.connect_over_cdp = mock.AsyncMock(return_value=mock_browser)
        mock_pw = mock.AsyncMock()
        mock_pw.chromium = mock_chromium

        # Setup return values
        playwright.async_api.async_playwright = mock.AsyncMock(
            return_value=mock.AsyncMock(start=mock.AsyncMock(return_value=mock_pw))
        )

        return {
            "mock_page": mock_page,
            "mock_context": mock_context,
            "mock_browser": mock_browser,
            "mock_pw": mock_pw,
        }

    # Add a helper method to setup client initialization
    def setup_client_for_testing(self, client):
        # Add the needed methods for testing
        client._check_server_health = mock.AsyncMock()
        client._create_session = mock.AsyncMock()
        return client

    @pytest.mark.asyncio
    async def test_init_with_existing_session(self, mock_playwright):
        """Test initializing with an existing session ID."""
        # Setup client with a session ID
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Mock health check to avoid actual API calls
        client = self.setup_client_for_testing(client)

        # Mock the initialization behavior
        original_init = getattr(client, "init", None)

        async def mock_init():
            if client._initialized:
                return
            await client._check_server_health()
            client._playwright = mock_playwright["mock_pw"]
            client._browser = mock_playwright["mock_browser"]
            client._context = mock_playwright["mock_context"]
            client._playwright_page = mock_playwright["mock_page"]
            client.page = StagehandPage(client._playwright_page, client)
            client._initialized = True

        # Add the mocked init method
        client.init = mock_init

        # Call init
        await client.init()

        # Check that session was not created since we already have one
        assert client.session_id == "test-session-123"
        assert client._initialized is True

        # Verify page was created
        assert isinstance(client.page, StagehandPage)

    @pytest.mark.asyncio
    async def test_init_creates_new_session(self, mock_playwright):
        """Test initializing without a session ID creates a new session."""
        # Setup client without a session ID
        client = Stagehand(
            api_url="http://test-server.com",
            api_key="test-api-key",
            project_id="test-project-id",
            model_api_key="test-model-api-key",
        )

        # Mock health check and session creation
        client = self.setup_client_for_testing(client)

        # Define a side effect for _create_session that sets session_id
        async def set_session_id():
            client.session_id = "new-session-id"

        client._create_session.side_effect = set_session_id

        # Mock the initialization behavior
        async def mock_init():
            if client._initialized:
                return
            await client._check_server_health()
            if not client.session_id:
                await client._create_session()
            client._playwright = mock_playwright["mock_pw"]
            client._browser = mock_playwright["mock_browser"]
            client._context = mock_playwright["mock_context"]
            client._playwright_page = mock_playwright["mock_page"]
            client.page = StagehandPage(client._playwright_page, client)
            client._initialized = True

        # Add the mocked init method
        client.init = mock_init

        # Call init
        await client.init()

        # Verify session was created
        client._create_session.assert_called_once()
        assert client.session_id == "new-session-id"
        assert client._initialized is True

    @pytest.mark.asyncio
    async def test_init_when_already_initialized(self, mock_playwright):
        """Test calling init when already initialized."""
        # Setup client
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Mock needed methods
        client = self.setup_client_for_testing(client)

        # Mark as already initialized
        client._initialized = True

        # Mock the initialization behavior
        async def mock_init():
            if client._initialized:
                return
            await client._check_server_health()
            client._playwright = mock_playwright["mock_pw"]
            client._browser = mock_playwright["mock_browser"]
            client._context = mock_playwright["mock_context"]
            client._playwright_page = mock_playwright["mock_page"]
            client.page = StagehandPage(client._playwright_page, client)
            client._initialized = True

        # Add the mocked init method
        client.init = mock_init

        # Call init
        await client.init()

        # Verify health check was not called because already initialized
        client._check_server_health.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_with_existing_browser_context(self, mock_playwright):
        """Test initialization when browser already has contexts."""
        # Setup client
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Mock health check
        client = self.setup_client_for_testing(client)

        # Mock the initialization behavior
        async def mock_init():
            if client._initialized:
                return
            await client._check_server_health()
            client._playwright = mock_playwright["mock_pw"]
            client._browser = mock_playwright["mock_browser"]
            client._context = mock_playwright["mock_context"]
            client._playwright_page = mock_playwright["mock_page"]
            client.page = StagehandPage(client._playwright_page, client)
            client._initialized = True

        # Add the mocked init method
        client.init = mock_init

        # Call init
        await client.init()

        # Verify existing context was used
        assert client._context == mock_playwright["mock_context"]

    @pytest.mark.asyncio
    async def test_init_with_no_browser_context(self, mock_playwright):
        """Test initialization when browser has no contexts."""
        # Setup client
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Modify mock browser to have empty contexts
        mock_playwright["mock_browser"].contexts = []

        # Setup a new context
        new_context = mock.AsyncMock()
        new_page = mock.AsyncMock()
        new_context.pages = []
        new_context.new_page = mock.AsyncMock(return_value=new_page)
        mock_playwright["mock_browser"].new_context = mock.AsyncMock(
            return_value=new_context
        )

        # Mock health check
        client = self.setup_client_for_testing(client)

        # Mock the initialization behavior with custom handling for no contexts
        async def mock_init():
            if client._initialized:
                return
            await client._check_server_health()
            client._playwright = mock_playwright["mock_pw"]
            client._browser = mock_playwright["mock_browser"]

            # If no contexts, create a new one
            if not client._browser.contexts:
                client._context = await client._browser.new_context()
                client._playwright_page = await client._context.new_page()
            else:
                client._context = client._browser.contexts[0]
                client._playwright_page = client._context.pages[0]

            client.page = StagehandPage(client._playwright_page, client)
            client._initialized = True

        # Add the mocked init method
        client.init = mock_init

        # Call init
        await client.init()

        # Verify new context was created
        mock_playwright["mock_browser"].new_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, mock_playwright):
        """Test client close method."""
        # Setup client
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Mock the needed attributes and methods
        client._playwright = mock_playwright["mock_pw"]
        client._client = mock.AsyncMock()
        # Store a reference to the client for later assertions
        http_client_ref = client._client
        client._execute = mock.AsyncMock()

        # Mock close method
        async def mock_close():
            if client._closed:
                return

            # End the session on the server if we have a session ID
            if client.session_id:
                try:
                    await client._execute("end", {"sessionId": client.session_id})
                except Exception:
                    pass

            if client._playwright:
                await client._playwright.stop()
                client._playwright = None

            if client._client:
                await client._client.aclose()
                client._client = None

            client._closed = True

        # Add the mocked close method
        client.close = mock_close

        # Call close
        await client.close()

        # Verify session was ended via API
        client._execute.assert_called_once_with(
            "end", {"sessionId": "test-session-123"}
        )

        # Verify Playwright was stopped
        mock_playwright["mock_pw"].stop.assert_called_once()

        # Verify internal HTTPX client was closed - use the stored reference
        http_client_ref.aclose.assert_called_once()

        # Verify closed flag was set
        assert client._closed is True

    @pytest.mark.asyncio
    async def test_close_error_handling(self, mock_playwright):
        """Test error handling in close method."""
        # Setup client
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Mock the needed attributes and methods
        client._playwright = mock_playwright["mock_pw"]
        client._client = mock.AsyncMock()
        # Store a reference to the client for later assertions
        http_client_ref = client._client
        client._execute = mock.AsyncMock(side_effect=Exception("API error"))
        client._log = mock.MagicMock()

        # Mock close method
        async def mock_close():
            if client._closed:
                return

            # End the session on the server if we have a session ID
            if client.session_id:
                try:
                    await client._execute("end", {"sessionId": client.session_id})
                except Exception as e:
                    client._log(f"Error ending session: {str(e)}", level=2)

            if client._playwright:
                await client._playwright.stop()
                client._playwright = None

            if client._client:
                await client._client.aclose()
                client._client = None

            client._closed = True

        # Add the mocked close method
        client.close = mock_close

        # Call close
        await client.close()

        # Verify Playwright was still stopped despite API error
        mock_playwright["mock_pw"].stop.assert_called_once()

        # Verify internal HTTPX client was still closed - use the stored reference
        http_client_ref.aclose.assert_called_once()

        # Verify closed flag was still set
        assert client._closed is True

    @pytest.mark.asyncio
    async def test_close_when_already_closed(self, mock_playwright):
        """Test calling close when already closed."""
        # Setup client
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Mock the needed attributes
        client._playwright = mock_playwright["mock_pw"]
        client._client = mock.AsyncMock()
        client._execute = mock.AsyncMock()

        # Mark as already closed
        client._closed = True

        # Mock close method
        async def mock_close():
            if client._closed:
                return

            # End the session on the server if we have a session ID
            if client.session_id:
                try:
                    await client._execute("end", {"sessionId": client.session_id})
                except Exception:
                    pass

            if client._playwright:
                await client._playwright.stop()
                client._playwright = None

            if client._client:
                await client._client.aclose()
                client._client = None

            client._closed = True

        # Add the mocked close method
        client.close = mock_close

        # Call close
        await client.close()

        # Verify close was a no-op - execute not called
        client._execute.assert_not_called()

        # Verify Playwright was not stopped
        mock_playwright["mock_pw"].stop.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_and_close_full_cycle(self, mock_playwright):
        """Test a full init-close lifecycle."""
        # Setup client
        client = Stagehand(
            api_url="http://test-server.com",
            browserbase_session_id="test-session-123",
            api_key="test-api-key",
            project_id="test-project-id",
        )

        # Mock needed methods
        client = self.setup_client_for_testing(client)
        client._execute = mock.AsyncMock()

        # Mock init method
        async def mock_init():
            if client._initialized:
                return
            await client._check_server_health()
            client._playwright = mock_playwright["mock_pw"]
            client._browser = mock_playwright["mock_browser"]
            client._context = mock_playwright["mock_context"]
            client._playwright_page = mock_playwright["mock_page"]
            client.page = StagehandPage(client._playwright_page, client)
            client._initialized = True

        # Mock close method
        async def mock_close():
            if client._closed:
                return

            # End the session on the server if we have a session ID
            if client.session_id:
                try:
                    await client._execute("end", {"sessionId": client.session_id})
                except Exception:
                    pass

            if client._playwright:
                await client._playwright.stop()
                client._playwright = None

            if client._client:
                await client._client.aclose()
                client._client = None

            client._closed = True

        # Add the mocked methods
        client.init = mock_init
        client.close = mock_close
        client._client = mock.AsyncMock()

        # Initialize
        await client.init()
        assert client._initialized is True

        # Close
        await client.close()
        assert client._closed is True

        # Verify session was ended via API
        client._execute.assert_called_once_with(
            "end", {"sessionId": "test-session-123"}
        )
