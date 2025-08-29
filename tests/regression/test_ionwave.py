"""
Regression test for ionwave functionality.

This test verifies that navigation actions work correctly by clicking on links,
based on the TypeScript ionwave evaluation.
"""

import os
import pytest
import pytest_asyncio

from stagehand import Stagehand, StagehandConfig


class TestIonwave:
    """Regression test for ionwave functionality"""

    @pytest.fixture(scope="class")
    def local_config(self):
        """Configuration for LOCAL mode testing"""
        return StagehandConfig(
            model_name="gpt-4o-mini",
            model_api_key=os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"),
            verbose=1,
            dom_settle_timeout_ms=2000,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture(scope="class")
    def local_test_config(self):
        """Configuration for local mode testing"""
        return StagehandConfig(
            model_name="gpt-4o-mini",
            model_api_key=os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"),
            verbose=2,
            local_browser_launch_options={"headless": True},
        )

    @pytest_asyncio.fixture
    async def local_stagehand(self, local_config):
        """Create a Stagehand instance for LOCAL testing"""
        stagehand = Stagehand(config=local_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest_asyncio.fixture
    async def local_test_stagehand(self, local_test_config):
        """Create a Stagehand instance for local testing"""
        stagehand = Stagehand(config=local_test_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.mark.asyncio
    @pytest.mark.regression
    @pytest.mark.local
    async def test_ionwave_local(self, local_stagehand):
        """
        Regression test: ionwave
        
        Mirrors the TypeScript ionwave evaluation:
        - Navigate to ionwave test site
        - Click on "Closed Bids" link
        - Verify navigation to closed-bids.html page
        """
        stagehand = local_stagehand
        
        await stagehand.page.goto("https://browserbase.github.io/stagehand-eval-sites/sites/ionwave/")
        
        result = await stagehand.page.act('Click on "Closed Bids"')
        
        current_url = stagehand.page.url
        expected_url = "https://browserbase.github.io/stagehand-eval-sites/sites/ionwave/closed-bids.html"
        
        # Test passes if we successfully navigated to the expected URL
        assert current_url.startswith(expected_url), f"Expected URL to start with {expected_url}, but got {current_url}"

    @pytest.mark.asyncio
    @pytest.mark.regression
    @pytest.mark.local
    async def test_ionwave_local_alt(self, local_test_stagehand):
        """
        Regression test: ionwave (local alternative)
        
        Same test as the main local test but using alternative configuration.
        """
        stagehand = local_test_stagehand
        
        await stagehand.page.goto("https://browserbase.github.io/stagehand-eval-sites/sites/ionwave/")
        
        result = await stagehand.page.act('Click on "Closed Bids"')
        
        current_url = stagehand.page.url
        expected_url = "https://browserbase.github.io/stagehand-eval-sites/sites/ionwave/closed-bids.html"
        
        # Test passes if we successfully navigated to the expected URL
        assert current_url.startswith(expected_url), f"Expected URL to start with {expected_url}, but got {current_url}" 