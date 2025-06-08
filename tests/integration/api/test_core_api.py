import os

import pytest
import pytest_asyncio
from pydantic import BaseModel, Field

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


skip_if_no_creds = pytest.mark.skipif(
    not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
    reason="Browserbase credentials are not available for API integration tests",
)


class Article(BaseModel):
    """Schema for article extraction tests"""
    title: str = Field(..., description="The title of the article")
    summary: str = Field(None, description="A brief summary or description of the article")


@pytest_asyncio.fixture(scope="module")
@skip_if_no_creds
async def stagehand_api():
    """Provide a lightweight Stagehand instance pointing to the Browserbase API."""
    config = StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        headless=True,
        verbose=0,
    )
    sh = Stagehand(config=config)
    await sh.init()
    yield sh
    await sh.close()


@skip_if_no_creds
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_stagehand_api_initialization(stagehand_api):
    """Ensure that Stagehand initializes correctly against the Browserbase API."""
    assert stagehand_api.session_id is not None


@skip_if_no_creds
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_api_extract_functionality(stagehand_api):
    """Test core extract functionality in API mode - extracted from e2e tests."""
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