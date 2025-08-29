"""
Integration tests for different LLM provider configurations.
Tests that custom API endpoints work correctly with local browser instances.
"""

import pytest
import os
from stagehand import Stagehand, StagehandConfig


class TestLLMProviderIntegration:
    """Integration tests for different LLM provider configurations."""

    @pytest.fixture(scope="class")
    def openai_config(self):
        """Configuration for OpenAI provider testing"""
        return StagehandConfig(
            model_name="gpt-4o-mini",
            model_client_options={
                "api_base": "https://api.openai.com/v1",
                "api_key": os.getenv("OPENAI_API_KEY")
            },
            verbose=1,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture(scope="class")
    def anthropic_config(self):
        """Configuration for Anthropic provider testing"""
        return StagehandConfig(
            model_name="claude-3-haiku-20240307",
            model_client_options={
                "api_base": "https://api.anthropic.com",
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            },
            verbose=1,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture(scope="class")
    def together_config(self):
        """Configuration for Together AI provider testing"""
        return StagehandConfig(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            model_client_options={
                "api_base": "https://api.together.xyz/v1",
                "api_key": os.getenv("TOGETHER_API_KEY")
            },
            verbose=1,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture
    async def stagehand_openai(self, openai_config):
        """Create a Stagehand instance with OpenAI configuration"""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not available")
        stagehand = Stagehand(config=openai_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.fixture
    async def stagehand_anthropic(self, anthropic_config):
        """Create a Stagehand instance with Anthropic configuration"""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not available")
        stagehand = Stagehand(config=anthropic_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.fixture
    async def stagehand_together(self, together_config):
        """Create a Stagehand instance with Together AI configuration"""
        if not os.getenv("TOGETHER_API_KEY"):
            pytest.skip("TOGETHER_API_KEY not available")
        stagehand = Stagehand(config=together_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.openai
    async def test_openai_provider_initialization(self, stagehand_openai):
        """Test that Stagehand initializes correctly with OpenAI provider."""
        stagehand = stagehand_openai
        assert stagehand._initialized is True
        assert stagehand.page is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.openai
    async def test_openai_provider_basic_functionality(self, stagehand_openai):
        """Test basic functionality with OpenAI provider."""
        stagehand = stagehand_openai
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test observe functionality
        observations = await stagehand.page.observe("Find the main heading on the page")
        assert observations is not None
        assert len(observations) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.anthropic
    async def test_anthropic_provider_initialization(self, stagehand_anthropic):
        """Test that Stagehand initializes correctly with Anthropic provider."""
        stagehand = stagehand_anthropic
        assert stagehand._initialized is True
        assert stagehand.page is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.anthropic
    async def test_anthropic_provider_basic_functionality(self, stagehand_anthropic):
        """Test basic functionality with Anthropic provider."""
        stagehand = stagehand_anthropic
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test observe functionality
        observations = await stagehand.page.observe("Find the main heading on the page")
        assert observations is not None
        assert len(observations) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.together
    async def test_together_provider_initialization(self, stagehand_together):
        """Test that Stagehand initializes correctly with Together AI provider."""
        stagehand = stagehand_together
        assert stagehand._initialized is True
        assert stagehand.page is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.together
    async def test_together_provider_basic_functionality(self, stagehand_together):
        """Test basic functionality with Together AI provider."""
        stagehand = stagehand_together
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test observe functionality
        observations = await stagehand.page.observe("Find the main heading on the page")
        assert observations is not None
        assert len(observations) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.config
    async def test_config_validation_for_custom_endpoints(self):
        """Test configuration validation for custom API endpoints."""
        # Test valid configuration
        valid_config = StagehandConfig(
            model_name="gpt-4o-mini",
            model_client_options={
                "api_base": "https://api.openai.com/v1",
                "api_key": "test-key"
            },
            local_browser_launch_options={"headless": True}
        )
        
        # Configuration should be created without errors
        assert valid_config.model_name == "gpt-4o-mini"
        assert valid_config.model_client_options["api_base"] == "https://api.openai.com/v1"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.config
    async def test_fallback_to_default_endpoints(self):
        """Test that system falls back to default endpoints when api_base is not provided."""
        # Test configuration without api_base
        default_config = StagehandConfig(
            model_name="gpt-4o-mini",
            model_api_key="test-key",
            local_browser_launch_options={"headless": True}
        )
        
        # Configuration should be created without errors
        assert default_config.model_name == "gpt-4o-mini"
        assert default_config.model_api_key == "test-key"
        # api_base should be None, allowing system to use defaults
        assert default_config.model_client_options is None or "api_base" not in (default_config.model_client_options or {})

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.config
    async def test_multiple_provider_configurations(self):
        """Test that different provider configurations can be created successfully."""
        # Test Groq configuration
        groq_config = StagehandConfig(
            model_name="llama3-8b-8192",
            model_client_options={
                "api_base": "https://api.groq.com/openai/v1",
                "api_key": "test-groq-key"
            },
            local_browser_launch_options={"headless": True}
        )
        assert groq_config.model_client_options["api_base"] == "https://api.groq.com/openai/v1"
        
        # Test Perplexity configuration
        perplexity_config = StagehandConfig(
            model_name="llama-3.1-sonar-small-128k-online",
            model_client_options={
                "api_base": "https://api.perplexity.ai",
                "api_key": "test-perplexity-key"
            },
            local_browser_launch_options={"headless": True}
        )
        assert perplexity_config.model_client_options["api_base"] == "https://api.perplexity.ai"
        
        # Test local OpenAI-compatible server configuration
        local_config = StagehandConfig(
            model_name="llama-3.2-3b-instruct",
            model_client_options={
                "api_base": "http://localhost:1234/v1",
                "api_key": "not-needed"
            },
            local_browser_launch_options={"headless": True}
        )
        assert local_config.model_client_options["api_base"] == "http://localhost:1234/v1"