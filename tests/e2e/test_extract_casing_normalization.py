"""
E2E tests to ensure extract returns validate into snake_case Pydantic schemas
for both LOCAL and BROWSERBASE environments, covering API responses that may
use camelCase keys.
"""

import os
import pytest
import pytest_asyncio
from urllib.parse import urlparse
from pydantic import BaseModel, Field, HttpUrl

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


class Company(BaseModel):
    company_name: str = Field(..., description="The name of the company")
    company_url: HttpUrl = Field(..., description="The URL of the company website or relevant page")


class Companies(BaseModel):
    companies: list[Company] = Field(..., description="List of companies extracted from the page")


@pytest.fixture(scope="class")
def local_config():
    return StagehandConfig(
        env="LOCAL",
        model_name="gpt-4o-mini",
        headless=True,
        verbose=1,
        dom_settle_timeout_ms=2000,
        model_client_options={
            "apiKey": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
        },
    )


@pytest.fixture(scope="class")
def browserbase_config():
    return StagehandConfig(
        env="BROWSERBASE",
        api_key=os.getenv("BROWSERBASE_API_KEY"),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
        model_name="gpt-4o",
        headless=False,
        verbose=2,
        dom_settle_timeout_ms=3000,
        model_client_options={
            "apiKey": os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
        },
    )


@pytest_asyncio.fixture
async def local_stagehand(local_config):
    stagehand = Stagehand(config=local_config)
    await stagehand.init()
    yield stagehand
    await stagehand.close()


@pytest_asyncio.fixture
async def browserbase_stagehand(browserbase_config):
    if not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")):
        pytest.skip("Browserbase credentials not available")
    stagehand = Stagehand(config=browserbase_config)
    await stagehand.init()
    yield stagehand
    await stagehand.close()


@pytest.mark.asyncio
@pytest.mark.local
async def test_extract_companies_casing_local(local_stagehand):
    stagehand = local_stagehand
    # Use stable eval site for consistency
    await stagehand.page.goto("https://browserbase.github.io/stagehand-eval-sites/sites/aigrant/")

    extract_options = ExtractOptions(
        instruction="Extract the names and URLs of up to 5 companies in batch 3",
        schema_definition=Companies,
    )

    result = await stagehand.page.extract(extract_options)

    # Should be validated into our snake_case Pydantic model
    assert isinstance(result, Companies)
    assert 0 < len(result.companies) <= 5
    for c in result.companies:
        assert isinstance(c.company_name, str) and c.company_name
        # Avoid isinstance checks with Pydantic's Annotated types; validate via parsing
        parsed = urlparse(str(c.company_url))
        assert parsed.scheme in ("http", "https") and bool(parsed.netloc)


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.skipif(
    not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
    reason="Browserbase credentials not available",
)
async def test_extract_companies_casing_browserbase(browserbase_stagehand):
    stagehand = browserbase_stagehand
    # Use stable eval site for consistency
    await stagehand.page.goto("https://browserbase.github.io/stagehand-eval-sites/sites/aigrant/")

    extract_options = ExtractOptions(
        instruction="Extract the names and URLs of up to 5 companies in batch 3",
        schema_definition=Companies,
    )

    result = await stagehand.page.extract(extract_options)

    # Should be validated into our snake_case Pydantic model even if API returns camelCase
    assert isinstance(result, Companies)
    assert 0 < len(result.companies) <= 5
    for c in result.companies:
        assert isinstance(c.company_name, str) and c.company_name
        parsed = urlparse(str(c.company_url))
        assert parsed.scheme in ("http", "https") and bool(parsed.netloc)


