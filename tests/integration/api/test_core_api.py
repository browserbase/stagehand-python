import os

import pytest
import pytest_asyncio

from stagehand import Stagehand, StagehandConfig


skip_if_no_creds = pytest.mark.skipif(
    not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
    reason="Browserbase credentials are not available for API integration tests",
)


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