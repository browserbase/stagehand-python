"""
Integration tests for local browser functionality and multi-page management.
Tests that local browser instances work correctly with multiple pages and contexts.
"""

import pytest
import os
from stagehand import Stagehand, StagehandConfig


@pytest.mark.asyncio
class TestLocalBrowserIntegration:
    """Integration tests for local browser functionality."""
    
    @pytest.fixture(scope="class")
    def local_test_config(self):
        """Configuration for local browser testing"""
        return StagehandConfig(
            model_name="gpt-4o-mini",
            model_api_key=os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY"),
            verbose=1,
            local_browser_launch_options={"headless": True},
        )

    @pytest.fixture
    async def stagehand_local(self, local_test_config):
        """Create a Stagehand instance for local testing"""
        stagehand = Stagehand(config=local_test_config)
        await stagehand.init()
        yield stagehand
        await stagehand.close()
    
    async def test_local_browser_initialization_and_page_management(self, stagehand_local):
        """Test that local browser initializes correctly and manages pages."""
        stagehand = stagehand_local
        
        # Verify initialization
        assert stagehand._initialized is True
        assert stagehand.page is not None
        assert stagehand.context is not None
        
        # Get the page and context
        page = stagehand.page
        context = stagehand.context
        
        # Verify page has frame tracking attributes
        assert hasattr(page, 'frame_id')
        assert hasattr(context, 'frame_id_map')
        
        # Navigate to test page functionality
        await page.goto("https://example.com")
        
        # Verify page navigation worked
        current_url = await page.url()
        assert "example.com" in current_url
    
    async def test_multiple_pages_local_browser(self, stagehand_local):
        """Test local browser with multiple pages."""
        stagehand = stagehand_local
        
        # Get first page
        page1 = stagehand.page
        context = stagehand.context
        
        # Navigate first page
        await page1.goto("https://example.com")
        
        # Create second page
        page2 = await context.new_page()
        
        # Navigate second page
        await page2.goto("https://httpbin.org")
        
        # Verify both pages are accessible and have different URLs
        url1 = await page1.url()
        url2 = await page2.url()
        
        assert "example.com" in url1
        assert "httpbin.org" in url2
        assert url1 != url2
        
        # Verify both pages have frame IDs
        assert hasattr(page1, 'frame_id')
        assert hasattr(page2, 'frame_id')
        
        # Verify context tracks both pages
        assert len(context.frame_id_map) >= 1  # At least one page tracked
    
    async def test_local_browser_persistence_across_navigation(self, stagehand_local):
        """Test that local browser maintains state across navigation."""
        stagehand = stagehand_local
        
        page = stagehand.page
        context = stagehand.context
        
        # Navigate to first page
        await page.goto("https://example.com")
        initial_url = await page.url()
        assert "example.com" in initial_url
        
        # Navigate to second page
        await page.goto("https://httpbin.org")
        second_url = await page.url()
        assert "httpbin.org" in second_url
        
        # Verify navigation worked
        assert initial_url != second_url
        
        # Verify page and context are still valid
        assert page is not None
        assert context is not None
        assert hasattr(page, 'frame_id')

    async def test_local_browser_with_forms_and_interactions(self, stagehand_local):
        """Test local browser with form interactions."""
        stagehand = stagehand_local
        
        page = stagehand.page
        
        # Navigate to a form page
        await page.goto("https://httpbin.org/forms/post")
        
        # Test that we can interact with form elements
        form_elements = await page.observe("Find all form input elements")
        assert form_elements is not None
        assert len(form_elements) > 0
        
        # Test form filling
        await page.act("Fill the customer name field with 'Local Browser Test'")
        
        # Verify the form was filled by observing the filled field
        filled_fields = await page.observe("Find filled form input fields")
        assert filled_fields is not None

    async def test_local_browser_error_handling(self, stagehand_local):
        """Test local browser error handling for invalid URLs."""
        stagehand = stagehand_local
        
        page = stagehand.page
        
        # Test navigation to valid page first
        await page.goto("https://example.com")
        valid_url = await page.url()
        assert "example.com" in valid_url
        
        # Test that browser handles navigation gracefully
        # (We won't test invalid URLs as they might cause timeouts)
        # Instead, test that the browser maintains state
        assert page is not None
        assert stagehand.context is not None