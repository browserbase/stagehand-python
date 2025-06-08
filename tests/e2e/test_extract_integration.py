"""
Integration tests for Stagehand extract functionality.

These tests are inspired by the extract evals and test the page.extract() functionality
for extracting structured data from web pages in both LOCAL and BROWSERBASE modes.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


class Article(BaseModel):
    """Schema for article extraction tests"""
    title: str = Field(..., description="The title of the article")
    summary: str = Field(None, description="A brief summary or description of the article")
    author: str = Field(None, description="The author of the article")
    date: str = Field(None, description="The publication date")
    url: HttpUrl = Field(None, description="The URL of the article")


class Articles(BaseModel):
    """Schema for multiple articles extraction"""
    articles: List[Article] = Field(..., description="List of articles extracted from the page")


class PressRelease(BaseModel):
    """Schema for press release extraction tests"""
    title: str = Field(..., description="The title of the press release")
    date: str = Field(..., description="The publication date")
    content: str = Field(..., description="The main content or summary")
    company: str = Field(None, description="The company name")


class SearchResult(BaseModel):
    """Schema for search result extraction"""
    title: str = Field(..., description="The title of the search result")
    url: HttpUrl = Field(..., description="The URL of the search result")
    snippet: str = Field(None, description="The snippet or description")


class FormData(BaseModel):
    """Schema for form data extraction"""
    customer_name: str = Field(None, description="Customer name field value")
    telephone: str = Field(None, description="Telephone field value")
    email: str = Field(None, description="Email field value")
    comments: str = Field(None, description="Comments field value")


class TestExtractIntegration:
    """Integration tests for Stagehand extract functionality"""

    @pytest.fixture(scope="class")
    def local_config(self):
        """Configuration for LOCAL mode testing"""
        return StagehandConfig(
            env="LOCAL",
            model_name="gpt-4o-mini",
            headless=True,
            verbose=1,
            dom_settle_timeout_ms=2000,
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
            headless=False,
            verbose=2,
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
        if not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")):
            pytest.skip("Browserbase credentials not available")
        
        stagehand = Stagehand(config=browserbase_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_news_articles_local(self, local_stagehand):
        """Test extracting news articles similar to extract_news_articles eval in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a news site
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Test simple string-based extraction
        titles_text = await stagehand.page.extract(
            "Extract the titles of the first 5 articles on the page as a JSON array"
        )
        assert titles_text is not None
        
        # Test schema-based extraction
        extract_options = ExtractOptions(
            instruction="Extract the first article's title, summary, and any available metadata",
            schema_definition=Article
        )
        
        article_data = await stagehand.page.extract(extract_options)
        assert article_data is not None
        
        # Validate the extracted data structure
        if hasattr(article_data, 'data') and article_data.data:
            # BROWSERBASE mode format
            article = Article.model_validate(article_data.data)
            assert article.title
        elif hasattr(article_data, 'title'):
            # LOCAL mode format
            article = Article.model_validate(article_data.model_dump())
            assert article.title

    @pytest.mark.asyncio
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_extract_news_articles_browserbase(self, browserbase_stagehand):
        """Test extracting news articles similar to extract_news_articles eval in BROWSERBASE mode"""
        stagehand = browserbase_stagehand
        
        # Navigate to a news site
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Test schema-based extraction
        extract_options = ExtractOptions(
            instruction="Extract the first article's title, summary, and any available metadata",
            schema_definition=Article
        )
        
        article_data = await stagehand.page.extract(extract_options)
        assert article_data is not None
        
        # Validate the extracted data structure
        if hasattr(article_data, 'data') and article_data.data:
            article = Article.model_validate(article_data.data)
            assert article.title

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_multiple_articles_local(self, local_stagehand):
        """Test extracting multiple articles in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a news site
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Extract multiple articles with schema
        extract_options = ExtractOptions(
            instruction="Extract the top 3 articles with their titles and any available metadata",
            schema_definition=Articles
        )
        
        articles_data = await stagehand.page.extract(extract_options)
        assert articles_data is not None
        
        # Validate the extracted data
        if hasattr(articles_data, 'data') and articles_data.data:
            articles = Articles.model_validate(articles_data.data)
            assert len(articles.articles) > 0
            for article in articles.articles:
                assert article.title
        elif hasattr(articles_data, 'articles'):
            articles = Articles.model_validate(articles_data.model_dump())
            assert len(articles.articles) > 0

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_search_results_local(self, local_stagehand):
        """Test extracting search results in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to Google and perform a search
        await stagehand.page.goto("https://www.google.com")
        await stagehand.page.act("Type 'python programming' in the search box")
        await stagehand.page.act("Press Enter")
        
        # Wait for results
        await asyncio.sleep(3)
        
        # Extract search results
        search_results = await stagehand.page.extract(
            "Extract the first 3 search results with their titles, URLs, and snippets as a JSON array"
        )
        
        assert search_results is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_form_data_local(self, local_stagehand):
        """Test extracting form data after filling it in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Fill the form first
        await stagehand.page.act("Fill the customer name field with 'Extract Test User'")
        await stagehand.page.act("Fill the telephone field with '555-EXTRACT'")
        await stagehand.page.act("Fill the email field with 'extract@test.com'")
        await stagehand.page.act("Fill the comments field with 'Testing extraction functionality'")
        
        # Extract the form data
        extract_options = ExtractOptions(
            instruction="Extract all the filled form field values",
            schema_definition=FormData
        )
        
        form_data = await stagehand.page.extract(extract_options)
        assert form_data is not None
        
        # Validate extracted form data
        if hasattr(form_data, 'data') and form_data.data:
            data = FormData.model_validate(form_data.data)
            assert data.customer_name or data.email  # At least one field should be extracted
        elif hasattr(form_data, 'customer_name'):
            data = FormData.model_validate(form_data.model_dump())
            assert data.customer_name or data.email

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_structured_content_local(self, local_stagehand):
        """Test extracting structured content from complex pages in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with structured content
        await stagehand.page.goto("https://httpbin.org")
        
        # Extract page structure information
        page_info = await stagehand.page.extract(
            "Extract the main sections and navigation elements of this page as structured JSON"
        )
        
        assert page_info is not None
        
        # Extract specific elements
        navigation_data = await stagehand.page.extract(
            "Extract all the navigation links with their text and destinations"
        )
        
        assert navigation_data is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_table_data_local(self, local_stagehand):
        """Test extracting tabular data in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with tables (using HTTP status codes page)
        await stagehand.page.goto("https://httpbin.org/status/200")
        
        # Extract any structured data available
        structured_data = await stagehand.page.extract(
            "Extract any structured data, lists, or key-value pairs from this page"
        )
        
        assert structured_data is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_metadata_local(self, local_stagehand):
        """Test extracting page metadata in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with rich metadata
        await stagehand.page.goto("https://example.com")
        
        # Extract page metadata
        metadata = await stagehand.page.extract(
            "Extract the page title, description, and any other metadata"
        )
        
        assert metadata is not None
        
        # Extract specific content
        content_info = await stagehand.page.extract(
            "Extract the main heading and paragraph content from this page"
        )
        
        assert content_info is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_error_handling_local(self, local_stagehand):
        """Test extract error handling in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test extracting non-existent data
        nonexistent_data = await stagehand.page.extract(
            "Extract all purple elephants and unicorns from this page"
        )
        # Should return something (even if empty) rather than crash
        assert nonexistent_data is not None
        
        # Test with very specific schema that might not match
        class ImpossibleSchema(BaseModel):
            unicorn_name: str = Field(..., description="Name of the unicorn")
            magic_level: int = Field(..., description="Level of magic")
        
        try:
            extract_options = ExtractOptions(
                instruction="Extract unicorn information",
                schema_definition=ImpossibleSchema
            )
            impossible_data = await stagehand.page.extract(extract_options)
            # If it doesn't crash, that's acceptable
            assert impossible_data is not None
        except Exception:
            # Expected for impossible schemas
            pass

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_json_validation_local(self, local_stagehand):
        """Test that extracted data validates against schemas in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a content-rich page
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Define a strict schema
        class StrictArticle(BaseModel):
            title: str = Field(..., description="Article title", min_length=1)
            has_content: bool = Field(..., description="Whether the article has visible content")
        
        extract_options = ExtractOptions(
            instruction="Extract the first article with its title and whether it has content",
            schema_definition=StrictArticle
        )
        
        article_data = await stagehand.page.extract(extract_options)
        assert article_data is not None
        
        # Validate against the strict schema
        if hasattr(article_data, 'data') and article_data.data:
            strict_article = StrictArticle.model_validate(article_data.data)
            assert len(strict_article.title) > 0
            assert isinstance(strict_article.has_content, bool)

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.local
    async def test_extract_performance_local(self, local_stagehand):
        """Test extract performance characteristics in LOCAL mode"""
        import time
        stagehand = local_stagehand
        
        # Navigate to a content-rich page
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Time simple extraction
        start_time = time.time()
        simple_extract = await stagehand.page.extract(
            "Extract the titles of the first 3 articles"
        )
        simple_time = time.time() - start_time
        
        assert simple_time < 30.0  # Should complete within 30 seconds
        assert simple_extract is not None
        
        # Time schema-based extraction
        start_time = time.time()
        extract_options = ExtractOptions(
            instruction="Extract the first article with metadata",
            schema_definition=Article
        )
        schema_extract = await stagehand.page.extract(extract_options)
        schema_time = time.time() - start_time
        
        assert schema_time < 45.0  # Schema extraction might take a bit longer
        assert schema_extract is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.local
    async def test_extract_end_to_end_workflow_local(self, local_stagehand):
        """End-to-end test combining actions and extraction in LOCAL mode"""
        stagehand = local_stagehand
        
        # Step 1: Navigate and search
        await stagehand.page.goto("https://www.google.com")
        await stagehand.page.act("Type 'news python programming' in the search box")
        await stagehand.page.act("Press Enter")
        await asyncio.sleep(3)
        
        # Step 2: Extract search results
        search_results = await stagehand.page.extract(
            "Extract the first 3 search results with titles and URLs"
        )
        assert search_results is not None
        
        # Step 3: Navigate to first result (if available)
        first_result = await stagehand.page.observe("Find the first search result link")
        if first_result and len(first_result) > 0:
            await stagehand.page.act("Click on the first search result")
            await asyncio.sleep(3)
            
            # Step 4: Extract content from the result page
            page_content = await stagehand.page.extract(
                "Extract the main title and content summary from this page"
            )
            assert page_content is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_extract_with_text_extract_mode_local(self, local_stagehand):
        """Test extraction with text extract mode in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a content page
        await stagehand.page.goto("https://example.com")
        
        # Test text-based extraction (no schema)
        text_content = await stagehand.page.extract(
            "Extract all the text content from this page as plain text"
        )
        assert text_content is not None
        
        # Test structured text extraction
        structured_text = await stagehand.page.extract(
            "Extract the heading and paragraph text as separate fields in JSON format"
        )
        assert structured_text is not None

    @pytest.mark.asyncio
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_extract_browserbase_specific_features(self, browserbase_stagehand):
        """Test Browserbase-specific extract capabilities"""
        stagehand = browserbase_stagehand
        
        # Navigate to a content-rich page
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Test extraction in Browserbase environment
        extract_options = ExtractOptions(
            instruction="Extract the first 2 articles with all available metadata",
            schema_definition=Articles
        )
        
        articles_data = await stagehand.page.extract(extract_options)
        assert articles_data is not None
        
        # Verify Browserbase session is active
        assert hasattr(stagehand, 'session_id')
        assert stagehand.session_id is not None
        
        # Validate the extracted data structure (Browserbase format)
        if hasattr(articles_data, 'data') and articles_data.data:
            articles = Articles.model_validate(articles_data.data)
            assert len(articles.articles) > 0 