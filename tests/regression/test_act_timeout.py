"""
Regression test for act timeout functionality.

This test verifies that the timeout mechanism works correctly for act operations,
based on the TypeScript expect_act_timeout evaluation.
"""

import os
import pytest
import pytest_asyncio

from stagehand import Stagehand, StagehandConfig


class TestActTimeout:
    """Regression test for act timeout functionality"""

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
    @pytest.mark.regression
    @pytest.mark.local
    async def test_expect_act_timeout_local(self, local_stagehand):
        """
        Regression test: expect_act_timeout
        
        Mirrors the TypeScript expect_act_timeout evaluation:
        - Navigate to docs.stagehand.dev
        - Attempt action with 1 second timeout
        - Expect the action to fail due to timeout
        """
        stagehand = local_stagehand
        
        await stagehand.page.goto("https://docs.stagehand.dev")
        
        result = await stagehand.page.act(
            "Click the button with id 'nonexistent-button-that-will-never-exist-12345'",
            timeout_ms=1000  # 1 second timeout
        )
        
        # Test passes if the action failed (due to timeout or element not found)
        # This mirrors the TypeScript: _success: !result.success
        assert not result.success, "Action should have failed due to timeout or missing element"

    @pytest.mark.asyncio
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_expect_act_timeout_browserbase(self, browserbase_stagehand):
        """
        Regression test: expect_act_timeout (Browserbase)
        
        Same test as local but running in Browserbase environment.
        """
        stagehand = browserbase_stagehand
        
        await stagehand.page.goto("https://docs.stagehand.dev")
        
        result = await stagehand.page.act(
            "Click the button with id 'nonexistent-button-that-will-never-exist-12345'",
            timeout_ms=1000  # 1 second timeout
        )
        
        # Test passes if the action failed (due to timeout or element not found)
        assert not result.success, "Action should have failed due to timeout or missing element" 