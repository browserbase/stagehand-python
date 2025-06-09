import pytest
import pytest_asyncio
import os

from stagehand import Stagehand, StagehandConfig


class TestStagehandLocalIntegration:
    """Integration tests for Stagehand Python SDK in LOCAL mode."""

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
            model_client_options={"apiKey": os.getenv("MODEL_API_KEY")},
        )

    @pytest_asyncio.fixture
    async def stagehand_local(self, local_config):
        """Create a Stagehand instance for LOCAL testing"""
        stagehand = Stagehand(config=local_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_stagehand_local_initialization(self, stagehand_local):
        """Ensure that Stagehand initializes correctly in LOCAL mode."""
        assert stagehand_local._initialized is True

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_observe_and_act_workflow(self, stagehand_local):
        """Test core observe and act workflow in LOCAL mode - extracted from e2e tests."""
        stagehand = stagehand_local
        
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
        await stagehand.page.act("Fill the customer name field with 'Local Integration Test'")
        await stagehand.page.act("Fill the telephone field with '555-LOCAL'")
        await stagehand.page.act("Fill the email field with 'local@integration.test'")
        
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
    @pytest.mark.local
    async def test_local_basic_navigation_and_observe(self, stagehand_local):
        """Test basic navigation and observe functionality in LOCAL mode"""
        stagehand = stagehand_local
        
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
    @pytest.mark.local
    async def test_local_extraction_functionality(self, stagehand_local):
        """Test extraction functionality in LOCAL mode"""
        stagehand = stagehand_local
        
        # Navigate to a content-rich page
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Extract article titles using simple string instruction
        articles_text = await stagehand.page.extract(
            "Extract the titles of the first 3 articles on the page as a JSON list"
        )
        
        # Verify extraction worked
        assert articles_text is not None 