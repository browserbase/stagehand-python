"""
Minimal example using the Sessions Agent Execute endpoint.

Required environment variables:
- BROWSERBASE_API_KEY
- BROWSERBASE_PROJECT_ID
- MODEL_API_KEY

Optional:
- STAGEHAND_MODEL (defaults to "openai/gpt-5-nano")

Run from the repo root:
  `PYTHONPATH=src .venv/bin/python examples/agent_execute_minimal.py`
"""

from __future__ import annotations

import os
import json

from env import load_example_env

from stagehand import AsyncStagehand, APIResponseValidationError


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
    model_name = os.environ.get("STAGEHAND_MODEL", "openai/gpt-5-nano")

    # Enable strict response validation so we fail fast if the API response
    # doesn't match the expected schema (instead of silently constructing models
    # with missing fields set to None).
    async with AsyncStagehand(_strict_response_validation=True) as client:
        try:
            session = await client.sessions.start(model_name=model_name)
        except APIResponseValidationError as e:
            print("Session start response failed schema validation.")
            print(f"Base URL: {client.base_url!r}")
            print(f"HTTP status: {e.response.status_code}")
            print("Raw response text:")
            print(e.response.text)
            print("Parsed response body:")
            print(e.body)
            raise
        if not session.id:
            raise RuntimeError(f"Expected a session ID from /sessions/start but received {session!r}")

        try:
            await session.navigate(
                url="https://news.ycombinator.com",
                options={"wait_until": "domcontentloaded"},
            )

            stream = await session.execute(
                agent_config={"model": model_name},
                execute_options={
                    "instruction": "Go to Hacker News and return the titles of the first 3 articles.",
                    "max_steps": 5,
                },
                stream_response=True,
                x_stream_response="true",
            )

            result = await _stream_to_result(stream, "execute")
            message = result.get("message") if isinstance(result, dict) else result
            print("Agent message:", message)
            print("\nFull result:")
            print(json.dumps(result, indent=2, default=str))
        finally:
            await session.end()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
