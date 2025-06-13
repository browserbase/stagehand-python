import asyncio
import json
import os
from typing import Any, Optional

from dotenv import load_dotenv
from openai import (
    OpenAI as OpenAISDK,  # Renamed to avoid conflict with a potential class name
)
from pydantic import BaseModel  # Ensure BaseModel is imported for isinstance check

from ..handlers.cua_handler import CUAHandler
from ..types.agent import (
    ActionExecutionResult,
    AgentAction,
    AgentActionType,
    AgentConfig,
    AgentExecuteOptions,
    AgentResult,
    FunctionAction,
)
from .client import AgentClient

load_dotenv()


class OpenAICUAClient(AgentClient):
    def __init__(
        self,
        model: str = "computer-use-preview",
        instructions: Optional[str] = None,  # System prompt
        config: Optional[AgentConfig] = None,
        logger: Optional[Any] = None,
        handler: Optional[CUAHandler] = None,
        viewport: Optional[dict[str, int]] = None,
        **kwargs,  # Allow for other OpenAI specific options if any
    ):
        super().__init__(model, instructions, config, logger, handler)
        # TODO pass api key
        self.openai_sdk_client = OpenAISDK(
            api_key=config.options.get("apiKey") or os.getenv("OPENAI_API_KEY")
        )

        dimensions = (
            (viewport["width"], viewport["height"]) if viewport else (1024, 768)
        )  # Default or from self.config if specified
        if (
            self.config
            and hasattr(self.config, "display_width")
            and hasattr(self.config, "display_height")
        ):
            dimensions = [self.config.display_width, self.config.display_height]

        self.tools = [
            {
                "type": "function",
                "name": "goto",
                "description": "Navigate to a specific URL",
                "parameters": {
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
                "type": "computer_use_preview",
                "display_width": dimensions[0],
                "display_height": dimensions[1],
                "environment": "browser",
            },
        ]
        self.last_openai_tool_calls: Optional[list[Any]] = None

    def format_screenshot(self, screenshot_base64: str) -> dict:
        """Formats a screenshot for the OpenAI CUA model."""
        return {
            "type": "input_image",
            "image_url": f"data:image/png;base64,{screenshot_base64}",
        }

    def _format_initial_messages(
        self, instruction: str, screenshot_base64: Optional[str]
    ) -> list[Any]:
        messages: list[Any] = []
        if self.instructions:  # System prompt from AgentConfig.instructions
            messages.append({"role": "system", "content": self.instructions})

        user_content: list[Any] = [{"type": "input_text", "text": instruction}]
        if screenshot_base64:
            user_content.append(self.format_screenshot(screenshot_base64))
        messages.append({"role": "user", "content": user_content})
        return messages

    def _process_provider_response(
        self, response: Any
    ) -> tuple[Optional[AgentAction], Optional[str], bool, Optional[str]]:
        if not response.output:
            self.logger.error(
                "No output from OpenAI model in response object", category="agent"
            )
            return (
                None,
                "Error: No output from model",
                True,
                "Error: No output from model",
            )

        output_items = response.output

        computer_call_item = next(
            (item for item in output_items if item.type == "computer_call"), None
        )
        function_call_item = next(
            (item for item in output_items if item.type == "function_call"), None
        )
        reasoning_item = next(
            (item for item in output_items if item.type == "reasoning"), None
        )
        message_item = next(
            (item for item in output_items if item.type == "message"), None
        )

        reasoning_text = None
        if (
            reasoning_item
            and reasoning_item.summary
            and isinstance(reasoning_item.summary, list)
            and len(reasoning_item.summary) > 0
        ):
            reasoning_text = reasoning_item.summary[0].text

        final_model_message = None
        if (
            message_item
            and message_item.content
            and isinstance(message_item.content, list)
        ):
            final_model_message_parts = [
                content_item.text
                for content_item in message_item.content
                if hasattr(content_item, "text") and content_item.type == "output_text"
            ]
            if final_model_message_parts:
                final_model_message = " ".join(final_model_message_parts)

        agent_action: Optional[AgentAction] = None
        self.last_openai_tool_calls = None  # Reset

        if computer_call_item:
            self.last_openai_tool_calls = [
                {
                    "type": "computer_call",
                    "call_id": computer_call_item.call_id,
                    "item": computer_call_item,
                }
            ]

            if not hasattr(computer_call_item, "action") or not isinstance(
                computer_call_item.action, BaseModel
            ):
                err_msg = f"OpenAI computer_call.action is not a Pydantic model or is missing. Type: {type(computer_call_item.action if hasattr(computer_call_item, 'action') else None)}. Content: {computer_call_item.action if hasattr(computer_call_item, 'action') else 'N/A'}"
                self.logger.error(err_msg, category="agent")
                return (
                    None,
                    reasoning_text,
                    True,
                    f"Error: Invalid action structure from OpenAI for computer_call: {computer_call_item.id}",
                )

            try:
                action_payload = AgentActionType(
                    **computer_call_item.action.model_dump()
                )
                agent_action = AgentAction(
                    action_type=computer_call_item.action.type,
                    action=action_payload,
                    reasoning=reasoning_text,  # Reasoning applies to this action
                    status=computer_call_item.status,
                    step=[item.model_dump() for item in output_items],
                )
                # If a computer_call is present, we typically expect to act on it and not look for a function call in the same turn.
                return agent_action, reasoning_text, False, final_model_message
            except Exception as e_parse:
                self.logger.error(
                    f"Error parsing computer_call_item.action: {e_parse}",
                    category="agent",
                )
                return (
                    None,
                    reasoning_text,
                    True,
                    f"Error: Failed to parse computer_call action: {e_parse}",
                )

        elif function_call_item:
            self.last_openai_tool_calls = [
                {
                    "type": "function_call",
                    "call_id": function_call_item.call_id,
                    "item": function_call_item,
                }
            ]

            try:
                arguments = (
                    json.loads(function_call_item.arguments)
                    if isinstance(function_call_item.arguments, str)
                    else function_call_item.arguments
                )
                # Ensure arguments is a dict, even if empty
                if not isinstance(arguments, dict):
                    self.logger.debug(
                        f"Function call arguments are not a dict: {arguments}. Using empty dict.",
                        category="agent",
                    )
                    arguments = {}

                function_action_payload = FunctionAction(type="function", name=function_call_item.name, arguments=arguments)  # type: ignore
                agent_action = AgentAction(
                    action_type="function",  # Literal 'function'
                    action=AgentActionType(root=function_action_payload),
                    reasoning=reasoning_text,  # Reasoning applies to this action
                    status=(
                        function_call_item.status
                        if hasattr(function_call_item, "status")
                        else "in_progress"
                    ),  # function_call might not have status
                    step=[item.model_dump() for item in output_items],
                )
                return agent_action, reasoning_text, False, final_model_message
            except json.JSONDecodeError as e_json:
                self.logger.error(
                    f"JSONDecodeError for function_call arguments: {function_call_item.arguments}. Error: {e_json}",
                    category="agent",
                )
                return (
                    None,
                    reasoning_text,
                    True,
                    f"Error: Invalid JSON arguments for function call {function_call_item.name}",
                )
            except Exception as e_parse_fn:
                self.logger.error(
                    f"Error parsing function_call_item: {e_parse_fn}", category="agent"
                )
                return (
                    None,
                    reasoning_text,
                    True,
                    f"Error: Failed to parse function_call action: {e_parse_fn}",
                )

        # If no computer_call or function_call, the task might be complete or just a message/reasoning turn.
        task_complete_reason = (
            final_model_message
            if final_model_message
            else "No further actions from model."
        )
        if (
            not final_model_message and reasoning_text and not agent_action
        ):  # If only reasoning, it's not task completion by message
            task_complete_reason = "Model provided reasoning but no executable action."
        self.logger.info(
            f"OpenAI CUA: Task appears complete or requires user input. Reason: {task_complete_reason}",
            category="agent",
        )
        return None, reasoning_text, True, final_model_message

    def _format_action_feedback(
        self,
        action_type_performed: str,
        call_id_performed: str,
        is_computer_call: bool,
        action_result: ActionExecutionResult,
        new_screenshot_base64: str,
    ) -> list[Any]:
        if not call_id_performed:
            self.logger.error(
                "Missing call_id for formatting action feedback.", category="agent"
            )
            return [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Error: Internal error, missing call_id for feedback."
                            ),
                        }
                    ],
                }
            ]

        output_item_type = (
            "computer_call_output" if is_computer_call else "function_call_output"
        )

        output_payload: Any
        if action_result["success"]:
            if is_computer_call:
                output_payload = self.format_screenshot(new_screenshot_base64)
            else:
                # Function results are often simple strings or JSON strings.
                output_payload = json.dumps(
                    {
                        "status": "success",
                        "detail": f"Function {action_type_performed} executed.",
                    }
                )

        else:
            error_message = f"Action {action_type_performed} failed: {action_result.get('error', 'Unknown error')}"
            self.logger.info(
                f"Formatting failed action feedback for OpenAI: {error_message}",
                category="agent",
            )
            if is_computer_call:
                output_payload = {
                    "type": "input_text",
                    "text": error_message,
                }
            else:
                output_payload = json.dumps(
                    {"status": "error", "detail": error_message}
                )

        return [
            {
                "type": output_item_type,
                "call_id": call_id_performed,
                "output": output_payload,
            }
        ]

    async def run_task(
        self,
        instruction: str,
        max_steps: int = 20,
        options: Optional[AgentExecuteOptions] = None,
    ) -> AgentResult:
        self.logger.debug(
            f"OpenAI CUA starting task: '{instruction}' with max_steps: {max_steps}",
            category="agent",
        )

        if not self.handler:
            self.logger.error(
                "CUAHandler not available for OpenAIClient.", category="agent"
            )
            return AgentResult(
                completed=False,
                actions=[],
                message="Internal error: Handler not set.",
                usage={"input_tokens": 0, "output_tokens": 0, "inference_time_ms": 0},
            )

        await self.handler.inject_cursor()
        current_screenshot_b64 = await self.handler.get_screenshot_base64()

        current_input_items: list[Any] = self._format_initial_messages(
            instruction, current_screenshot_b64
        )

        actions_taken: list[AgentAction] = []
        total_input_tokens = 0
        total_output_tokens = 0
        total_inference_time_ms = 0  # Placeholder

        for step_count in range(max_steps):
            self.logger.info(
                f"OpenAI CUA - Step {step_count + 1}/{max_steps}",
                category="agent",
            )

            start_time = asyncio.get_event_loop().time()
            try:
                response = self.openai_sdk_client.responses.create(
                    model=self.model,
                    input=current_input_items,
                    tools=self.tools,
                    reasoning={"summary": "concise"},
                    truncation="auto",
                )
                end_time = asyncio.get_event_loop().time()
                total_inference_time_ms += int((end_time - start_time) * 1000)
                if hasattr(response, "usage") and response.usage:
                    total_input_tokens += response.usage.input_tokens or 0
                    total_output_tokens += response.usage.output_tokens or 0

            except Exception as e:
                self.logger.error(f"OpenAI API call failed: {e}", category="agent")
                # Ensure usage is a valid AgentUsage object or None
                usage_obj = {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "inference_time_ms": total_inference_time_ms,
                }
                return AgentResult(
                    actions=[act.action for act in actions_taken if act.action],
                    message=f"OpenAI API error: {e}",
                    completed=True,
                    usage=usage_obj,
                )

            agent_action, reasoning_text, task_completed, final_model_message = (
                self._process_provider_response(response)
            )

            current_input_items.extend(response.output)

            if reasoning_text:
                self.logger.info(f"Model reasoning: {reasoning_text}", category="agent")

            if agent_action:
                actions_taken.append(agent_action)

                action_result: ActionExecutionResult = (
                    await self.handler.perform_action(agent_action)
                )
                current_screenshot_b64 = await self.handler.get_screenshot_base64()

                # Determine call_id and type from last_openai_tool_calls
                # This part assumes last_openai_tool_calls was set correctly in _process_provider_response
                call_to_feedback = None
                if self.last_openai_tool_calls:  # Should be a list with one item
                    call_to_feedback = self.last_openai_tool_calls[0]

                if call_to_feedback:
                    feedback_items = self._format_action_feedback(
                        action_type_performed=agent_action.action_type,  # or specific name for function
                        call_id_performed=call_to_feedback["call_id"],
                        is_computer_call=(call_to_feedback["type"] == "computer_call"),
                        action_result=action_result,
                        new_screenshot_base64=current_screenshot_b64,
                    )
                    current_input_items.extend(feedback_items)
                else:
                    self.logger.error(
                        "Could not find call_id to provide feedback for the last action.",
                        category="agent",
                    )

            if task_completed:
                self.logger.info(
                    f"Task marked complete by model. Final message: {final_model_message}",
                    category="agent",
                )
                usage_obj = {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "inference_time_ms": total_inference_time_ms,
                }
                return AgentResult(
                    actions=[act.action for act in actions_taken if act.action],
                    message=final_model_message or "Task completed.",
                    completed=True,
                    usage=usage_obj,
                )

            if not agent_action and not task_completed:
                self.logger.info(
                    "Model did not request an action and task not marked complete. Ending task to prevent loop.",
                    category="agent",
                )
                usage_obj = {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "inference_time_ms": total_inference_time_ms,
                }
                return AgentResult(
                    actions=[act.action for act in actions_taken if act.action],
                    message="Model did not provide further actions.",
                    completed=False,
                    usage=usage_obj,
                )

        self.logger.info("Max steps reached for OpenAI CUA task.", category="agent")
        usage_obj = {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "inference_time_ms": total_inference_time_ms,
        }
        return AgentResult(
            actions=[act.action for act in actions_taken if act.action],
            message="Max steps reached.",
            completed=False,
            usage=usage_obj,
        )

    def key_to_playwright(self, key: str) -> str:
        """Converts a key name if OpenAI CUA uses specific names not covered by CUAHandler."""
        return key
