import asyncio
import os
import sys
from pathlib import Path

# Add the local stagehand directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from stagehand.main import Stagehand
from stagehand.config import StagehandConfig

# Load environment variables
load_dotenv()

# Define Pydantic models for structured data extraction
class Company(BaseModel):
    name: str = Field(..., description="Company name")
    description: str = Field(..., description="Brief company description")

class Companies(BaseModel):
    companies: list[Company] = Field(..., description="List of companies")
    
async def main():
    # Create configuration for local browser automation with custom LLM endpoint
    config = StagehandConfig(
        model_name="qwen-turbo",  # Use Alibaba DashScope model for demo
        model_client_options={
            "api_base": os.getenv("ALIBABA_ENDPOINT", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "api_key": os.getenv("ALIBABA_API_KEY"),
            "timeout": 30
        },
        verbose=1,
        local_browser_launch_options={
            "headless": False,  # Set to True for headless mode
            "viewport": {"width": 1280, "height": 720}
        }
    )
    
    async with Stagehand(config=config) as stagehand:
        print("\nInitializing 🤘 Stagehand with local browser...")
        
        # Validate LLM configuration
        validation = stagehand.llm.validate_configuration()
        if validation['valid']:
            print(f"✓ LLM configured: {validation['configuration']['provider']} - {config.model_name}")
        else:
            print("⚠ LLM configuration issues:", validation['errors'])

        page = stagehand.page

        await page.goto("https://www.aigrant.com")
        
        # Extract companies using structured schema        
        companies_data = await page.extract(
          "Extract names and descriptions of 5 companies in batch 3",
          schema=Companies
        )
        
        # Display results
        print("\nExtracted Companies:")
        for idx, company in enumerate(companies_data.companies, 1):
            print(f"{idx}. {company.name}: {company.description}")

        observe = await page.observe("the link to the company Browserbase")
        print("\nObserve result:", observe)
        act = await page.act("click the link to the company Browserbase")
        print("\nAct result:", act)
            
        print("\n🤘 Stagehand session completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())