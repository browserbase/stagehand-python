import os

import pytest
from pydantic import BaseModel, Field

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


class Article(BaseModel):
    """Schema for article extraction tests"""
    title: str = Field(..., description="The title of the article")
    summary: str = Field(None, description="A brief summary or description of the article")


class TestStagehandIntegration:
    """Integration tests for Stagehand Python SDK with local browser and custom LLM providers"""

    @pytest.fixture(scope="class")
    def local_test_config(self):
        """Configuration for local mode testing with OpenAI"""
        return StagehandConfig(
            model_name="gpt-4o-mini",
            model_api_key=os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"),
            verbose=2,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture(scope="class")
    def custom_llm_config(self):
        """Configuration for testing custom LLM endpoints"""
        return StagehandConfig(
            model_name="gpt-4o-mini",
            model_client_options={
                "api_base": "https://api.openai.com/v1",
                "api_key": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
            },
            verbose=2,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture(scope="class") 
    def anthropic_config(self):
        """Configuration for testing Anthropic-compatible endpoints"""
        return StagehandConfig(
            model_name="claude-3-haiku-20240307",
            model_client_options={
                "api_base": "https://api.anthropic.com",
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            },
            verbose=2,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture
    async def stagehand_local(self, local_test_config):
        """Create a Stagehand instance for local testing"""
        stagehand = Stagehand(config=local_test_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.fixture
    async def stagehand_custom_llm(self, custom_llm_config):
        """Create a Stagehand instance with custom LLM endpoint"""
        stagehand = Stagehand(config=custom_llm_config)
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

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_stagehand_local_initialization(self, stagehand_local):
        """Ensure that Stagehand initializes correctly in local mode."""
        assert stagehand_local.page is not None
        assert stagehand_local._initialized is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_observe_and_act_workflow(self, stagehand_local):
        """Test core observe and act workflow in local mode."""
        stagehand = stagehand_local
        
        # Navigate to a form page for testing
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Test OBSERVE primitive: Find form elements
        form_elements = await stagehand.page.observe("Find all form input elements")
        
        # Verify observations
        assert form_elements is not None
        assert len(form_elements) > 0
        
        # Verify observation structure
        for obs in form_elements:
            assert hasattr(obs, "selector")
            assert obs.selector  # Not empty
        
        # Test ACT primitive: Fill form fields
        await stagehand.page.act("Fill the customer name field with 'Integration Test'")
        await stagehand.page.act("Fill the telephone field with '555-TEST'")
        await stagehand.page.act("Fill the email field with 'test@integration.local'")
        
        # Verify actions worked by observing filled fields
        filled_fields = await stagehand.page.observe("Find all filled form input fields")
        assert filled_fields is not None
        assert len(filled_fields) > 0
        
        # Test interaction with specific elements
        customer_field = await stagehand.page.observe("Find the customer name input field")
        assert customer_field is not None
        assert len(customer_field) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_basic_navigation_and_observe(self, stagehand_local):
        """Test basic navigation and observe functionality in local mode."""
        stagehand = stagehand_local
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Observe elements on the page
        observations = await stagehand.page.observe("Find all the links on the page")
        
        # Verify we got some observations
        assert observations is not None
        assert len(observations) > 0
        
        # Verify observation structure
        for obs in observations:
            assert hasattr(obs, "selector")
            assert obs.selector  # Not empty

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_extraction_functionality(self, stagehand_local):
        """Test extraction functionality in local mode."""
        stagehand = stagehand_local
        
        # Navigate to a content-rich page
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Test simple text-based extraction
        titles_text = await stagehand.page.extract(
            "Extract the titles of the first 3 articles on the page as a JSON array"
        )
        
        # Verify extraction worked
        assert titles_text is not None
        
        # Test schema-based extraction
        extract_options = ExtractOptions(
            instruction="Extract the first article's title and any available summary",
            schema_definition=Article
        )
        
        article_data = await stagehand.page.extract(extract_options)
        assert article_data is not None
        
        # Validate the extracted data structure (local mode format)
        if hasattr(article_data, 'title'):
            # Direct format
            article = Article.model_validate(article_data.model_dump())
            assert article.title
            assert len(article.title) > 0
        else:
            # Fallback validation
            assert article_data is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.custom_llm
    async def test_custom_llm_endpoint_functionality(self, stagehand_custom_llm):
        """Test functionality with custom LLM endpoint configuration."""
        stagehand = stagehand_custom_llm
        
        # Verify initialization with custom endpoint
        assert stagehand.page is not None
        assert stagehand._initialized is True
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test basic observe functionality with custom LLM
        observations = await stagehand.page.observe("Find the main heading on the page")
        
        # Verify observations work with custom endpoint
        assert observations is not None
        assert len(observations) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.anthropic
    async def test_anthropic_endpoint_functionality(self, stagehand_anthropic):
        """Test functionality with Anthropic-compatible endpoint."""
        stagehand = stagehand_anthropic
        
        # Verify initialization with Anthropic endpoint
        assert stagehand.page is not None
        assert stagehand._initialized is True
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test basic observe functionality with Anthropic
        observations = await stagehand.page.observe("Find the main heading on the page")
        
        # Verify observations work with Anthropic endpoint
        assert observations is not None
        assert len(observations) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_multiple_llm_providers_configuration(self):
        """Test that different LLM provider configurations work correctly."""
        # Test OpenAI configuration
        openai_config = StagehandConfig(
            model_name="gpt-4o-mini",
            model_client_options={
                "api_base": "https://api.openai.com/v1",
                "api_key": os.getenv("OPENAI_API_KEY")
            },
            local_browser_launch_options={"headless": True}
        )
        
        if os.getenv("OPENAI_API_KEY"):
            stagehand_openai = Stagehand(config=openai_config)
            await stagehand_openai.init()
            assert stagehand_openai._initialized is True
            await stagehand_openai.close()
        
        # Test Together AI configuration (if available)
        together_config = StagehandConfig(
            model_name="meta-llama/Llama-2-7b-chat-hf",
            model_client_options={
                "api_base": "https://api.together.xyz/v1",
                "api_key": os.getenv("TOGETHER_API_KEY")
            },
            local_browser_launch_options={"headless": True}
        )
        
        if os.getenv("TOGETHER_API_KEY"):
            stagehand_together = Stagehand(config=together_config)
            await stagehand_together.init()
            assert stagehand_together._initialized is True
            await stagehand_together.close()

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_browser_configuration_options(self):
        """Test that different browser configuration options work correctly."""
        # Test with different viewport sizes
        viewport_config = StagehandConfig(
            model_name="gpt-4o-mini",
            model_api_key=os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"),
            local_browser_launch_options={
                "headless": True,
                "viewport": {"width": 1920, "height": 1080}
            }
        )
        
        if os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"):
            stagehand = Stagehand(config=viewport_config)
            await stagehand.init()
            assert stagehand._initialized is True
            
            # Navigate to test the viewport
            await stagehand.page.goto("https://example.com")
            
            # Verify the page loaded
            current_url = stagehand.page.url
            assert "example.com" in current_url
            
            await stagehand.close()

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_error_handling_with_invalid_llm_config(self):
        """Test error handling with invalid LLM configurations."""
        # Test with invalid API base URL
        invalid_config = StagehandConfig(
            model_name="gpt-4o-mini",
            model_client_options={
                "api_base": "https://invalid-api-endpoint.com/v1",
                "api_key": "invalid-key"
            },
            local_browser_launch_options={"headless": True}
        )
        
        # Should be able to initialize (browser connection should work)
        stagehand = Stagehand(config=invalid_config)
        await stagehand.init()
        assert stagehand._initialized is True
        
        # Navigate to a page (this should work)
        await stagehand.page.goto("https://example.com")
        
        # LLM operations might fail, but browser operations should work
        # We won't test LLM operations here as they would fail with invalid config
        
        await stagehand.close() 