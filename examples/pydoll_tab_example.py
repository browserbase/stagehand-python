"""
Example: use a Pydoll Tab with the Stagehand Python SDK.

What this demonstrates:
- Start a Stagehand session (remote Stagehand API / Browserbase browser)
- Attach Pydoll to the same browser via CDP (`cdp_url`)
- Use Pydoll to navigate
- Fetch the current page's `frame_id` via CDP `Page.getFrameTree`
- Fetch the current page's `frame_id` via CDP ePage.getFrameTree`
- Pass `frame_id` into `session.observe/act/extract`

Environment variables required:
- MODEL_API_KEY
- BROWSERBASE_API_KEY
- BROWSERBASE_PROJECT_ID

Optional:
- STAGEHAND_BASE_URL (defaults to https://api.stagehand.browserbase.com)

Notes:
- This example requires Python 3.10+ because `pydoll-python` requires Python 3.10+.
- If this repo is pinned to an older Python via `.python-version`, run with:
  - `uv run --python 3.12 python examples/pydoll_tab_example.py`
"""

from __future__ import annotations

import os
import sys
import asyncio
from typing import Any

from env import load_example_env

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


def _normalize_ws_address_for_pydoll(cdp_url: str) -> str:
    # Pydoll currently validates the address strictly as `ws://...` (not `wss://...`).
    if cdp_url.startswith("ws://"):
        return cdp_url
    if cdp_url.startswith("wss://"):
        return "ws://" + cdp_url.removeprefix("wss://")
    if cdp_url.startswith("http://"):
        return "ws://" + cdp_url.removeprefix("http://")
    if cdp_url.startswith("https://"):
        return "ws://" + cdp_url.removeprefix("https://")
    raise RuntimeError(f"Unsupported CDP URL scheme for Pydoll: {cdp_url!r}")


async def _pydoll_attach_to_tab_session(*, chrome: Any, tab: Any) -> tuple[Any, str]:
    """
    Attach to the tab target via CDP Target.attachToTarget (flatten mode) and return (handler, session_id).

    For some CDP proxies (including Browserbase connect URLs), the `/devtools/page/<id>` endpoints may not
    behave like local Chrome's endpoints. Attaching and sending commands with `sessionId` is the most
    compatible approach.
    """
    handler = getattr(chrome, "_connection_handler", None)
    if handler is None:
        raise RuntimeError("Could not find Pydoll browser connection handler on `chrome`.")

    target_id = getattr(tab, "_target_id", None) or getattr(tab, "target_id", None)
    if not target_id:
        raise RuntimeError("Could not find a target id on the tab (expected `tab._target_id`).")

    attached = await handler.execute_command(
        {
            "method": "Target.attachToTarget",
            "params": {"targetId": target_id, "flatten": True},
        },
        timeout=60,
    )
    try:
        return handler, attached["result"]["sessionId"]
    except Exception as e:  # noqa: BLE001
        raise RuntimeError("Failed to attach to target and get sessionId") from e


async def _pydoll_execute_on_session(*, handler: Any, session_id: str, command: dict[str, Any]) -> dict[str, Any]:
    cmd = dict(command)
    cmd["sessionId"] = session_id
    return await handler.execute_command(cmd, timeout=60)


async def _pydoll_session_to_frame_id(*, handler: Any, session_id: str) -> str:
    response = await _pydoll_execute_on_session(
        handler=handler,
        session_id=session_id,
        command={"method": "Page.getFrameTree", "params": {}},
    )
    try:
        return response["result"]["frameTree"]["frame"]["id"]
    except Exception as e:  # noqa: BLE001
        raise RuntimeError("Failed to extract frame id from CDP Page.getFrameTree response") from e


async def main() -> None:
    load_example_env()
    load_example_env()
    model_api_key = os.environ.get("MODEL_API_KEY")
    if not model_api_key:
        sys.exit("Set the MODEL_API_KEY environment variable to run this example.")

    bb_api_key = os.environ.get("BROWSERBASE_API_KEY")
    bb_project_id = os.environ.get("BROWSERBASE_PROJECT_ID")
    if not bb_api_key or not bb_project_id:
        sys.exit("Set BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID to run this example.")

    try:
        from pydoll.browser.chromium import Chrome  # type: ignore[import-not-found]
    except Exception:
        sys.exit(
            "Pydoll is not installed. Install it with:\n"
            "  uv pip install pydoll-python\n"
            "or:\n"
            "  pip install pydoll-python\n"
        )

    async with AsyncStagehand(
        server="remote",
        browserbase_api_key=bb_api_key,
        browserbase_project_id=bb_project_id,
        model_api_key=model_api_key,
    ) as client:
        print("⏳ Starting Stagehand session...")
        session = await client.sessions.start(
            model_name="anthropic/claude-sonnet-4-6",
            browser={"type": "browserbase"},
        )

        cdp_url = session.data.cdp_url
        if not cdp_url:
            sys.exit("No cdp_url returned from the API for this session; cannot attach Pydoll.")

        print(f"✅ Session started: {session.id}")
        print("🔌 Connecting Pydoll to the same browser over CDP...")

        chrome = Chrome()
        try:
            ws_address = _normalize_ws_address_for_pydoll(cdp_url)
            if ws_address != cdp_url:
                print(f"ℹ️ Normalized cdp_url for Pydoll: {ws_address}")
            tab = await chrome.connect(ws_address)

            handler, session_id = await _pydoll_attach_to_tab_session(chrome=chrome, tab=tab)

            await _pydoll_execute_on_session(
                handler=handler,
                session_id=session_id,
                command={"method": "Page.enable", "params": {}},
            )
            await _pydoll_execute_on_session(
                handler=handler,
                session_id=session_id,
                command={"method": "Runtime.enable", "params": {}},
            )

            # Navigate a bit using CDP (via the attached session).
            await _pydoll_execute_on_session(
                handler=handler,
                session_id=session_id,
                command={"method": "Page.navigate", "params": {"url": "https://example.com"}},
            )
            await asyncio.sleep(2)

            await _pydoll_execute_on_session(
                handler=handler,
                session_id=session_id,
                command={
                    "method": "Page.navigate",
                    "params": {"url": "https://www.iana.org/domains/reserved"},
                },
            )
            await asyncio.sleep(2)

            frame_id = await _pydoll_session_to_frame_id(handler=handler, session_id=session_id)
            print(f"🧩 frame_id: {frame_id}")

            print("👀 Stagehand.observe(frame_id=...) ...")
            observe_stream = await session.observe(
                instruction="Find the most relevant click target on this page",
                frame_id=frame_id,
                stream_response=True,
                x_stream_response="true",
            )
            actions = await _stream_to_result(observe_stream, "observe")
            actions = actions if isinstance(actions, list) else []
            print(f"Observed {len(actions)} actions")

            print("🧠 Stagehand.extract(frame_id=...) ...")
            extract_stream = await session.extract(
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
                frame_id=frame_id,
                stream_response=True,
                x_stream_response="true",
            )
            extracted = await _stream_to_result(extract_stream, "extract")
            print("Extracted:", extracted)

        finally:
            close = getattr(chrome, "close", None)
            if callable(close):
                await close()
            await session.end()


if __name__ == "__main__":
    asyncio.run(main())
