import pytest
import pytest_asyncio

from stagehand import Stagehand, StagehandConfig


@pytest_asyncio.fixture(scope="module")
async def stagehand_local():
    """Provide a lightweight Stagehand instance running in LOCAL mode for integration tests."""
    config = StagehandConfig(env="LOCAL", headless=True, verbose=0)
    sh = Stagehand(config=config)
    await sh.init()
    yield sh
    await sh.close()


@pytest.mark.asyncio
async def test_stagehand_local_initialization(stagehand_local):
    """Ensure that Stagehand initializes correctly in LOCAL mode."""
    assert stagehand_local._initialized is True 