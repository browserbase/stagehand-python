import asyncio
import base64

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
                await self.page.keyboard.type(specific_action_model.text)
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
                self.logger.warning(
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
                return {"success": True}

            else:
                self.logger.warning(
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
            self.logger.warning(
                f"Failed to call window.__stagehandUpdateCursorPosition: {e}",
                category=StagehandFunctionName.AGENT,
            )

    async def _animate_click(self, x: int, y: int) -> None:
        """Animate a click at the given position by calling the JS function."""
        try:
            await self.page.evaluate(f"window.__stagehandAnimateClick({x}, {y})")
        except Exception as e:
            self.logger.warning(
                f"Failed to call window.__stagehandAnimateClick: {e}",
                category=StagehandFunctionName.AGENT,
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

    async def _handle_page_navigation(self) -> None:
        """Handle page navigation actions."""
        pass

    async def handle_page_navigation(
        self,
        action_description: str,
        initial_url: str,
        dom_settle_timeout_ms: int = 1000,
    ) -> None:
        """Handle possible page navigation after an action."""
        self.logger.debug(
            f"{action_description} - checking for page navigation",
            category=StagehandFunctionName.AGENT,
        )

        # Check for new tab/window
        new_opened_tab = None
        try:
            async with self.page.context.expect_page(timeout=1500) as new_page_info:
                # Just checking if a page was opened by the action
                pass
            new_opened_tab = await new_page_info.value
        except Exception:
            new_opened_tab = None

        # Handle new tab if one was opened
        if new_opened_tab:
            self.logger.info(
                f"New tab detected with URL: {new_opened_tab.url}",
                category=StagehandFunctionName.AGENT,
            )
            new_tab_url = new_opened_tab.url
            await new_opened_tab.close()
            await self.page.goto(new_tab_url)
            await self.page.wait_for_load_state("domcontentloaded")

        # Wait for DOM to settle
        try:
            await self.page.wait_for_load_state(
                "domcontentloaded", timeout=dom_settle_timeout_ms
            )
            # Additional optional wait for network idle
            await self.page.wait_for_load_state(
                "networkidle", timeout=dom_settle_timeout_ms
            )
        except Exception as e:
            self.logger.warning(
                f"Wait for DOM settle timed out: {str(e)}",
                category=StagehandFunctionName.AGENT,
            )

        # Check if URL changed
        current_url = self.page.url
        if current_url != initial_url:
            self.logger.debug(
                f"Page navigation detected: {initial_url} -> {current_url}",
                category=StagehandFunctionName.AGENT,
            )

        self.logger.debug(
            "Finished checking for page navigation",
            category=StagehandFunctionName.AGENT,
        )
