"""
Regression test for wichita functionality.

This test verifies that combination actions (act + extract) work correctly,
based on the TypeScript wichita evaluation.
"""

import os
import pytest
import pytest_asyncio
from pydantic import BaseModel, Field

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


class BidResults(BaseModel):
    """Schema for bid results extraction"""
    total_results: str = Field(..., description="The total number of bids that the search produced")


class TestWichita:
    """Regression test for wichita functionality"""

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
    async def test_wichita_local(self, local_stagehand):
        """
        Regression test: wichita
        
        Mirrors the TypeScript wichita evaluation:
        - Navigate to Wichita Falls TX government bids page
        - Click on "Show Closed/Awarded/Cancelled bids"
        - Extract the total number of bids
        - Verify the count is within expected range (405 ± 10)
        """
        stagehand = local_stagehand
        
        await stagehand.page.goto("https://www.wichitafallstx.gov/Bids.aspx")
        
        # Click to show closed/awarded/cancelled bids
        await stagehand.page.act('Click on "Show Closed/Awarded/Cancelled bids"')
        
        # Extract the total number of results using proper Python schema-based extraction
        extract_options = ExtractOptions(
            instruction="Extract the total number of bids that the search produced.",
            schema_definition=BidResults
        )
        
        result = await stagehand.page.extract(extract_options)
        #TODO - how to unify the extract result handling between LOCAL and BROWSERBASE?

        # Handle result based on the mode (LOCAL returns data directly, BROWSERBASE returns ExtractResult)
        if hasattr(result, 'data') and result.data:
            # BROWSERBASE mode format
            bid_data = BidResults.model_validate(result.data)
            total_results = bid_data.total_results
        elif hasattr(result, 'total_results'):
            # LOCAL mode format - result is the Pydantic model instance
            total_results = result.total_results
        else:
            # Fallback - try to get total_results from the result directly
            total_results = getattr(result, 'total_results', str(result))
        
        # Parse the number from the result
        expected_number = 405
        extracted_number = int(''.join(filter(str.isdigit, total_results)))
        
        # Check if the number is within expected range (±10)
        is_within_range = (
            extracted_number >= expected_number - 10 and
            extracted_number <= expected_number + 10
        )
        
        assert is_within_range, (
            f"Total number of results {extracted_number} is not within the expected range "
            f"{expected_number} ± 10"
        )

    @pytest.mark.asyncio
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_wichita_browserbase(self, browserbase_stagehand):
        """
        Regression test: wichita (Browserbase)
        
        Same test as local but running in Browserbase environment.
        """
        stagehand = browserbase_stagehand
        
        await stagehand.page.goto("https://www.wichitafallstx.gov/Bids.aspx")
        
        # Click to show closed/awarded/cancelled bids
        await stagehand.page.act('Click on "Show Closed/Awarded/Cancelled bids"')
        
        # Extract the total number of results using proper Python schema-based extraction
        extract_options = ExtractOptions(
            instruction="Extract the total number of bids that the search produced.",
            schema_definition=BidResults
        )
        
        result = await stagehand.page.extract(extract_options)
        
        #TODO - how to unify the extract result handling between LOCAL and BROWSERBASE?
        
        # Handle result based on the mode (LOCAL returns data directly, BROWSERBASE returns ExtractResult)
        if hasattr(result, 'data') and result.data:
            # BROWSERBASE mode format
            bid_data = BidResults.model_validate(result.data)
            total_results = bid_data.total_results
        elif hasattr(result, 'total_results'):
            # LOCAL mode format - result is the Pydantic model instance
            total_results = result.total_results
        else:
            # Fallback - try to get total_results from the result directly
            total_results = getattr(result, 'total_results', str(result))
        
        # Parse the number from the result
        expected_number = 405
        extracted_number = int(''.join(filter(str.isdigit, total_results)))
        
        # Check if the number is within expected range (±10)
        is_within_range = (
            extracted_number >= expected_number - 10 and
            extracted_number <= expected_number + 10
        )
        
        assert is_within_range, (
            f"Total number of results {extracted_number} is not within the expected range "
            f"{expected_number} ± 10"
        ) 