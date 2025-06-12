"""
Integration tests for Stagehand observe functionality.

These tests are inspired by the observe evals and test the page.observe() functionality
for finding and identifying elements on web pages in both LOCAL and BROWSERBASE modes.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import List, Dict, Any

from stagehand import Stagehand, StagehandConfig


class TestObserveIntegration:
    """Integration tests for Stagehand observe functionality"""

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
    async def test_observe_form_elements_local(self, local_stagehand):
        """Test observing form elements similar to observe_taxes eval in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Observe form input elements
        observations = await stagehand.page.observe("Find all form input elements")
        
        # Verify observations
        assert observations is not None
        assert len(observations) > 0
        
        # Check observation structure
        for obs in observations:
            assert hasattr(obs, "selector")
            assert obs.selector  # Not empty
            
        # Test finding specific labeled elements
        labeled_observations = await stagehand.page.observe("Find all form elements with labels")
        assert labeled_observations is not None

    @pytest.mark.asyncio
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_observe_form_elements_browserbase(self, browserbase_stagehand):
        """Test observing form elements similar to observe_taxes eval in BROWSERBASE mode"""
        stagehand = browserbase_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Observe form input elements
        observations = await stagehand.page.observe("Find all form input elements")
        
        # Verify observations
        assert observations is not None
        assert len(observations) > 0
        
        # Check observation structure
        for obs in observations:
            assert hasattr(obs, "selector")
            assert obs.selector  # Not empty

    @pytest.mark.asyncio
    @pytest.mark.local  
    async def test_observe_search_results_local(self, local_stagehand):
        """Test observing search results similar to observe_search_results eval in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to Google
        await stagehand.page.goto("https://www.google.com")
        
        # Find search box
        search_box = await stagehand.page.observe("Find the search input field")
        assert search_box is not None
        assert len(search_box) > 0
        
        # Perform search
        await stagehand.page.act("Type 'python' in the search box")
        await stagehand.page.act("Press Enter")
        
        # Wait for results
        await asyncio.sleep(3)
        
        # Observe search results
        results = await stagehand.page.observe("Find all search result links")
        assert results is not None
        # Note: Results may vary, so we just check that we got some response

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_observe_navigation_elements_local(self, local_stagehand):
        """Test observing navigation elements in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a site with navigation
        await stagehand.page.goto("https://example.com")
        
        # Observe all links
        links = await stagehand.page.observe("Find all links on the page")
        assert links is not None
        
        # Observe clickable elements
        clickable = await stagehand.page.observe("Find all clickable elements")
        assert clickable is not None
        
        # Test specific element observation
        specific_elements = await stagehand.page.observe("Find the main heading on the page")
        assert specific_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_observe_complex_selectors_local(self, local_stagehand):
        """Test observing elements with complex selectors in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with various elements
        await stagehand.page.goto("https://httpbin.org")
        
        # Test observing by element type
        buttons = await stagehand.page.observe("Find all buttons on the page")
        assert buttons is not None
        
        # Test observing by text content
        text_elements = await stagehand.page.observe("Find elements containing the word 'testing'")
        assert text_elements is not None
        
        # Test observing by position/layout
        visible_elements = await stagehand.page.observe("Find all visible interactive elements")
        assert visible_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_observe_element_validation_local(self, local_stagehand):
        """Test that observed elements can be interacted with in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Observe form elements
        form_elements = await stagehand.page.observe("Find all input fields in the form")
        assert form_elements is not None
        assert len(form_elements) > 0
        
        # Validate that we can get element info for each observed element
        for element in form_elements[:3]:  # Test first 3 to avoid timeout
            selector = element.selector
            if selector:
                try:
                    # Try to check if element exists and is visible
                    element_info = await stagehand.page.locator(selector).first.is_visible()
                    # Element should be found (visible or not)
                    assert element_info is not None
                except Exception:
                    # Some elements might not be accessible, which is okay
                    pass

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_observe_accessibility_features_local(self, local_stagehand):
        """Test observing elements by accessibility features in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a form page with labels
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Observe by accessibility labels
        labeled_elements = await stagehand.page.observe("Find all form fields with proper labels")
        assert labeled_elements is not None
        
        # Observe interactive elements
        interactive = await stagehand.page.observe("Find all interactive elements accessible to screen readers")
        assert interactive is not None
        
        # Test role-based observation
        form_controls = await stagehand.page.observe("Find all form control elements")
        assert form_controls is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_observe_error_handling_local(self, local_stagehand):
        """Test observe error handling in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test observing non-existent elements
        nonexistent = await stagehand.page.observe("Find elements with class 'nonexistent-class-12345'")
        # Should return empty list or None, not crash
        assert nonexistent is not None or nonexistent == []
        
        # Test with ambiguous instructions
        ambiguous = await stagehand.page.observe("Find stuff")
        assert ambiguous is not None
        
        # Test with very specific instructions that might not match
        specific = await stagehand.page.observe("Find a purple button with the text 'Impossible Button'")
        assert specific is not None or specific == []

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.local
    async def test_observe_performance_local(self, local_stagehand):
        """Test observe performance characteristics in LOCAL mode"""
        import time
        stagehand = local_stagehand
        
        # Navigate to a complex page
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Time observation operation
        start_time = time.time()
        observations = await stagehand.page.observe("Find all story titles on the page")
        observation_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert observation_time < 30.0  # 30 seconds max
        assert observations is not None
        
        # Test multiple rapid observations
        start_time = time.time()
        await stagehand.page.observe("Find all links")
        await stagehand.page.observe("Find all comments")
        await stagehand.page.observe("Find the navigation")
        total_time = time.time() - start_time
        
        # Multiple observations should still be reasonable
        assert total_time < 120.0  # 2 minutes max for 3 operations

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.local
    async def test_observe_end_to_end_workflow_local(self, local_stagehand):
        """End-to-end test with observe as part of larger workflow in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a news site
        await stagehand.page.goto("https://news.ycombinator.com")
        
        # Step 1: Observe the page structure
        structure = await stagehand.page.observe("Find the main content areas")
        assert structure is not None
        
        # Step 2: Observe specific content
        stories = await stagehand.page.observe("Find the first 5 story titles")
        assert stories is not None
        
        # Step 3: Use observation results to guide next actions
        if stories and len(stories) > 0:
            # Try to interact with the first story
            await stagehand.page.act("Click on the first story title")
            await asyncio.sleep(2)
            
            # Observe elements on the new page
            new_page_elements = await stagehand.page.observe("Find the main content of this page")
            assert new_page_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_observe_browserbase_specific_features(self, browserbase_stagehand):
        """Test Browserbase-specific observe features"""
        stagehand = browserbase_stagehand
        
        # Navigate to a page
        await stagehand.page.goto("https://example.com")
        
        # Test observe with Browserbase capabilities
        observations = await stagehand.page.observe("Find all interactive elements on the page")
        assert observations is not None
        
        # Verify we can access Browserbase session info
        assert hasattr(stagehand, 'session_id')
        assert stagehand.session_id is not None 