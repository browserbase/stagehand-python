"""
Example demonstrating how to run Stagehand in local mode using the SEA binary
that ships with the PyPI wheel.

Required environment variables:
- BROWSERBASE_API_KEY (can be any value in local mode)
- BROWSERBASE_PROJECT_ID (can be any value in local mode)
- MODEL_API_KEY (used for client configuration even in local mode)


Install the published wheel before running this script:
  `pip install stagehand`
Then execute this example with the same interpreter:
  `python examples/local_example.py`
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from env import load_example_env

from stagehand import Stagehand


def _stream_to_result(stream, label: str) -> object | None:
    result_payload: object | None = None
    for event in stream:
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


def main() -> None:
    load_example_env()
    model_key = os.environ.get("MODEL_API_KEY")
    if not model_key:
        sys.exit("Set MODEL_API_KEY to run the local server.")

    client = Stagehand(
        server="local",
        model_api_key=model_key,
        local_ready_timeout_s=30.0,
    )

    session_id: Optional[str] = None

    try:
        print("⏳ Starting local session (this will start the embedded SEA binary)...")
        session = client.sessions.start(
            model_name="anthropic/claude-sonnet-4-6",
            browser={
                "type": "local",
                "launchOptions": {
                    "headless": True,
                },
            },
        )
        session_id = session.data.session_id
        print(f"✅ Session started: {session_id}")

        print("🌐 Navigating to https://www.example.com...")
        client.sessions.navigate(
            id=session_id,
            url="https://www.example.com",
        )
        print("✅ Navigation complete")

        print("🔍 Extracting the main heading text...")
        extract_stream = client.sessions.extract(
            id=session_id,
            instruction="Extract the text of the top-level heading on this page.",
            stream_response=True,
            x_stream_response="true",
        )
        extract_result = _stream_to_result(extract_stream, "extract")
        print(f"📄 Extracted data: {extract_result}")

    except Exception as exc:
        print(f"❌ Encountered an error: {exc}")
        raise
    finally:
        if session_id:
            print("🛑 Ending session...")
            client.sessions.end(id=session_id)
            print("✅ Session ended")
        print("🔌 Closing client (shuts down the SEA server)...")
        client.close()
        print("✅ Local server shut down")


if __name__ == "__main__":
    main()
