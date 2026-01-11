from __future__ import annotations

"""
Example showing how to bring your own browser driver while still using Stagehand.

This script runs Playwright locally to drive the browser and uses Stagehand to
plan the interactions (observe → extract) without having Stagehand own the page.

Required environment variables:
- BROWSERBASE_API_KEY
- BROWSERBASE_PROJECT_ID
- MODEL_API_KEY

Usage:

```
pip install playwright stagehand-alpha
# (if Playwright is new) playwright install chromium
uv run python examples/byob_example.py
```
"""

import os
import asyncio

from playwright.async_api import async_playwright

from stagehand import AsyncStagehand


async def main() -> None:
    async with AsyncStagehand(
        browserbase_api_key=os.environ.get("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
        model_api_key=os.environ.get("MODEL_API_KEY"),
    ) as client, async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        session = await client.sessions.create(model_name="openai/gpt-5-nano")

        try:
            target_url = "https://news.ycombinator.com"
            await page.goto(target_url, wait_until="networkidle")
            await session.navigate(url=target_url)

            print("🎯 Navigated Playwright to Hacker News; Stagehand tracks the same URL.")

            print("🔄 Syncing Stagehand to the current Playwright URL:", page.url)
            await session.navigate(url=page.url)

            extract_response = await session.extract(
                instruction="extract the primary headline on the page",
                schema={
                    "type": "object",
                    "properties": {"headline": {"type": "string"}},
                    "required": ["headline"],
                },
            )

            print("🧮 Stagehand extraction result:", extract_response.data.result)
        finally:
            await session.end()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
