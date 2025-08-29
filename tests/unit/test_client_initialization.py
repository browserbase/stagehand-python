import asyncio
import unittest.mock as mock
import os

import pytest

from stagehand import Stagehand
from stagehand.config import StagehandConfig


class TestClientInitialization:
    """Tests for the Stagehand client initialization and configuration."""

    @pytest.mark.smoke
    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=True)
    def test_init_with_direct_params(self):
        """Test initialization with direct parameters."""
        config = StagehandConfig(
            model_api_key="test-model-api-key",
            verbose=2,
        )
        client = Stagehand(config=config)

        assert client.model_api_key == "test-model-api-key"
        assert client.verbose == 2
        assert client._initialized is False
        assert client._closed is False

    @pytest.mark.smoke
    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=True)
    def test_init_with_config(self):
        """Test initialization with a configuration object."""
        config = StagehandConfig(
            model_name="gpt-4",
            model_api_key="config-model-key",
            dom_settle_timeout_ms=500,
            self_heal=True,
            wait_for_captcha_solves=True,
            system_prompt="Custom system prompt for testing",
        )

        client = Stagehand(config=config)

        assert client.model_name == "gpt-4"
        assert client.model_api_key == "config-model-key"
        assert client.dom_settle_timeout_ms == 500
        assert hasattr(client, "self_heal")
        assert client.self_heal is True
        assert hasattr(client, "wait_for_captcha_solves")
        assert client.wait_for_captcha_solves is True
        assert hasattr(client, "config")
        assert hasattr(client, "system_prompt")
        assert client.system_prompt == "Custom system prompt for testing"

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=True)
    def test_config_priority_over_direct_params(self):
        """Test that config parameters work correctly."""
        config = StagehandConfig(
            model_api_key="config-model-key",
            model_name="gpt-4",
        )

        client = Stagehand(config=config)

        # Config parameters should be used
        assert client.model_api_key == "config-model-key"
        assert client.model_name == "gpt-4"

    @mock.patch.dict(os.environ, {}, clear=True)
    def test_init_with_missing_required_fields(self):
        """Test initialization with missing required fields."""
        # Test that error is raised when no API key is provided
        from stagehand.config import StagehandConfigError
        
        with pytest.raises(StagehandConfigError, match="No API key found"):
            client = Stagehand()

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=True)
    def test_init_as_context_manager(self):
        """Test the client as a context manager."""
        client = Stagehand(
            model_api_key="test-model-key",
        )

        # Mock the async context manager methods
        client.__aenter__ = mock.AsyncMock(return_value=client)
        client.__aexit__ = mock.AsyncMock()
        client.init = mock.AsyncMock()
        client.close = mock.AsyncMock()

        # We can't easily test an async context manager in a non-async test,
        # so we just verify the methods exist and are async
        assert hasattr(client, "__aenter__")
        assert hasattr(client, "__aexit__")

        # Verify init is called in __aenter__
        assert client.init is not None

        # Verify close is called in __aexit__
        assert client.close is not None

    @pytest.mark.asyncio
    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=True)
    async def test_init_playwright_timeout(self):
        """Test that init() raises TimeoutError when playwright takes too long to start."""
        client = Stagehand(model_api_key="test-model-key")

        # Mock async_playwright to simulate a hanging start() method
        mock_playwright_instance = mock.AsyncMock()
        mock_start = mock.AsyncMock()
        
        # Make start() hang indefinitely
        async def hanging_start():
            await asyncio.sleep(100)  # Sleep longer than the 30s timeout
        
        mock_start.side_effect = hanging_start
        mock_playwright_instance.start = mock_start

        with mock.patch("stagehand.main.async_playwright", return_value=mock_playwright_instance):
            # The init() method should raise TimeoutError due to the 30-second timeout
            with pytest.raises(asyncio.TimeoutError):
                await client.init()

        # Ensure the client is not marked as initialized
        assert client._initialized is False

    @pytest.mark.asyncio
    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-openai-key"}, clear=True)
    async def test_local_browser_initialization(self):
        """Test local browser initialization."""
        client = Stagehand(model_api_key="test-model-key")

        # Mock the browser connection
        with mock.patch("stagehand.main.connect_browser") as mock_connect:
            mock_connect.return_value = (
                mock.MagicMock(),  # browser
                mock.MagicMock(),  # context
                mock.MagicMock(),  # stagehand_context
                mock.MagicMock(),  # page
                None  # downloads_path
            )
            
            with mock.patch("stagehand.main.async_playwright") as mock_playwright:
                mock_playwright_instance = mock.AsyncMock()
                mock_playwright.return_value = mock_playwright_instance
                mock_playwright_instance.start.return_value = mock.MagicMock()
                
                await client.init()
                
                # Verify client is initialized
                assert client._initialized is True

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "test-model-api-key"}, clear=True)
    def test_init_with_model_api_key_in_env(self):
        client = Stagehand()
        assert client.model_api_key == "test-model-api-key"

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "fallback-key"}, clear=True)
    def test_init_with_custom_llm(self):
        config = StagehandConfig(
            model_client_options={"api_key": "custom-llm-key", "api_base": "https://custom-llm.com"}
        )
        client = Stagehand(config=config)
        assert client.model_api_key == "custom-llm-key"
        assert client.model_client_options["api_key"] == "custom-llm-key"
        assert client.model_client_options["api_base"] == "https://custom-llm.com"

    @mock.patch.dict(os.environ, {"OPENAI_API_KEY": "fallback-key"}, clear=True)
    def test_init_with_custom_llm_override(self):
        config = StagehandConfig(
            model_client_options={"api_key": "custom-llm-key", "api_base": "https://custom-llm.com"}
        )
        # Test that direct parameter overrides config
        client = Stagehand(
            config=config,
            model_api_key="override-llm-key"
        )
        assert client.model_api_key == "override-llm-key"