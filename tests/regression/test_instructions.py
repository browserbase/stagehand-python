"""
Regression test for instructions functionality.

This test verifies that special instruction actions work correctly,
based on the TypeScript instructions evaluation.
"""

import os
import pytest
import pytest_asyncio

from stagehand import Stagehand, StagehandConfig


class TestInstructions:
    """Regression test for instructions functionality"""

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
    async def test_instructions_local(self, local_stagehand):
        """
        Regression test: instructions
        
        Mirrors the TypeScript instructions evaluation:
        - Navigate to docs.browserbase.com
        - Perform special action with "secret12345"
        - Verify correct navigation to introduction page
        """
        stagehand = local_stagehand
        
        await stagehand.page.goto("https://docs.browserbase.com/")
        
        result = await stagehand.page.act("secret12345")
        
        # Wait for page to settle after the action
        await stagehand.page.wait_for_load_state("domcontentloaded")
        
        current_url = stagehand.page.url
        expected_url = "https://docs.browserbase.com/introduction/what-is-browserbase"
        
        # Test passes if we navigated to the correct URL
        assert current_url == expected_url, f"Expected URL {expected_url}, but got {current_url}"

    @pytest.mark.asyncio
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_instructions_browserbase(self, browserbase_stagehand):
        """
        Regression test: instructions (Browserbase)
        
        Same test as local but running in Browserbase environment.
        """
        stagehand = browserbase_stagehand
        
        await stagehand.page.goto("https://docs.browserbase.com/")
        
        result = await stagehand.page.act("secret12345")
        
        # Wait for page to settle after the action
        await stagehand.page.wait_for_load_state("domcontentloaded")
        
        current_url = stagehand.page.url
        expected_url = "https://docs.browserbase.com/introduction/what-is-browserbase"
        
        # Test passes if we navigated to the correct URL
        assert current_url == expected_url, f"Expected URL {expected_url}, but got {current_url}" 