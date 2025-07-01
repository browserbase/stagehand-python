import asyncio
import os
from typing import Any, Optional

from anthropic import Anthropic, AnthropicError
from dotenv import load_dotenv

from ..handlers.cua_handler import CUAHandler, StagehandFunctionName
from ..types.agent import (
    ActionExecutionResult,
    AgentAction,
    AgentActionType,
    AgentConfig,
    AgentExecuteOptions,
    AgentResult,
    AgentUsage,
    FunctionArguments,
    Point,
)
from .client import AgentClient

load_dotenv()


class AnthropicCUAClient(AgentClient):
    ANTHROPIC_KEY_MAPPING = {
        "return": "Enter",
        "enter": "Enter",
        "esc": "Escape",
        "escape": "Escape",
        "tab": "Tab",
        "backspace": "Backspace",
        "delete": "Delete",
        "del": "Delete",
        "arrowup": "ArrowUp",
        "up": "ArrowUp",
        "arrowdown": "ArrowDown",
        "down": "ArrowDown",
        "arrowleft": "ArrowLeft",
        "left": "ArrowLeft",
        "arrowright": "ArrowRight",
        "right": "ArrowRight",
        # Add any other specific Anthropic key representations here
    }

    def __init__(
        self,
        model: str,
        instructions: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        logger: Optional[Any] = None,
        handler: Optional[CUAHandler] = None,
        viewport: Optional[dict[str, int]] = None,
        **kwargs,
    ):
        super().__init__(model, instructions, config, logger, handler)
        self.anthropic_sdk_client = Anthropic(
            api_key=config.options.get("apiKey") or os.getenv("ANTHROPIC_API_KEY")
        )

        dimensions = (
            (viewport["width"], viewport["height"]) if viewport else (1024, 768)
        )  # Default dimensions
        if self.config:
            if hasattr(self.config, "display_width") and self.config.display_width is not None:  # type: ignore
                dimensions[0] = self.config.display_width  # type: ignore
            if hasattr(self.config, "display_height") and self.config.display_height is not None:  # type: ignore
                dimensions[1] = self.config.display_height  # type: ignore
        computer_tool_type = (
            "computer_20250124"
            if model == "claude-3-7-sonnet-latest"
            else "computer_20241022"
        )
        self.beta_flag = (
            ["computer-use-2025-01-24"]
            if model == "claude-3-7-sonnet-latest"
            else ["computer-use-2024-10-22"]
        )
        self.tools = [
            {
                "type": computer_tool_type,
                "name": "computer",
                "display_width_px": dimensions[0],
                "display_height_px": dimensions[1],
                "display_number": 1,
            },
            {
                "name": "goto",
                "description": "Navigate to a specific URL",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": (
                                "The URL to navigate to. Provide a full URL, including the protocol (e.g., https://www.google.com)."
                            ),
                        },
                    },
                    "required": ["url"],
                },
            },
            {
                "name": "navigate_back",
                "description": "Navigate back to the previous page",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                },
            },
        ]
        self.max_tokens = kwargs.get("max_tokens", 1024)
        self.last_tool_use_ids = None
        self.logger.info(
            f"AnthropicCUAClient initialized for model: {model}",
            category=StagehandFunctionName.AGENT,
        )

    async def run_task(
        self,
        instruction: str,
        max_steps: int = 20,  # Default max_steps if not in config
        options: Optional[AgentExecuteOptions] = None,
    ) -> AgentResult:
        if self.config and self.config.max_steps is not None:
            max_steps = self.config.max_steps

        self.logger.debug(
            f"Anthropic CUA starting task: '{instruction}' with max_steps: {max_steps}",
            category=StagehandFunctionName.AGENT,
        )

        if not self.handler:
            self.logger.error(
                "CUAHandler not available for AnthropicCUAClient.",
                category=StagehandFunctionName.AGENT,
            )
            return AgentResult(
                completed=False,
                actions=[],
                message="Internal error: Handler not set.",
                usage=AgentUsage(input_tokens=0, output_tokens=0, inference_time_ms=0),
            )

        await self.handler.inject_cursor()
        current_screenshot_b64 = await self.handler.get_screenshot_base64()
        current_messages: list[dict[str, Any]] = self._format_initial_messages(
            instruction, current_screenshot_b64
        )

        actions_taken: list[AgentAction] = []
        total_input_tokens = 0
        total_output_tokens = 0
        total_inference_time_ms = 0
        final_model_message_text: Optional[str] = None

        for step_count in range(max_steps):
            self.logger.info(
                f"Anthropic CUA - Step {step_count + 1}/{max_steps}",
                category=StagehandFunctionName.AGENT,
            )

            start_time = asyncio.get_event_loop().time()
            try:
                response = self.anthropic_sdk_client.beta.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=self.instructions
                    + "Remember to call the computer tools, and only goto or navigate_back if you need to. Screenshots, clicks, etc, will be parsed from computer tool calls",  # System prompt
                    messages=current_messages,
                    tools=self.tools,
                    betas=self.beta_flag,
                )
                end_time = asyncio.get_event_loop().time()
                total_inference_time_ms += int((end_time - start_time) * 1000)
                if response.usage:
                    total_input_tokens += response.usage.input_tokens or 0
                    total_output_tokens += response.usage.output_tokens or 0

            except AnthropicError as e:
                self.logger.error(
                    f"Anthropic API call failed: {e}",
                    category=StagehandFunctionName.AGENT,
                )
                return AgentResult(
                    actions=[act.action for act in actions_taken if act.action],
                    message=f"Anthropic API error: {e}",
                    completed=True,  # End task on API error
                    usage=AgentUsage(
                        input_tokens=total_input_tokens,
                        output_tokens=total_output_tokens,
                        inference_time_ms=total_inference_time_ms,
                    ),
                )

            (
                agent_action,
                reasoning_text,
                task_completed,
                raw_assistant_content_blocks,
            ) = self._process_provider_response(response)

            if raw_assistant_content_blocks:
                current_messages.append(
                    {"role": "assistant", "content": raw_assistant_content_blocks}
                )

            if reasoning_text:
                self.logger.info(
                    f"Model reasoning: {reasoning_text}",
                    category=StagehandFunctionName.AGENT,
                )
                final_model_message_text = reasoning_text

            if agent_action:
                actions_taken.append(agent_action)
                action_result: ActionExecutionResult = (
                    await self.handler.perform_action(agent_action)
                )
                # Get new screenshot and current page url after action
                current_screenshot_b64_after_action = (
                    await self.handler.get_screenshot_base64()
                )

                current_page_url_after_action = None
                if self.handler.page:
                    current_page_url_after_action = self.handler.page.url

                if self.last_tool_use_ids:
                    feedback_items = self._format_action_feedback(
                        action=agent_action,
                        tool_use_id=self.last_tool_use_ids[0],
                        tool_name="computer",
                        action_result=action_result,
                        new_screenshot_base64=current_screenshot_b64_after_action,
                        current_url=current_page_url_after_action,
                    )
                    current_messages.append({"role": "user", "content": feedback_items})

            if task_completed:
                self.logger.info(
                    f"Task marked complete by model. Final message: {final_model_message_text}",
                    category=StagehandFunctionName.AGENT,
                )
                break

            if not agent_action and not task_completed:
                self.logger.info(
                    "Model did not request an action and task not marked complete. Ending task to prevent loop.",
                    category=StagehandFunctionName.AGENT,
                )
                final_model_message_text = "Model did not provide further actions."
                task_completed = False  # Mark as not truly completed by intent
                break

        usage_obj = AgentUsage(
            input_tokens=total_input_tokens,
            output_tokens=total_output_tokens,
            inference_time_ms=total_inference_time_ms,
        )
        return AgentResult(
            actions=[act.action for act in actions_taken if act.action],
            message=final_model_message_text or "Max steps reached or task ended.",
            completed=(task_completed if "task_completed" in locals() else False),
            usage=usage_obj,
        )

    def _format_initial_messages(
        self, instruction: str, screenshot_base64: Optional[str]
    ) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        user_content: list[dict[str, Any]] = [{"type": "text", "text": instruction}]
        if screenshot_base64:
            user_content.append(self.format_screenshot(screenshot_base64))

        messages.append({"role": "user", "content": user_content})
        return messages

    def _process_provider_response(
        self, response: Any  # Anthropic API response object
    ) -> tuple[Optional[AgentAction], Optional[str], bool, list[dict[str, Any]]]:

        self.last_tool_use_ids = []
        model_message_parts: list[str] = []
        agent_action: Optional[AgentAction] = None

        raw_assistant_content_blocks = []
        if hasattr(response, "content") and isinstance(response.content, list):
            # Serialize Pydantic models from response.content for history
            try:
                raw_assistant_content_blocks = [
                    block.model_dump() for block in response.content
                ]
            except Exception as e:
                self.logger.error(
                    f"Could not model_dump response.content blocks: {e}",
                    category=StagehandFunctionName.AGENT,
                )
                # Fallback if model_dump fails for some reason, try to keep raw if possible
                raw_assistant_content_blocks = response.content

            tool_use_block = None
            for block in response.content:
                if block.type == "tool_use":
                    tool_use_block = block
                    self.last_tool_use_ids.append(block.id)
                elif block.type == "text":
                    model_message_parts.append(block.text)

            if tool_use_block:
                tool_name = tool_use_block.name
                tool_input = (
                    tool_use_block.input if hasattr(tool_use_block, "input") else {}
                )

                agent_action = self._convert_tool_use_to_agent_action(
                    tool_name, tool_input
                )
                if agent_action:
                    agent_action.step = raw_assistant_content_blocks

        model_message_text = " ".join(model_message_parts).strip() or None
        task_completed = not bool(
            agent_action
        )  # Task is complete if no tool_use blocks

        return (
            agent_action,
            model_message_text,
            task_completed,
            raw_assistant_content_blocks,
        )

    def _convert_tool_use_to_agent_action(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> Optional[AgentAction]:
        if (
            tool_name != "computer"
            and tool_name != "goto"
            and tool_name != "navigate_back"
        ):
            self.logger.error(
                f"Unsupported tool name from Anthropic: {tool_name}",
                category=StagehandFunctionName.AGENT,
            )
            return None

        if tool_name == "goto" or tool_name == "navigate_back":
            action_type_str = "function"
        else:
            action_type_str = tool_input.get("action")
        if not action_type_str:
            self.logger.error(
                "Missing 'action' in Anthropic computer tool_input",
                category=StagehandFunctionName.AGENT,
            )
            return None

        action_model_payload: Optional[AgentActionType] = None
        reasoning = tool_input.get("reasoning")

        try:
            # Get coordinates for actions that use them
            coordinate = tool_input.get("coordinate", [])
            x, y = (
                coordinate
                if isinstance(coordinate, list) and len(coordinate) >= 2
                else [None, None]
            )

            if action_type_str == "left_click":
                action_model_payload = AgentActionType(
                    type="click",
                    x=x,
                    y=y,
                    button="left",
                )
                action_type_str = "click"  # Normalize

            elif action_type_str == "right_click":
                action_model_payload = AgentActionType(
                    type="click",
                    x=x,
                    y=y,
                    button="right",
                )
                action_type_str = "click"  # Normalize

            elif action_type_str == "middle_click":
                action_model_payload = AgentActionType(
                    type="click",
                    x=x,
                    y=y,
                    button="middle",
                )
                action_type_str = "click"  # Normalize

            elif action_type_str == "double_click":
                action_model_payload = AgentActionType(
                    type="double_click",
                    x=x,
                    y=y,
                )

            elif action_type_str == "triple_click":
                # Handle as double_click for now since we don't have a dedicated triple click
                action_model_payload = AgentActionType(
                    type="double_click",
                    x=x,
                    y=y,
                )
                action_type_str = "double_click"  # Normalize

            elif action_type_str == "type":
                action_model_payload = AgentActionType(
                    type="type", text=tool_input.get("text", "")
                )

            elif action_type_str == "key":
                key_text = tool_input.get("text", "")
                if key_text:
                    # Convert string to an array of keys
                    keys = [
                        self.key_to_playwright(k.strip()) for k in key_text.split("+")
                    ]
                    action_model_payload = AgentActionType(
                        type="keypress",
                        keys=keys,
                    )
                    action_type_str = "keypress"  # Normalize

            elif action_type_str == "hold_key":
                key_text = tool_input.get("text", "")
                duration = tool_input.get(
                    "duration", 1
                )  # Default 1 second if not specified
                if key_text:
                    # Convert to keydown followed by keyup after duration
                    keys = [
                        self.key_to_playwright(k.strip()) for k in key_text.split("+")
                    ]
                    # For now, handle as a regular keypress
                    action_model_payload = AgentActionType(
                        type="keypress",
                        keys=keys,
                    )
                    action_type_str = "keypress"  # Normalize

            elif action_type_str == "scroll":
                scroll_direction = tool_input.get("scroll_direction")
                scroll_amount = tool_input.get("scroll_amount", 1)
                scroll_multiplier = 100  # Default multiplier

                scroll_x = 0
                scroll_y = 0

                if scroll_direction == "down":
                    scroll_y = scroll_amount * scroll_multiplier
                elif scroll_direction == "up":
                    scroll_y = -scroll_amount * scroll_multiplier
                elif scroll_direction == "right":
                    scroll_x = scroll_amount * scroll_multiplier
                elif scroll_direction == "left":
                    scroll_x = -scroll_amount * scroll_multiplier

                action_model_payload = AgentActionType(
                    type="scroll",
                    x=x or 0,  # Default to 0 if none
                    y=y or 0,  # Default to 0 if none
                    scroll_x=scroll_x,
                    scroll_y=scroll_y,
                )

            elif action_type_str == "mouse_move":
                action_model_payload = AgentActionType(
                    type="move",
                    x=x,
                    y=y,
                )
                action_type_str = "move"  # Normalize

            elif action_type_str == "left_click_drag":
                start_coordinate = tool_input.get("start_coordinate", [])
                start_x, start_y = (
                    start_coordinate
                    if isinstance(start_coordinate, list) and len(start_coordinate) >= 2
                    else [None, None]
                )

                if (
                    start_x is not None
                    and start_y is not None
                    and x is not None
                    and y is not None
                ):
                    path_points = [
                        Point(x=start_x, y=start_y),
                        Point(x=x, y=y),
                    ]
                    action_model_payload = AgentActionType(
                        type="drag",
                        path=path_points,
                    )
                    action_type_str = "drag"  # Normalize
                else:
                    self.logger.error(
                        "Drag action missing valid start or end coordinates.",
                        category=StagehandFunctionName.AGENT,
                    )
                    return None

            elif action_type_str == "left_mouse_down":
                # Currently not directly supported - handle as a click for now
                action_model_payload = AgentActionType(
                    type="click",
                    x=x,
                    y=y,
                    button="left",
                )
                action_type_str = "click"  # Normalize

            elif action_type_str == "left_mouse_up":
                # Currently not directly supported - handle as a click for now
                action_model_payload = AgentActionType(
                    type="click",
                    x=x,
                    y=y,
                    button="left",
                )
                action_type_str = "click"  # Normalize

            elif action_type_str == "wait":
                duration = tool_input.get("duration", 1)  # Default 1 second
                # Convert seconds to milliseconds
                action_model_payload = AgentActionType(
                    type="wait",
                    miliseconds=int(duration * 1000),
                )

            elif action_type_str == "screenshot":
                action_model_payload = AgentActionType(
                    type="screenshot",
                )

            elif action_type_str == "cursor_position":
                # This is a read operation, not directly supported
                # Return a no-op for now
                action_model_payload = AgentActionType(
                    type="screenshot",  # Use screenshot as a way to show cursor position
                )
                action_type_str = "screenshot"  # Normalize

            elif action_type_str == "function":
                if tool_name == "goto":
                    url = tool_input.get("url")
                    if url:
                        action_model_payload = AgentActionType(
                            type="function",
                            name="goto",
                            arguments=FunctionArguments(url=url),
                        )
                        action_type_str = "function"
                    else:
                        self.logger.error(
                            "Goto action from Anthropic missing URL",
                            category=StagehandFunctionName.AGENT,
                        )
                        return None
                elif tool_name == "navigate_back":
                    action_model_payload = AgentActionType(
                        type="function",
                        name="navigate_back",
                        arguments=FunctionArguments(),
                    )
                    action_type_str = "function"
            else:
                self.logger.error(
                    f"Unsupported action type '{action_type_str}' from Anthropic computer tool.",
                    category=StagehandFunctionName.AGENT,
                )
                return None

            if action_model_payload is not None:
                return AgentAction(
                    action_type=action_type_str,
                    action=action_model_payload,
                    reasoning=reasoning,
                )

        except Exception as e:
            self.logger.error(
                f"Error converting Anthropic action '{action_type_str}': {e}",
                category=StagehandFunctionName.AGENT,
            )

        return None

    def _format_action_feedback(
        self,
        action: AgentAction,
        tool_use_id: str,
        tool_name: str,
        action_result: ActionExecutionResult,
        new_screenshot_base64: str,
        current_url: Optional[str],
    ) -> list[dict[str, Any]]:
        content_for_tool_result: list[dict[str, Any]] = []
        is_error_result = not action_result.get("success", False)

        if tool_name == "computer":
            if (
                new_screenshot_base64
            ):  # Always send screenshot for computer tool results
                content_for_tool_result.append(
                    self.format_screenshot(new_screenshot_base64)
                )
            else:
                self.logger.error(
                    "Missing screenshot for computer tool feedback (empty string passed).",
                    category=StagehandFunctionName.AGENT,
                )

            if current_url:  # Add current URL as text, similar to TS client
                content_for_tool_result.append(
                    {"type": "text", "text": f"Current URL: {current_url}"}
                )

            if is_error_result:
                error_msg = action_result.get("error", "Unknown error")
                content_for_tool_result.append(
                    {"type": "text", "text": f"Error: {error_msg}"}
                )

        else:  # For other tools, if any
            if is_error_result:
                error_msg = action_result.get("error", "Unknown error")
                content_for_tool_result.append(
                    {
                        "type": "text",
                        "text": f"Error executing {tool_name}: {error_msg}",
                    }
                )
            else:
                content_for_tool_result.append(
                    {"type": "text", "text": f"Tool {tool_name} executed successfully."}
                )

        if not content_for_tool_result and not is_error_result:
            content_for_tool_result.append(
                {"type": "text", "text": "Action completed."}
            )

        return [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": content_for_tool_result,
            }
        ]

    def format_screenshot(self, screenshot_base64: str) -> dict[str, Any]:
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": screenshot_base64,
            },
        }

    def key_to_playwright(self, key: str) -> str:
        """Convert an Anthropic key name to a Playwright-compatible key name."""
        return self.ANTHROPIC_KEY_MAPPING.get(key.lower(), key)
