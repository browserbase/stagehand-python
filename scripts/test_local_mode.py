#!/usr/bin/env python3
"""Quick test of local server mode with the embedded binary."""

import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stagehand import Stagehand


def main() -> None:
    model_api_key = os.environ.get("MODEL_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not model_api_key:
        print("❌ Error: MODEL_API_KEY or OPENAI_API_KEY environment variable not set")  # noqa: T201
        print("   Set it with: export MODEL_API_KEY='sk-proj-...'")  # noqa: T201
        sys.exit(1)

    os.environ["BROWSERBASE_FLOW_LOGS"] = "1"

    print("🚀 Testing local server mode...")  # noqa: T201
    client = None

    try:
        print("📦 Creating Stagehand client in local mode...")  # noqa: T201
        client = Stagehand(
            server="local",
            browserbase_api_key="local",
            browserbase_project_id="local",
            model_api_key=model_api_key,
            local_headless=True,
            local_port=0,
            local_ready_timeout_s=15.0,
        )

        print("🔧 Starting session (this will start the local server)...")  # noqa: T201
        session = client.sessions.start(
            model_name="openai/gpt-5-nano",
            browser={  # type: ignore[arg-type]
                "type": "local",
                "launchOptions": {},
            },
        )
        session_id = session.data.session_id

        print(f"✅ Session started: {session_id}")  # noqa: T201
        print(f"🌐 Server running at: {client.base_url}")  # noqa: T201

        print("\n📍 Navigating to example.com...")  # noqa: T201
        client.sessions.navigate(id=session_id, url="https://example.com")
        print("✅ Navigation complete")  # noqa: T201

        print("\n🔍 Extracting page heading...")  # noqa: T201
        result = client.sessions.extract(
            id=session_id,
            instruction="Extract the main heading text from the page",
        )
        print(f"📄 Extracted: {result.data.result}")  # noqa: T201

        print("\n🛑 Ending session...")  # noqa: T201
        client.sessions.end(id=session_id)
        print("✅ Session ended")  # noqa: T201
        print("\n🎉 All tests passed!")  # noqa: T201
    except Exception as exc:
        print(f"\n❌ Error: {exc}")  # noqa: T201
        traceback.print_exc()
        sys.exit(1)
    finally:
        if client is not None:
            print("\n🔌 Closing client (will shut down server)...")  # noqa: T201
            client.close()
            print("✅ Server shut down successfully!")  # noqa: T201


if __name__ == "__main__":
    main()
