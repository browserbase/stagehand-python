"""
Example demonstrating how to run Stagehand in local mode using the SEA binary
that ships with the PyPI wheel.

Required environment variables:
- BROWSERBASE_API_KEY (can be any value in local mode)
- BROWSERBASE_PROJECT_ID (can be any value in local mode)
- MODEL_API_KEY (used for client configuration even in local mode)

You can also set `OPENAI_API_KEY` if you prefer, but the example defaults to `MODEL_API_KEY`.

Install the published wheel before running this script:
  `pip install stagehand`
Then execute this example with the same interpreter:
  `python examples/local_example.py`
"""

import os
import sys
from typing import Optional

from stagehand import Stagehand


def main() -> None:
    model_key = os.environ.get("MODEL_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if not model_key and not openai_key:
        sys.exit("Set MODEL_API_KEY to run the local server.")

    client = Stagehand(
        server="local",
        local_openai_api_key=openai_key or model_key,
        local_ready_timeout_s=30.0,
    )

    session_id: Optional[str] = None

    try:
        print("⏳ Starting local session (this will start the embedded SEA binary)...")
        session = client.sessions.start(
            model_name="openai/gpt-5-nano",
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
        extract_response = client.sessions.extract(
            id=session_id,
            instruction="Extract the text of the top-level heading on this page.",
        )
        print(f"📄 Extracted data: {extract_response.data.result}")

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
