"""
Example: use a Playwright Page with the Stagehand Python SDK (local browser).

What this demonstrates:
- Start a Stagehand session in local mode
- Launch a local Playwright browser server and share its CDP URL with Stagehand
- Pass the Playwright `page` into `session.observe/act/extract/execute`
  so Stagehand auto-detects the correct `frame_id` for that page
- Stream SSE events by default for observe/act/extract/execute
- Run the full flow: start → observe → act → extract → agent/execute → end

Environment variables required:
- MODEL_API_KEY
- BROWSERBASE_API_KEY (can be any value in local mode)
- BROWSERBASE_PROJECT_ID (can be any value in local mode)

Optional:
- STAGEHAND_BASE_URL (defaults to http://127.0.0.1:3000)
"""

from __future__ import annotations

import os
import sys
import json
import time
import socket
from typing import Any, Optional
from urllib.request import urlopen

from env import load_example_env

from stagehand import Stagehand


def _print_stream_events(stream: Any, label: str) -> object | None:
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


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _resolve_cdp_ws_url(port: int) -> str:
    url = f"http://127.0.0.1:{port}/json/version"
    last_error: Exception | None = None
    for _ in range(40):
        try:
            with urlopen(url, timeout=1) as response:
                payload = json.loads(response.read().decode("utf-8"))
            ws_url = payload.get("webSocketDebuggerUrl")
            if ws_url:
                return str(ws_url)
        except Exception as exc:  # noqa: BLE001 - transient startup errors are expected
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(
        f"Unable to resolve CDP websocket URL from {url}. Last error: {last_error}"
    )


def main() -> None:
    load_example_env()
    model_api_key = os.environ.get("MODEL_API_KEY")
    if not model_api_key:
        sys.exit("Set the MODEL_API_KEY environment variable to run this example.")

    bb_api_key = os.environ.get("BROWSERBASE_API_KEY")
    bb_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
    if not bb_api_key or not bb_project_id:
        sys.exit(
            "Set BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID to run this example."
        )

    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]
    except Exception:
        sys.exit(
            "Playwright is not installed. Install it with:\n"
            "  uv pip install playwright\n"
            "and ensure browsers are installed (e.g. `playwright install chromium`)."
        )

    session_id: Optional[str] = None

    with Stagehand(
        server="local",
        browserbase_api_key=bb_api_key,
        browserbase_project_id=bb_project_id,
        model_api_key=model_api_key,
        local_openai_api_key=model_api_key,
        local_ready_timeout_s=30.0,
    ) as client:
        print("⏳ Starting Stagehand session (local server + local browser)...")

        with sync_playwright() as p:
            port = _pick_free_port()
            browser = p.chromium.launch(
                headless=True,
                args=[f"--remote-debugging-port={port}"],
            )
            cdp_url = _resolve_cdp_ws_url(port)

            context = browser.new_context()
            page = context.new_page()
            page.goto("about:blank", wait_until="domcontentloaded")

            session = client.sessions.start(
                model_name="anthropic/claude-sonnet-4-6",
                browser={
                    "type": "local",
                    "launchOptions": {"cdpUrl": cdp_url},
                },
                verbose=2,
            )
            session_id = session.id

            print(f"✅ Session started: {session_id}")
            print("🔌 Connecting Playwright to the same browser over CDP...")

            try:
                page.goto("https://example.com", wait_until="domcontentloaded")

                print("👀 Stagehand.observe(page=...) with SSE streaming...")
                observe_stream = session.observe(
                    instruction="Find the most relevant click target on this page",
                    page=page,
                    stream_response=True,
                    x_stream_response="true",
                )
                observe_result = _print_stream_events(observe_stream, "observe")

                actions = observe_result or []
                if not actions:
                    print("No actions found; ending session.")
                    return

                print("🖱️ Stagehand.act(page=...) with SSE streaming...")
                act_stream = session.act(
                    input=actions[0],
                    page=page,
                    stream_response=True,
                    x_stream_response="true",
                )
                _ = _print_stream_events(act_stream, "act")

                print("🧠 Stagehand.extract(page=...) with SSE streaming...")
                extract_stream = session.extract(
                    instruction="Extract the page title and the primary heading (h1) text",
                    schema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "h1": {"type": "string"},
                        },
                        "required": ["title", "h1"],
                        "additionalProperties": False,
                    },
                    page=page,
                    stream_response=True,
                    x_stream_response="true",
                )
                extracted = _print_stream_events(extract_stream, "extract")
                print("Extracted:", extracted)

                print("🤖 Stagehand.execute(page=...) with SSE streaming...")
                execute_stream = session.execute(
                    agent_config={"model": "anthropic/claude-opus-4-6"},
                    execute_options={
                        "instruction": (
                            "Open the 'Learn more' link if present and summarize the destination in one sentence."
                        ),
                        "max_steps": 5,
                    },
                    page=page,
                    stream_response=True,
                    x_stream_response="true",
                )
                execute_result = _print_stream_events(execute_stream, "execute")
                print("Execute result:", execute_result)
            finally:
                browser.close()
                session.end()
                print("✅ Session ended.")


if __name__ == "__main__":
    main()
