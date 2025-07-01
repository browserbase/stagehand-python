import asyncio
import base64
from typing import Any, Optional

from ..types.agent import (
    ActionExecutionResult,
    AgentAction,
)


class StagehandFunctionName:
    AGENT = "agent"


class CUAHandler:  # Computer Use Agent Handler
    """Handles Computer Use Agent tasks by executing actions on the page."""

    def __init__(
        self,
        stagehand,
        page,
        logger,
    ):
        self.stagehand = stagehand
        self.logger = logger
        self.page = page

    async def get_screenshot_base64(self) -> str:
        """Captures a screenshot of the current page and returns it as a base64 encoded string."""
        self.logger.debug(
            "Capturing screenshot for CUA client", category=StagehandFunctionName.AGENT
        )
        screenshot_bytes = await self.page.screenshot(full_page=False, type="png")
        return base64.b64encode(screenshot_bytes).decode()

    async def perform_action(self, action: AgentAction) -> ActionExecutionResult:
        """Execute a single action on the page."""
        self.logger.info(
            f"Performing action: {action.action.root if action.action else ''}",
            category=StagehandFunctionName.AGENT,
        )
        action_type = action.action_type
        # action.action is the RootModel, action.action.root is the specific action model (e.g., ClickAction)
        specific_action_model = action.action.root if action.action else None

        if not specific_action_model:
            self.logger.error(
                f"No specific action model found for action type {action_type}",
                category=StagehandFunctionName.AGENT,
            )
            return {
                "success": False,
                "error": f"No specific action model for {action_type}",
            }

        try:
            # Store initial URL to detect navigation
            initial_url = self.page.url

            if action_type == "click":
                # specific_action_model is already an instance of ClickAction
                x, y = specific_action_model.x, specific_action_model.y
                button = getattr(specific_action_model, "button", "left")
                if button == "back":
                    await self.page.go_back()
                elif button == "forward":
                    await self.page.go_forward()
                else:
                    await self._update_cursor_position(x, y)
                    await self._animate_click(x, y)
                    await asyncio.sleep(0.1)  # Ensure animation is visible
                    await self.page.mouse.click(x, y, button=button)

                # Check for page navigation
                await self.handle_page_navigation("click", initial_url)
                return {"success": True}

            elif action_type == "double_click":
                # specific_action_model is e.g. DoubleClickAction
                x, y = specific_action_model.x, specific_action_model.y
                await self._update_cursor_position(x, y)
                await self._animate_click(x, y)
                await asyncio.sleep(0.1)
                await self._animate_click(x, y)
                await asyncio.sleep(0.1)
                await self.page.mouse.dblclick(x, y)

                # Check for page navigation
                await self.handle_page_navigation("double_click", initial_url)
                return {"success": True}

            elif action_type == "type":
                # specific_action_model is TypeAction
                if (
                    hasattr(specific_action_model, "x")
                    and hasattr(specific_action_model, "y")
                    and specific_action_model.x is not None
                    and specific_action_model.y is not None
                ):
                    await self._update_cursor_position(
                        specific_action_model.x, specific_action_model.y
                    )
                    # Consider if _animate_click is desired before typing at a coordinate
                    await self.page.mouse.click(
                        specific_action_model.x, specific_action_model.y
                    )
                    # await asyncio.sleep(0.1) # Brief pause after click before typing

                await self.page.keyboard.type(specific_action_model.text)

                if (
                    hasattr(specific_action_model, "press_enter_after")
                    and specific_action_model.press_enter_after
                ):
                    await self.page.keyboard.press("Enter")
                    await self.handle_page_navigation("type", initial_url)

                return {"success": True}

            elif action_type == "keypress":
                # specific_action_model is KeyPressAction
                # Ensure playwright_key is defined before loop or correctly scoped if used after
                playwright_key = ""  # Initialize
                for key_str in specific_action_model.keys:
                    playwright_key = self._convert_key_name(key_str)
                    await self.page.keyboard.press(playwright_key)  # Press each key

                # Check for page navigation - keys like Enter can cause navigation
                await self.handle_page_navigation("keypress", initial_url)
                return {"success": True}

            elif action_type == "scroll":
                # specific_action_model is ScrollAction
                x, y = specific_action_model.x, specific_action_model.y
                scroll_x = getattr(specific_action_model, "scroll_x", 0)
                scroll_y = getattr(specific_action_model, "scroll_y", 0)
                await self.page.mouse.move(x, y)
                await self.page.mouse.wheel(scroll_x, scroll_y)
                return {"success": True}

            elif action_type == "function":
                # specific_action_model is FunctionAction
                name = specific_action_model.name
                args = getattr(specific_action_model, "arguments", {})
                if name == "goto" and args.url:
                    await self.page.goto(args.url)
                    return {"success": True}
                elif name == "navigate_back":
                    await self.page.go_back()
                    return {"success": True}
                # Add other function calls like back, forward, reload if needed, similar to TS version
                self.logger.error(
                    f"Unsupported function call: {name}",
                    category=StagehandFunctionName.AGENT,
                )
                return {"success": False, "error": f"Unsupported function: {name}"}

            elif (
                action_type == "key"
            ):  # Anthropic specific key action (can be generalized or mapped by Anthropic client)
                # specific_action_model is KeyAction
                text = specific_action_model.text
                # This logic might be better if Anthropic client translates to a "keypress" AgentAction
                # or if _convert_key_name handles these common names too.
                if text.lower() in ["return", "enter"]:
                    await self.page.keyboard.press("Enter")
                elif text.lower() == "tab":
                    await self.page.keyboard.press("Tab")
                else:
                    # Use _convert_key_name for consistency if possible, or press directly
                    await self.page.keyboard.press(self._convert_key_name(text))

                # Check for page navigation - Enter and other keys may navigate
                await self.handle_page_navigation("key", initial_url)
                return {"success": True}

            elif action_type == "wait":
                await asyncio.gather(
                    asyncio.sleep(specific_action_model.miliseconds / 1000),
                    self.inject_cursor(),
                )
                return {"success": True}

            elif action_type == "move":
                x, y = specific_action_model.x, specific_action_model.y
                await self._update_cursor_position(x, y)
                return {"success": True}

            elif action_type == "screenshot":
                return {"success": True}

            elif action_type == "goto":
                await self.page.goto(specific_action_model.url)
                await self.handle_page_navigation("goto", initial_url)
                return {"success": True}

            else:
                self.logger.error(
                    f"Unsupported action type: {action_type}",
                    category=StagehandFunctionName.AGENT,
                )
                return {
                    "success": False,
                    "error": f"Unsupported action type: {action_type}",
                }

        except Exception as e:
            self.logger.error(
                f"Error executing action {action_type}: {e}",
                category=StagehandFunctionName.AGENT,
            )
            return {"success": False, "error": str(e)}

    async def inject_cursor(self) -> None:
        """Inject a cursor element into the page for visual feedback by calling the JS function."""
        self.logger.debug(
            "Attempting to inject cursor via window.__stagehandInjectCursor",
            category=StagehandFunctionName.AGENT,
        )
        try:
            await self.page.evaluate("window.__stagehandInjectCursor()")
            self.logger.debug(
                "Cursor injection via JS function initiated.",
                category=StagehandFunctionName.AGENT,
            )
        except Exception as e:
            self.logger.error(
                f"Failed to call window.__stagehandInjectCursor: {e}",
                category=StagehandFunctionName.AGENT,
            )

    async def _update_cursor_position(self, x: int, y: int) -> None:
        """Update the cursor position on the page by calling the JS function."""
        try:
            await self.page.evaluate(
                f"window.__stagehandUpdateCursorPosition({x}, {y})"
            )
        except Exception as e:
            self.logger.debug(
                f"Failed to call window.__stagehandUpdateCursorPosition: {e}",
                category=StagehandFunctionName.AGENT,
            )

    async def _animate_click(self, x: int, y: int) -> None:
        """Animate a click at the given position by calling the JS function."""
        try:
            await self.page.evaluate(f"window.__stagehandAnimateClick({x}, {y})")
        except Exception as e:
            self.logger.debug(
                f"Failed to call window.__stagehandAnimateClick: {e}",
                category=StagehandFunctionName.AGENT,
            )

    async def _wait_for_settled_dom(self, timeout_ms: Optional[int] = None) -> None:
        timeout = (
            timeout_ms if timeout_ms is not None else 10000
        )  # Default to 10s, can be configured via stagehand options
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        cdp_session = None

        try:
            cdp_session = await self.page.context.new_cdp_session(self.page)

            # Check if document exists, similar to TypeScript version's hasDoc
            try:
                await self.page.title()
            except Exception:
                await self.page.wait_for_load_state("domcontentloaded", timeout=timeout)

            await cdp_session.send("Network.enable")
            await cdp_session.send("Page.enable")
            await cdp_session.send(
                "Target.setAutoAttach",
                {
                    "autoAttach": True,
                    "waitForDebuggerOnStart": False,
                    "flatten": True,
                },
            )

            inflight_requests: set[str] = set()
            request_meta: dict[str, dict[str, Any]] = (
                {}
            )  # {requestId: {url: string, start: float}}
            doc_by_frame: dict[str, str] = {}  # {frameId: requestId}

            quiet_timer_handle: Optional[asyncio.TimerHandle] = None
            stalled_request_sweep_task: Optional[asyncio.Task] = None

            # Helper to clear quiet timer
            def clear_quiet_timer():
                nonlocal quiet_timer_handle
                if quiet_timer_handle:
                    quiet_timer_handle.cancel()
                    quiet_timer_handle = None

            # Forward declaration for resolve_done
            resolve_done_callbacks = []  # To store cleanup actions

            def resolve_done_action():
                nonlocal quiet_timer_handle, stalled_request_sweep_task

                for callback in resolve_done_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        self.logger.debug(
                            f"Error during resolve_done callback: {e}", category="dom"
                        )

                clear_quiet_timer()
                if stalled_request_sweep_task and not stalled_request_sweep_task.done():
                    stalled_request_sweep_task.cancel()

                if not future.done():
                    future.set_result(None)

            # Helper to potentially resolve if network is quiet
            def maybe_quiet():
                nonlocal quiet_timer_handle
                if (
                    not inflight_requests
                    and not quiet_timer_handle
                    and not future.done()
                ):
                    quiet_timer_handle = loop.call_later(
                        1.0, resolve_done_action
                    )  # Increased to 1000ms (from 0.5)

            # Finishes a request
            def finish_request(request_id: str):
                if request_id not in inflight_requests:
                    return
                inflight_requests.remove(request_id)
                request_meta.pop(request_id, None)

                frames_to_remove = [
                    fid for fid, rid in doc_by_frame.items() if rid == request_id
                ]
                for fid in frames_to_remove:
                    doc_by_frame.pop(fid, None)

                clear_quiet_timer()
                maybe_quiet()

            # Event handlers
            def on_request_will_be_sent(params: dict):
                request_type = params.get("type")
                if request_type == "WebSocket" or request_type == "EventSource":
                    return

                request_id = params["requestId"]
                inflight_requests.add(request_id)
                request_meta[request_id] = {
                    "url": params["request"]["url"],
                    "start": loop.time(),
                }

                if params.get("type") == "Document" and params.get("frameId"):
                    doc_by_frame[params["frameId"]] = request_id

                clear_quiet_timer()

            def on_loading_finished(params: dict):
                finish_request(params["requestId"])

            def on_loading_failed(params: dict):
                finish_request(params["requestId"])

            def on_request_served_from_cache(params: dict):
                finish_request(params["requestId"])

            def on_response_received(params: dict):  # For data URLs
                response_url = params.get("response", {}).get("url", "")
                if response_url.startswith("data:"):
                    finish_request(params["requestId"])

            def on_frame_stopped_loading(params: dict):
                frame_id = params["frameId"]
                request_id = doc_by_frame.get(frame_id)
                if request_id:
                    finish_request(request_id)

            # Attach CDP event listeners
            cdp_session.on("Network.requestWillBeSent", on_request_will_be_sent)
            cdp_session.on("Network.loadingFinished", on_loading_finished)
            cdp_session.on("Network.loadingFailed", on_loading_failed)
            cdp_session.on(
                "Network.requestServedFromCache", on_request_served_from_cache
            )
            cdp_session.on(
                "Network.responseReceived", on_response_received
            )  # For data URLs
            cdp_session.on("Page.frameStoppedLoading", on_frame_stopped_loading)

            resolve_done_callbacks.append(
                lambda: cdp_session.remove_listener(
                    "Network.requestWillBeSent", on_request_will_be_sent
                )
            )
            resolve_done_callbacks.append(
                lambda: cdp_session.remove_listener(
                    "Network.loadingFinished", on_loading_finished
                )
            )
            resolve_done_callbacks.append(
                lambda: cdp_session.remove_listener(
                    "Network.loadingFailed", on_loading_failed
                )
            )
            resolve_done_callbacks.append(
                lambda: cdp_session.remove_listener(
                    "Network.requestServedFromCache", on_request_served_from_cache
                )
            )
            resolve_done_callbacks.append(
                lambda: cdp_session.remove_listener(
                    "Network.responseReceived", on_response_received
                )
            )
            resolve_done_callbacks.append(
                lambda: cdp_session.remove_listener(
                    "Page.frameStoppedLoading", on_frame_stopped_loading
                )
            )

            # Stalled request sweeper
            async def sweep_stalled_requests():
                while not future.done():
                    await asyncio.sleep(0.5)  # 500ms interval
                    now = loop.time()
                    stalled_ids_to_remove = []
                    for req_id, meta in list(
                        request_meta.items()
                    ):  # Iterate over a copy for safe modification
                        if (
                            now - meta["start"] > 4.0
                        ):  # Increased to 4 seconds (from 2.0)
                            stalled_ids_to_remove.append(req_id)
                            self.logger.debug(
                                f"DOM Settle: Forcing completion of stalled request {req_id}, URL: {meta['url'][:120]}",
                                category="dom",  # Using "dom" as a category for these logs
                            )

                    if stalled_ids_to_remove:
                        for req_id in stalled_ids_to_remove:
                            if (
                                req_id in inflight_requests
                            ):  # Ensure it's still considered inflight
                                inflight_requests.remove(req_id)
                            request_meta.pop(req_id, None)
                        clear_quiet_timer()  # State changed
                        maybe_quiet()  # Re-evaluate if network is quiet

            stalled_request_sweep_task = loop.create_task(sweep_stalled_requests())

            # Overall timeout guard
            guard_handle = loop.call_later(
                timeout / 1000.0, lambda: {resolve_done_action()}
            )
            resolve_done_callbacks.append(lambda: guard_handle.cancel())

            maybe_quiet()  # Initial check if already quiet

            await future  # Wait for the future to be resolved

        except Exception as e:
            self.logger.error(f"Error in _wait_for_settled_dom: {e}", category="dom")
            if not future.done():
                future.set_exception(e)  # Propagate error if future not done
        finally:
            if (
                "resolve_done_action" in locals()
                and callable(resolve_done_action)
                and not future.done()
            ):
                # If future isn't done but we are exiting, ensure cleanup happens.
                # This might happen on an unexpected early exit from the try block.
                # However, guard_handle or quiet_timer should eventually call resolve_done_action.
                # If an unhandled exception caused early exit before guard/quiet timers, this is a fallback.
                self.logger.debug(
                    "Ensuring resolve_done_action is called in finally due to early exit",
                    category="dom",
                )
                # resolve_done_action() # Be cautious calling it directly here, might lead to double calls or race conditions
                # Rely on the guard and quiet timers mostly.

            if stalled_request_sweep_task and not stalled_request_sweep_task.done():
                stalled_request_sweep_task.cancel()
                try:
                    await stalled_request_sweep_task  # Allow cleanup
                except asyncio.CancelledError:
                    pass  # Expected

            if cdp_session:
                try:
                    await cdp_session.detach()
                except Exception as e_detach:
                    self.logger.debug(
                        f"Error detaching CDP session: {e_detach}", category="dom"
                    )

    def _convert_key_name(self, key: str) -> str:
        """Convert CUA key names to Playwright key names."""
        key_map = {
            "ENTER": "Enter",
            "RETURN": "Enter",  # Added for Anthropic 'key' type if used via this
            "ESCAPE": "Escape",
            "ESC": "Escape",  # Added
            "BACKSPACE": "Backspace",
            "TAB": "Tab",
            "SPACE": " ",
            "ARROWUP": "ArrowUp",
            "ARROWDOWN": "ArrowDown",
            "ARROWLEFT": "ArrowLeft",
            "ARROWRIGHT": "ArrowRight",
            "UP": "ArrowUp",
            "DOWN": "ArrowDown",
            "LEFT": "ArrowLeft",
            "RIGHT": "ArrowRight",
            "SHIFT": "Shift",
            "CONTROL": "Control",
            "CTRL": "Control",  # Added
            "ALT": "Alt",
            "OPTION": "Alt",  # Added
            "META": "Meta",
            "COMMAND": "Meta",
            "CMD": "Meta",  # Added
            "DELETE": "Delete",
            "HOME": "Home",
            "END": "End",
            "PAGEUP": "PageUp",
            "PAGEDOWN": "PageDown",
            "CAPSLOCK": "CapsLock",
            "INSERT": "Insert",
            "/": "Divide",
            "\\": "Backslash",
        }
        # Convert to uppercase for case-insensitive matching then check map,
        # default to original key if not found.
        return key_map.get(key.upper(), key)

    async def handle_page_navigation(
        self,
        action_description: str,
        initial_url: str,
        dom_settle_timeout_ms: int = 5000,  # Increased default for the new method
    ) -> None:
        """Handle possible page navigation after an action."""
        self.logger.info(
            f"{action_description} - checking for page navigation",
            category=StagehandFunctionName.AGENT,
        )
        newly_opened_page = None
        try:
            # Using a short timeout for immediate new tab detection
            async with self.page.context.expect_page(timeout=1000) as new_page_info:
                pass  # The action that might open a page has already run. We check if one was caught.
            newly_opened_page = await new_page_info.value

            new_page_url = newly_opened_page.url
            await newly_opened_page.close()
            await self.page.goto(new_page_url, timeout=dom_settle_timeout_ms)
            # After navigating, the DOM needs to settle on the new URL.
            await self._wait_for_settled_dom(timeout_ms=dom_settle_timeout_ms)

        except asyncio.TimeoutError:
            newly_opened_page = None
        except Exception:
            newly_opened_page = None

        # If no new tab was opened and handled by navigating, or if we are on the original page after handling a new tab,
        # then proceed to wait for DOM settlement on the current page.
        if not newly_opened_page:
            await self._wait_for_settled_dom(timeout_ms=dom_settle_timeout_ms)

        final_url = self.page.url
        if final_url != initial_url:
            self.logger.debug(
                f"Page navigation handled. Initial URL: {initial_url}, Final URL: {final_url}",
                category=StagehandFunctionName.AGENT,
            )
        else:
            self.logger.debug(
                f"Finished checking for page navigation. URL remains {initial_url}.",
                category=StagehandFunctionName.AGENT,
            )

        # Ensure cursor is injected after any potential navigation or page reload
        await self.inject_cursor()
