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
pip install playwright stagehand
# (if Playwright is new) playwright install chromium
uv run python examples/byob_example.py
```
"""

from __future__ import annotations

import os
import asyncio

from env import load_example_env
from playwright.async_api import async_playwright

from stagehand import AsyncStagehand


async def _stream_to_result(stream, label: str) -> object | None:
    result_payload: object | None = None
    async for event in stream:
        if event.type == "log":
            print(f"[{label}][log] {event.data.message}")
            continue

        status = event.data.status
        print(f"[{label}][system] status={status}")
        if status == "finished":
            result_payload = event.data.result
        elif status == "error":
            error_message = event.data.error or "unknown error"
            raise RuntimeError(f"{label} stream reported error: {error_message}")

    return result_payload


async def main() -> None:
    load_example_env()
    load_example_env()
    async with AsyncStagehand(
        browserbase_api_key=os.environ.get("BROWSERBASE_API_KEY"),
        browserbase_project_id=os.environ.get("BROWSERBASE_PROJECT_ID"),
        model_api_key=os.environ.get("MODEL_API_KEY"),
    ) as client, async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        session = await client.sessions.start(model_name="anthropic/claude-sonnet-4-6")

        try:
            target_url = "https://news.ycombinator.com"
            await session.navigate(url=target_url)
            await page.goto(target_url, wait_until="networkidle")

            print("🎯 Stagehand already navigated to Hacker News; Playwright now drives that page.")

            # Click the first story's comments link with Playwright.
            comments_selector = "tr.athing:first-of-type + tr .subline > a[href^='item?id=']:nth-last-of-type(1)"
            await page.click(comments_selector, timeout=15_000)
            await page.wait_for_load_state("networkidle")

            print("✅ Playwright clicked the first story link.")

            print("🔄 Syncing Stagehand to Playwright's current URL:", page.url)
            await session.navigate(url=page.url)

            extract_stream = await session.extract(
                instruction="extract the text of the top comment on this page",
                schema={
                    "type": "object",
                    "properties": {"comment": {"type": "string"}},
                    "required": ["comment"],
                },
                stream_response=True,
                x_stream_response="true",
            )

            extract_result = await _stream_to_result(extract_stream, "extract")
            print("🧮 Stagehand extraction result:", extract_result)
        finally:
            await session.end()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
