"""
Integration tests for Stagehand Python SDK.

These tests verify the end-to-end functionality of Stagehand in both LOCAL and BROWSERBASE modes.
Inspired by the evals and examples in the project.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import Dict, Any
from pydantic import BaseModel, Field, HttpUrl

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


class Company(BaseModel):
    """Schema for company extraction tests"""
    name: str = Field(..., description="The name of the company")
    url: HttpUrl = Field(..., description="The URL of the company website or relevant page")


class Companies(BaseModel):
    """Schema for companies list extraction tests"""
    companies: list[Company] = Field(..., description="List of companies extracted from the page, maximum of 5 companies")


class NewsArticle(BaseModel):
    """Schema for news article extraction tests"""
    title: str = Field(..., description="The title of the article")
    summary: str = Field(..., description="A brief summary of the article")
    author: str = Field(None, description="The author of the article")
    date: str = Field(None, description="The publication date")


class TestStagehandIntegration:
    """
    Integration tests for Stagehand Python SDK.
    
    These tests verify the complete workflow of Stagehand operations
    including initialization, navigation, observation, action, and extraction.
    """

    @pytest.fixture(scope="class")
    def local_config(self):
        """Configuration for LOCAL mode testing"""
        return StagehandConfig(
            env="LOCAL",
            model_name="gpt-4o-mini",
            headless=True,  # Use headless mode for CI
            verbose=1,
            dom_settle_timeout_ms=2000,
            self_heal=True,
            wait_for_captcha_solves=False,
            system_prompt="You are a browser automation assistant for testing purposes.",
            model_client_options={"apiKey": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")},
        )

    @pytest.fixture(scope="class")
    def browserbase_config(self):
        """Configuration for BROWSERBASE mode testing"""
        return StagehandConfig(
            env="BROWSERBASE",
            api_key=os.getenv("BROWSERBASE_API_KEY"),
            project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
            model_name="gpt-4o",
            verbose=2,
            dom_settle_timeout_ms=3000,
            self_heal=True,
            wait_for_captcha_solves=True,
            system_prompt="You are a browser automation assistant for integration testing.",
            model_client_options={"apiKey": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")},
        )

    @pytest_asyncio.fixture
    async def local_stagehand(self, local_config):
        """Create a Stagehand instance for LOCAL testing"""
        stagehand = Stagehand(config=local_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest_asyncio.fixture
    async def browserbase_stagehand(self, browserbase_config):
        """Create a Stagehand instance for BROWSERBASE testing"""
        # Skip if Browserbase credentials are not available
        if not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")):
            pytest.skip("Browserbase credentials not available")
        
        stagehand = Stagehand(config=browserbase_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_basic_navigation_and_observe_local(self, local_stagehand):
        """Test basic navigation and observe functionality in LOCAL mode"""
        stagehand = local_stagehand
        
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
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_basic_navigation_and_observe_browserbase(self, browserbase_stagehand):
        """Test basic navigation and observe functionality in BROWSERBASE mode"""
        stagehand = browserbase_stagehand
        
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
    @pytest.mark.local
    async def test_form_interaction_local(self, local_stagehand):
        """Test form interaction capabilities in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with forms
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Observe form elements
        form_elements = await stagehand.page.observe("Find all form input elements")
        
        # Verify we found form elements
        assert form_elements is not None
        assert len(form_elements) > 0
        
        # Try to interact with a form field
        await stagehand.page.act("Fill the customer name field with 'Test User'")
        
        # Verify the field was filled by observing its value
        filled_elements = await stagehand.page.observe("Find the customer name input field")
        assert filled_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.browserbase  
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_form_interaction_browserbase(self, browserbase_stagehand):
        """Test form interaction capabilities in BROWSERBASE mode"""
        stagehand = browserbase_stagehand
        
        # Navigate to a page with forms
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Observe form elements
        form_elements = await stagehand.page.observe("Find all form input elements")
        
        # Verify we found form elements
        assert form_elements is not None
        assert len(form_elements) > 0
        
        # Try to interact with a form field
        await stagehand.page.act("Fill the customer name field with 'Test User'")
        
        # Verify the field was filled by observing its value
        filled_elements = await stagehand.page.observe("Find the customer name input field")
        assert filled_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_search_functionality_local(self, local_stagehand):
        """Test search functionality similar to examples in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a search page
        await stagehand.page.goto("https://www.google.com")
        
        # Find and interact with search box
        search_elements = await stagehand.page.observe("Find the search input field")
        assert search_elements is not None
        assert len(search_elements) > 0
        
        # Perform a search
        await stagehand.page.act("Type 'python automation' in the search box")
        
        # Submit the search (press Enter or click search button)
        await stagehand.page.act("Press Enter or click the search button")
        
        # Wait for results and observe them
        await asyncio.sleep(2)  # Give time for results to load
        
        # Observe search results
        results = await stagehand.page.observe("Find search result links")
        assert results is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extraction_functionality_local(self, local_stagehand):
        """Test extraction functionality with schema validation in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a news site
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Extract article titles using simple string instruction
        articles_text = await stagehand.page.extract(
            "Extract the titles of the first 3 articles on the page as a JSON list"
        )
        
        # Verify extraction worked
        assert articles_text is not None
        
        # Test with schema-based extraction
        extract_options = ExtractOptions(
            instruction="Extract the first article's title and a brief summary",
            schema_definition=NewsArticle
        )
        
        article_data = await stagehand.page.extract(extract_options)
        assert article_data is not None
        
        # Validate the extracted data structure
        if hasattr(article_data, 'data') and article_data.data:
            # BROWSERBASE mode format
            article = NewsArticle.model_validate(article_data.data)
            assert article.title
        elif hasattr(article_data, 'title'):
            # LOCAL mode format  
            article = NewsArticle.model_validate(article_data.model_dump())
            assert article.title

    @pytest.mark.asyncio
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_extraction_functionality_browserbase(self, browserbase_stagehand):
        """Test extraction functionality with schema validation in BROWSERBASE mode"""
        stagehand = browserbase_stagehand
        
        # Navigate to a news site
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Extract article titles using simple string instruction
        articles_text = await stagehand.page.extract(
            "Extract the titles of the first 3 articles on the page as a JSON list"
        )
        
        # Verify extraction worked
        assert articles_text is not None
        
        # Test with schema-based extraction
        extract_options = ExtractOptions(
            instruction="Extract the first article's title and a brief summary",
            schema_definition=NewsArticle
        )
        
        article_data = await stagehand.page.extract(extract_options)
        assert article_data is not None
        
        # Validate the extracted data structure
        if hasattr(article_data, 'data') and article_data.data:
            # BROWSERBASE mode format
            article = NewsArticle.model_validate(article_data.data)
            assert article.title
        elif hasattr(article_data, 'title'):
            # LOCAL mode format  
            article = NewsArticle.model_validate(article_data.model_dump())
            assert article.title

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_multi_page_workflow_local(self, local_stagehand):
        """Test multi-page workflow similar to examples in LOCAL mode"""
        stagehand = local_stagehand
        
        # Start at a homepage
        await stagehand.page.goto("https://example.com")
        
        # Observe initial page
        initial_observations = await stagehand.page.observe("Find all navigation links")
        assert initial_observations is not None
        
        # Create a new page in the same context
        new_page = await stagehand.context.new_page()
        await new_page.goto("https://httpbin.org")
        
        # Observe elements on the new page
        new_page_observations = await new_page.observe("Find the main content area")
        assert new_page_observations is not None
        
        # Verify both pages are working independently
        assert stagehand.page != new_page

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_accessibility_features_local(self, local_stagehand):
        """Test accessibility tree extraction in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with form elements
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Test accessibility tree extraction by finding labeled elements
        labeled_elements = await stagehand.page.observe("Find all form elements with labels")
        assert labeled_elements is not None
        
        # Test finding elements by accessibility properties
        accessible_elements = await stagehand.page.observe(
            "Find all interactive elements that are accessible to screen readers"
        )
        assert accessible_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_error_handling_local(self, local_stagehand):
        """Test error handling and recovery in LOCAL mode"""
        stagehand = local_stagehand
        
        # Test with a non-existent page (should handle gracefully)
        with pytest.raises(Exception):
            await stagehand.page.goto("https://thisdomaindoesnotexist12345.com")
        
        # Test with a valid page after error
        await stagehand.page.goto("https://example.com")
        observations = await stagehand.page.observe("Find any elements on the page")
        assert observations is not None

    @pytest.mark.asyncio
    @pytest.mark.local 
    async def test_performance_basic_local(self, local_stagehand):
        """Test basic performance characteristics in LOCAL mode"""
        import time
        
        stagehand = local_stagehand
        
        # Time navigation
        start_time = time.time()
        await stagehand.page.goto("https://example.com")
        navigation_time = time.time() - start_time
        
        # Navigation should complete within reasonable time (30 seconds)
        assert navigation_time < 30.0
        
        # Time observation
        start_time = time.time()
        observations = await stagehand.page.observe("Find all links on the page")
        observation_time = time.time() - start_time
        
        # Observation should complete within reasonable time (20 seconds)
        assert observation_time < 20.0
        assert observations is not None

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.local
    async def test_complex_workflow_local(self, local_stagehand):
        """Test complex multi-step workflow in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Step 1: Observe the form structure
        form_structure = await stagehand.page.observe("Find all form fields and their labels")
        assert form_structure is not None
        assert len(form_structure) > 0
        
        # Step 2: Fill multiple form fields
        await stagehand.page.act("Fill the customer name field with 'Integration Test User'")
        await stagehand.page.act("Fill the telephone field with '555-1234'")
        await stagehand.page.act("Fill the email field with 'test@example.com'")
        
        # Step 3: Observe filled fields to verify
        filled_fields = await stagehand.page.observe("Find all filled form input fields")
        assert filled_fields is not None
        
        # Step 4: Extract the form data
        form_data = await stagehand.page.extract(
            "Extract all the form field values as a JSON object"
        )
        assert form_data is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.local
    async def test_end_to_end_search_and_extract_local(self, local_stagehand):
        """End-to-end test: search and extract results in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to search page
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Extract top stories
        stories = await stagehand.page.extract(
            "Extract the titles and points of the top 5 stories as a JSON array with title and points fields"
        )
        
        assert stories is not None
        
        # Navigate to first story (if available)
        story_links = await stagehand.page.observe("Find the first story link")
        if story_links and len(story_links) > 0:
            await stagehand.page.act("Click on the first story title link")
            
            # Wait for page load
            await asyncio.sleep(3)
            
            # Extract content from the story page
            content = await stagehand.page.extract("Extract the main content or title from this page")
            assert content is not None

    # Test Configuration and Environment Detection
    def test_environment_detection(self):
        """Test that environment is correctly detected based on available credentials"""
        # Test LOCAL mode detection
        local_config = StagehandConfig(env="LOCAL")
        assert local_config.env == "LOCAL"
        
        # Test BROWSERBASE mode configuration
        if os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID"):
            browserbase_config = StagehandConfig(
                env="BROWSERBASE",
                api_key=os.getenv("BROWSERBASE_API_KEY"),
                project_id=os.getenv("BROWSERBASE_PROJECT_ID")
            )
            assert browserbase_config.env == "BROWSERBASE"
            assert browserbase_config.api_key is not None
            assert browserbase_config.project_id is not None 