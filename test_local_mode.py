#!/usr/bin/env python3
"""Quick test of local server mode with the embedded binary."""

import os
import sys

# Add src to path for local testing
sys.path.insert(0, "src")

from stagehand import Stagehand

# Set required API key for LLM operations
if not os.environ.get("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    print("   Set it with: export OPENAI_API_KEY='sk-proj-...'")
    sys.exit(1)

print("🚀 Testing local server mode...")

try:
    # Create client in local mode - will use bundled binary
    print("📦 Creating Stagehand client in local mode...")
    client = Stagehand(
        server="local",
        browserbase_api_key="local",  # Dummy value - not used in local mode
        browserbase_project_id="local",  # Dummy value - not used in local mode
        model_api_key=os.environ["OPENAI_API_KEY"],
        local_headless=True,
        local_port=0,  # Auto-pick free port
        local_ready_timeout_s=15.0,  # Give it time to start
    )

    print("🔧 Starting session (this will start the local server)...")
    session = client.sessions.start(
        model_name="openai/gpt-5-nano",
        browser={
            "type": "local",
            "launchOptions": {},  # Launch local Playwright browser with defaults
        },
    )
    session_id = session.data.session_id

    print(f"✅ Session started: {session_id}")
    print(f"🌐 Server running at: {client.base_url}")

    print("\n📍 Navigating to example.com...")
    client.sessions.navigate(
        id=session_id,
        url="https://example.com",
        frame_id="",
    )
    print("✅ Navigation complete")

    print("\n🔍 Extracting page heading...")
    result = client.sessions.extract(
        id=session_id,
        instruction="Extract the main heading text from the page",
    )
    print(f"📄 Extracted: {result.data.result}")

    print("\n🛑 Ending session...")
    client.sessions.end(id=session_id)
    print("✅ Session ended")

    print("\n🔌 Closing client (will shut down server)...")
    client.close()
    print("✅ Server shut down successfully!")

    print("\n🎉 All tests passed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
