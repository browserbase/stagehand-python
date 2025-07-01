import os

import pytest
import pytest_asyncio
from pydantic import BaseModel, Field

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


class Article(BaseModel):
    """Schema for article extraction tests"""
    title: str = Field(..., description="The title of the article")
    summary: str = Field(None, description="A brief summary or description of the article")


class TestStagehandAPIIntegration:
    """Integration tests for Stagehand Python SDK in BROWSERBASE API mode"""

    @pytest.fixture(scope="class")
    def browserbase_config(self):
        """Configuration for BROWSERBASE mode testing"""
        return StagehandConfig(
            env="BROWSERBASE",
            api_key=os.getenv("BROWSERBASE_API_KEY"),
            project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
            model_name="gpt-4o",
            headless=False,
            verbose=2,
            model_client_options={"apiKey": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")},
        )

    @pytest_asyncio.fixture
    async def stagehand_api(self, browserbase_config):
        """Create a Stagehand instance for BROWSERBASE API testing"""
        if not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")):
            pytest.skip("Browserbase credentials not available")
        
        stagehand = Stagehand(config=browserbase_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials are not available for API integration tests",
    )
    async def test_stagehand_api_initialization(self, stagehand_api):
        """Ensure that Stagehand initializes correctly against the Browserbase API."""
        assert stagehand_api.session_id is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials are not available for API integration tests",
    )
    async def test_api_observe_and_act_workflow(self, stagehand_api):
        """Test core observe and act workflow in API mode - replicated from local tests."""
        stagehand = stagehand_api
        
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
        await stagehand.page.act("Fill the customer name field with 'API Integration Test'")
        await stagehand.page.act("Fill the telephone field with '555-API'")
        await stagehand.page.act("Fill the email field with 'api@integration.test'")
        
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
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials are not available for API integration tests",
    )
    async def test_api_basic_navigation_and_observe(self, stagehand_api):
        """Test basic navigation and observe functionality in API mode - replicated from local tests."""
        stagehand = stagehand_api
        
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
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials are not available for API integration tests",
    )
    async def test_api_extraction_functionality(self, stagehand_api):
        """Test extraction functionality in API mode - replicated from local tests."""
        stagehand = stagehand_api
        
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
        
        # Validate the extracted data structure (Browserbase format)
        if hasattr(article_data, 'data') and article_data.data:
            # BROWSERBASE mode format
            article = Article.model_validate(article_data.data)
            assert article.title
            assert len(article.title) > 0
        elif hasattr(article_data, 'title'):
            # Fallback format
            article = Article.model_validate(article_data.model_dump())
            assert article.title
            assert len(article.title) > 0
        
        # Verify API session is active
        assert stagehand.session_id is not None 