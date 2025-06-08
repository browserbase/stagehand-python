"""
Integration tests for Stagehand act functionality.

These tests are inspired by the act evals and test the page.act() functionality
for performing actions and interactions in both LOCAL and BROWSERBASE modes.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import List, Dict, Any

from stagehand import Stagehand, StagehandConfig


class TestActIntegration:
    """Integration tests for Stagehand act functionality"""

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
    async def test_form_filling_local(self, local_stagehand):
        """Test form filling capabilities similar to act_form_filling eval in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Fill various form fields
        await stagehand.page.act("Fill the customer name field with 'John Doe'")
        await stagehand.page.act("Fill the telephone field with '555-0123'")
        await stagehand.page.act("Fill the email field with 'john@example.com'")
        
        # Verify fields were filled by observing their values
        filled_name = await stagehand.page.observe("Find the customer name input field")
        assert filled_name is not None
        assert len(filled_name) > 0
        
        # Test dropdown/select interaction
        await stagehand.page.act("Select 'Large' from the size dropdown")
        
        # Test checkbox interaction
        await stagehand.page.act("Check the 'I accept the terms' checkbox")

    @pytest.mark.asyncio
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_form_filling_browserbase(self, browserbase_stagehand):
        """Test form filling capabilities similar to act_form_filling eval in BROWSERBASE mode"""
        stagehand = browserbase_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Fill various form fields
        await stagehand.page.act("Fill the customer name field with 'Jane Smith'")
        await stagehand.page.act("Fill the telephone field with '555-0456'")
        await stagehand.page.act("Fill the email field with 'jane@example.com'")
        
        # Verify fields were filled
        filled_name = await stagehand.page.observe("Find the customer name input field")
        assert filled_name is not None
        assert len(filled_name) > 0

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_button_clicking_local(self, local_stagehand):
        """Test button clicking functionality in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with buttons
        await stagehand.page.goto("https://httpbin.org")
        
        # Test clicking various button types
        # Find and click a navigation button/link
        buttons = await stagehand.page.observe("Find all clickable buttons or links")
        assert buttons is not None
        
        if buttons and len(buttons) > 0:
            # Try clicking the first button found
            await stagehand.page.act("Click the first button or link on the page")
            
            # Wait for any page changes
            await asyncio.sleep(2)
            
            # Verify we're still on a valid page
            new_elements = await stagehand.page.observe("Find any elements on the current page")
            assert new_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_navigation_actions_local(self, local_stagehand):
        """Test navigation actions in LOCAL mode"""
        stagehand = local_stagehand
        
        # Start at example.com
        await stagehand.page.goto("https://example.com")
        
        # Test link clicking for navigation
        links = await stagehand.page.observe("Find all links on the page")
        
        if links and len(links) > 0:
            # Click on a link to navigate
            await stagehand.page.act("Click on the 'More information...' link")
            await asyncio.sleep(2)
            
            # Verify navigation occurred
            current_elements = await stagehand.page.observe("Find the main content on this page")
            assert current_elements is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_search_workflow_local(self, local_stagehand):
        """Test search workflow similar to google_jobs eval in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to Google
        await stagehand.page.goto("https://www.google.com")
        
        # Perform search actions
        await stagehand.page.act("Type 'python programming' in the search box")
        await stagehand.page.act("Press Enter to search")
        
        # Wait for results
        await asyncio.sleep(3)
        
        # Verify search results appeared
        results = await stagehand.page.observe("Find search result links")
        assert results is not None
        
        # Test interacting with search results
        if results and len(results) > 0:
            await stagehand.page.act("Click on the first search result")
            await asyncio.sleep(2)
            
            # Verify we navigated to a result page
            content = await stagehand.page.observe("Find the main content of this page")
            assert content is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_text_input_actions_local(self, local_stagehand):
        """Test various text input actions in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Test different text input scenarios
        await stagehand.page.act("Clear the customer name field and type 'Test User'")
        await stagehand.page.act("Fill the comments field with 'This is a test comment with special characters: @#$%'")
        
        # Test text modification actions
        await stagehand.page.act("Select all text in the comments field")
        await stagehand.page.act("Type 'Replaced text' to replace the selected text")
        
        # Verify text actions worked
        filled_fields = await stagehand.page.observe("Find all filled form fields")
        assert filled_fields is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_keyboard_actions_local(self, local_stagehand):
        """Test keyboard actions in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to Google for keyboard testing
        await stagehand.page.goto("https://www.google.com")
        
        # Test various keyboard actions
        await stagehand.page.act("Click on the search box")
        await stagehand.page.act("Type 'hello world'")
        await stagehand.page.act("Press Ctrl+A to select all")
        await stagehand.page.act("Press Delete to clear the field")
        await stagehand.page.act("Type 'new search term'")
        await stagehand.page.act("Press Enter")
        
        # Wait for search results
        await asyncio.sleep(3)
        
        # Verify keyboard actions resulted in search
        results = await stagehand.page.observe("Find search results")
        assert results is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_mouse_actions_local(self, local_stagehand):
        """Test mouse actions in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a page with various clickable elements
        await stagehand.page.goto("https://httpbin.org")
        
        # Test different mouse actions
        await stagehand.page.act("Right-click on the main heading")
        await stagehand.page.act("Click outside the page to dismiss any context menu")
        await stagehand.page.act("Double-click on the main heading")
        
        # Test hover actions
        links = await stagehand.page.observe("Find all links on the page")
        if links and len(links) > 0:
            await stagehand.page.act("Hover over the first link")
            await asyncio.sleep(1)
            await stagehand.page.act("Click the hovered link")
            await asyncio.sleep(2)

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_complex_form_workflow_local(self, local_stagehand):
        """Test complex form workflow in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a comprehensive form
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Complete multi-step form filling
        await stagehand.page.act("Fill the customer name field with 'Integration Test User'")
        await stagehand.page.act("Fill the telephone field with '+1-555-123-4567'")
        await stagehand.page.act("Fill the email field with 'integration.test@example.com'")
        await stagehand.page.act("Select 'Medium' from the size dropdown if available")
        await stagehand.page.act("Fill the comments field with 'This is an automated integration test submission'")
        
        # Submit the form
        await stagehand.page.act("Click the Submit button")
        
        # Wait for submission and verify
        await asyncio.sleep(3)
        
        # Check if form was submitted (page changed or success message)
        result_content = await stagehand.page.observe("Find any confirmation or result content")
        assert result_content is not None

    @pytest.mark.asyncio
    @pytest.mark.local
    async def test_error_recovery_local(self, local_stagehand):
        """Test error recovery in act operations in LOCAL mode"""
        stagehand = local_stagehand
        
        # Navigate to a simple page
        await stagehand.page.goto("https://example.com")
        
        # Test acting on non-existent elements (should handle gracefully)
        try:
            await stagehand.page.act("Click the non-existent button with id 'impossible-button-12345'")
            # If it doesn't raise an exception, that's also acceptable
        except Exception:
            # Expected for non-existent elements
            pass
        
        # Verify page is still functional after error
        elements = await stagehand.page.observe("Find any elements on the page")
        assert elements is not None
        
        # Test successful action after failed attempt
        await stagehand.page.act("Click on the main heading of the page")

    @pytest.mark.asyncio
    @pytest.mark.slow
    @pytest.mark.local
    async def test_performance_multiple_actions_local(self, local_stagehand):
        """Test performance of multiple sequential actions in LOCAL mode"""
        import time
        stagehand = local_stagehand
        
        # Navigate to a form page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Time multiple actions
        start_time = time.time()
        
        await stagehand.page.act("Fill the customer name field with 'Speed Test'")
        await stagehand.page.act("Fill the telephone field with '555-SPEED'")
        await stagehand.page.act("Fill the email field with 'speed@test.com'")
        await stagehand.page.act("Click in the comments field")
        await stagehand.page.act("Type 'Performance testing in progress'")
        
        total_time = time.time() - start_time
        
        # Multiple actions should complete within reasonable time
        assert total_time < 120.0  # 2 minutes for 5 actions
        
        # Verify all actions were successful
        filled_fields = await stagehand.page.observe("Find all filled form fields")
        assert filled_fields is not None
        assert len(filled_fields) > 0

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.local
    async def test_end_to_end_user_journey_local(self, local_stagehand):
        """End-to-end test simulating complete user journey in LOCAL mode"""
        stagehand = local_stagehand
        
        # Step 1: Start at homepage
        await stagehand.page.goto("https://httpbin.org")
        
        # Step 2: Navigate to forms section
        await stagehand.page.act("Click on any link that leads to forms or testing")
        await asyncio.sleep(2)
        
        # Step 3: Fill out a form completely
        forms = await stagehand.page.observe("Find any form elements")
        if forms and len(forms) > 0:
            # Navigate to forms page if not already there
            await stagehand.page.goto("https://httpbin.org/forms/post")
            
            # Complete the form
            await stagehand.page.act("Fill the customer name field with 'E2E Test User'")
            await stagehand.page.act("Fill the telephone field with '555-E2E-TEST'")
            await stagehand.page.act("Fill the email field with 'e2e@test.com'")
            await stagehand.page.act("Fill the comments with 'End-to-end integration test'")
            
            # Submit the form
            await stagehand.page.act("Click the Submit button")
            await asyncio.sleep(3)
            
            # Verify successful completion
            result = await stagehand.page.observe("Find any result or confirmation content")
            assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.browserbase
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_browserbase_specific_actions(self, browserbase_stagehand):
        """Test Browserbase-specific action capabilities"""
        stagehand = browserbase_stagehand
        
        # Navigate to a page
        await stagehand.page.goto("https://httpbin.org/forms/post")
        
        # Test actions in Browserbase environment
        await stagehand.page.act("Fill the customer name field with 'Browserbase Test'")
        await stagehand.page.act("Fill the email field with 'browserbase@test.com'")
        
        # Verify actions worked
        filled_fields = await stagehand.page.observe("Find filled form fields")
        assert filled_fields is not None
        
        # Verify Browserbase session is active
        assert hasattr(stagehand, 'session_id')
        assert stagehand.session_id is not None 