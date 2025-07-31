"""
Regression test for extract_aigrant_companies functionality.

This test verifies that data extraction works correctly by extracting
companies that received AI grants along with their batch numbers,
based on the TypeScript extract_aigrant_companies evaluation.
"""

import os
import pytest
import pytest_asyncio
from pydantic import BaseModel, Field
from typing import List

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ExtractOptions


class Company(BaseModel):
    company: str = Field(..., description="The name of the company")
    batch: str = Field(..., description="The batch number of the grant")


class Companies(BaseModel):
    companies: List[Company] = Field(..., description="List of companies that received AI grants")


class TestExtractAigrantCompanies:
    """Regression test for extract_aigrant_companies functionality"""

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
    async def test_extract_aigrant_companies_local(self, local_stagehand):
        """
        Regression test: extract_aigrant_companies
        
        Mirrors the TypeScript extract_aigrant_companies evaluation:
        - Navigate to AI grant companies test site
        - Extract all companies that received AI grants with their batch numbers
        - Verify total count is 91
        - Verify first company is "Goodfire" in batch "4"
        - Verify last company is "Forefront" in batch "1"
        """
        stagehand = local_stagehand
        
        await stagehand.page.goto("https://browserbase.github.io/stagehand-eval-sites/sites/aigrant/")
        
        # Extract all companies with their batch numbers
        extract_options = ExtractOptions(
            instruction=(
                "Extract all companies that received the AI grant and group them with their "
                "batch numbers as an array of objects. Each object should contain the company "
                "name and its corresponding batch number."
            ),
            schema_definition=Companies
        )
        
        result = await stagehand.page.extract(extract_options)
        
        # Both LOCAL and BROWSERBASE modes return the Pydantic model instance directly
        companies = result.companies
        
        # Verify total count
        expected_length = 91
        assert len(companies) == expected_length, (
            f"Expected {expected_length} companies, but got {len(companies)}"
        )
        
        # Verify first company
        expected_first_item = {
            "company": "Goodfire",
            "batch": "4"
        }
        assert len(companies) > 0, "No companies were extracted"
        first_company = companies[0]
        assert first_company.company == expected_first_item["company"], (
            f"Expected first company to be '{expected_first_item['company']}', "
            f"but got '{first_company.company}'"
        )
        assert first_company.batch == expected_first_item["batch"], (
            f"Expected first company batch to be '{expected_first_item['batch']}', "
            f"but got '{first_company.batch}'"
        )
        
        # Verify last company
        expected_last_item = {
            "company": "Forefront",
            "batch": "1"
        }
        last_company = companies[-1]
        assert last_company.company == expected_last_item["company"], (
            f"Expected last company to be '{expected_last_item['company']}', "
            f"but got '{last_company.company}'"
        )
        assert last_company.batch == expected_last_item["batch"], (
            f"Expected last company batch to be '{expected_last_item['batch']}', "
            f"but got '{last_company.batch}'"
        )

    @pytest.mark.asyncio
    @pytest.mark.regression
    @pytest.mark.api
    @pytest.mark.skipif(
        not (os.getenv("BROWSERBASE_API_KEY") and os.getenv("BROWSERBASE_PROJECT_ID")),
        reason="Browserbase credentials not available"
    )
    async def test_extract_aigrant_companies_browserbase(self, browserbase_stagehand):
        """
        Regression test: extract_aigrant_companies (Browserbase)
        
        Same test as local but running in Browserbase environment.
        """
        stagehand = browserbase_stagehand
        
        await stagehand.page.goto("https://browserbase.github.io/stagehand-eval-sites/sites/aigrant/")
        
        # Extract all companies with their batch numbers
        extract_options = ExtractOptions(
            instruction=(
                "Extract all companies that received the AI grant and group them with their "
                "batch numbers as an array of objects. Each object should contain the company "
                "name and its corresponding batch number."
            ),
            schema_definition=Companies
        )
        
        result = await stagehand.page.extract(extract_options)
        
        # Both LOCAL and BROWSERBASE modes return the Pydantic model instance directly
        companies = result.companies
        
        # Verify total count
        expected_length = 91
        assert len(companies) == expected_length, (
            f"Expected {expected_length} companies, but got {len(companies)}"
        )
        
        # Verify first company
        expected_first_item = {
            "company": "Goodfire",
            "batch": "4"
        }
        assert len(companies) > 0, "No companies were extracted"
        first_company = companies[0]
        assert first_company.company == expected_first_item["company"], (
            f"Expected first company to be '{expected_first_item['company']}', "
            f"but got '{first_company.company}'"
        )
        assert first_company.batch == expected_first_item["batch"], (
            f"Expected first company batch to be '{expected_first_item['batch']}', "
            f"but got '{first_company.batch}'"
        )
        
        # Verify last company
        expected_last_item = {
            "company": "Forefront",
            "batch": "1"
        }
        last_company = companies[-1]
        assert last_company.company == expected_last_item["company"], (
            f"Expected last company to be '{expected_last_item['company']}', "
            f"but got '{last_company.company}'"
        )
        assert last_company.batch == expected_last_item["batch"], (
            f"Expected last company batch to be '{expected_last_item['batch']}', "
            f"but got '{last_company.batch}'"
        ) 