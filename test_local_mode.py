#!/usr/bin/env python3
"""Quick test of local server mode with the embedded binary."""

import os
import sys

# Add src to path for local testing
sys.path.insert(0, "src")

from stagehand import Stagehand

# Set required API key for LLM operations
if not os.environ.get("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY environment variable not set")  # noqa: T201
    print("   Set it with: export OPENAI_API_KEY='sk-proj-...'")  # noqa: T201
    sys.exit(1)

print("🚀 Testing local server mode...")  # noqa: T201

try:
    # Create client in local mode - will use bundled binary
    print("📦 Creating Stagehand client in local mode...")  # noqa: T201
    client = Stagehand(
        server="local",
        browserbase_api_key="local",  # Dummy value - not used in local mode
        browserbase_project_id="local",  # Dummy value - not used in local mode
        model_api_key=os.environ["OPENAI_API_KEY"],
        local_headless=True,
        local_port=0,  # Auto-pick free port
        local_ready_timeout_s=15.0,  # Give it time to start
    )

    print("🔧 Starting session (this will start the local server)...")  # noqa: T201
    session = client.sessions.start(
        model_name="openai/gpt-5-nano",
        browser={
            "type": "local",
            "launchOptions": {},  # Launch local Playwright browser with defaults
        },
    )
    session_id = session.data.session_id

    print(f"✅ Session started: {session_id}")  # noqa: T201
    print(f"🌐 Server running at: {client.base_url}")  # noqa: T201

    print("\n📍 Navigating to example.com...")  # noqa: T201
    client.sessions.navigate(
        id=session_id,
        url="https://example.com",
        frame_id="",
    )
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

    print("\n🔌 Closing client (will shut down server)...")  # noqa: T201
    client.close()
    print("✅ Server shut down successfully!")  # noqa: T201

    print("\n🎉 All tests passed!")  # noqa: T201

except Exception as e:
    print(f"\n❌ Error: {e}")  # noqa: T201
    import traceback
    traceback.print_exc()
    sys.exit(1)
