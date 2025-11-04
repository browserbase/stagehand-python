import asyncio
import os
from typing import Any, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.types import (
    Candidate,
    Content,
    FunctionResponse,
    FunctionResponseBlob,
    FunctionResponsePart,
    GenerateContentConfig,
    Part,
)
from pydantic import TypeAdapter

from ..handlers.cua_handler import CUAHandler
from ..types.agent import (
    ActionExecutionResult,
    AgentAction,
    AgentActionType,
    AgentConfig,
    AgentExecuteOptions,
    AgentResult,
)
from .client import AgentClient

load_dotenv()


class GoogleCUAClient(AgentClient):
    def __init__(
        self,
        model: str = "computer-use-preview-10-2025",
        instructions: Optional[str] = None,  # System prompt
        config: Optional[AgentConfig] = None,
        logger: Optional[Any] = None,
        handler: Optional[CUAHandler] = None,
        viewport: Optional[dict[str, int]] = None,
        **kwargs,  # Allow for other Google specific options if any
    ):
        super().__init__(model, instructions, config, logger, handler)

        # Match OpenAI pattern for API key handling
        api_key = None
        if config and hasattr(config, "options") and config.options:
            api_key = config.options.get("apiKey")
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable not set and not provided in config."
            )

        self.genai_client = genai.Client(api_key=api_key)

        # Match OpenAI pattern for viewport handling
        dimensions = (
            (viewport["width"], viewport["height"]) if viewport else (1288, 711)
        )
        if (
            self.config
            and hasattr(self.config, "display_width")
            and hasattr(self.config, "display_height")
        ):
            dimensions = [self.config.display_width, self.config.display_height]

        self.display_width = dimensions[0]
        self.display_height = dimensions[1]

        self._generate_content_config = GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            tools=[
                types.Tool(
                    computer_use=types.ComputerUse(
                        environment=types.Environment.ENVIRONMENT_BROWSER
                    )
                )
            ],
        )

        self.history: list[Content] = []

    def format_screenshot(self, screenshot_base64: str) -> Part:
        """Formats a screenshot for the Gemini CUA model."""
        return Part(
            inline_data=types.Blob(mime_type="image/png", data=screenshot_base64)
        )

    def _format_initial_messages(
        self, instruction: str, screenshot_base64: Optional[str]
    ) -> list[Content]:
        """Formats the initial messages for the Gemini CUA model."""
        parts: list[Part] = []

        # Add system prompt if provided
        if self.instructions:
            parts.append(Part(text=self.instructions))

        parts.append(Part(text=instruction))

        if screenshot_base64:
            parts.append(self.format_screenshot(screenshot_base64))

        # Initial user message
        initial_content = Content(role="user", parts=parts)
        self.history = [initial_content]  # Start history with the first user message
        return self.history

    def _normalize_coordinates(self, x: int, y: int) -> tuple[int, int]:
        """Normalizes coordinates from 0-1000 range to actual display dimensions."""
        norm_x = int(x / 1000 * self.display_width)
        norm_y = int(y / 1000 * self.display_height)
        return norm_x, norm_y

    def _process_provider_response(
        self, response: types.GenerateContentResponse
    ) -> tuple[
        list[AgentAction],
        Optional[str],
        bool,
        Optional[str],
        list[tuple[str, dict[str, Any]]],
    ]:
        if not response.candidates:
            self.logger.error("No candidates in Google response", category="agent")
            return (
                [],
                "Error: No candidates from model",
                True,
                "Error: No candidates from model",
                [],
            )

        candidate = response.candidates[0]
        self.history.append(candidate.content)  # Add model's response to history

        reasoning_text: Optional[str] = None
        function_call_parts: list[types.FunctionCall] = []

        for part in candidate.content.parts:
            if part.text:
                if reasoning_text is None:
                    reasoning_text = part.text
                else:
                    reasoning_text += (
                        " " + part.text
                    )  # Concatenate if multiple text parts
            if part.function_call:
                function_call_parts.append(part.function_call)

        # Retry the request in case of malformed FCs
        if (
            not function_call_parts
            and not reasoning_text
            and hasattr(candidate, "finish_reason")
            and candidate.finish_reason == types.FinishReason.MALFORMED_FUNCTION_CALL
        ):
            return [], reasoning_text, False, None, []

        if (
            hasattr(candidate, "finish_reason")
            and candidate.finish_reason != types.FinishReason.FINISH_REASON_UNSPECIFIED
            and candidate.finish_reason != types.FinishReason.STOP
            and candidate.finish_reason != types.FinishReason.TOOL_CODE
        ):
            error_message = (
                f"Task stopped due to finish reason: {candidate.finish_reason.name}"
            )
            if (
                candidate.finish_reason == types.FinishReason.SAFETY
                and candidate.safety_ratings
            ):
                error_message += f" - Safety Ratings: {candidate.safety_ratings}"
            self.logger.error(error_message, category="agent")
            return [], reasoning_text, True, error_message, []

        if not function_call_parts:
            # Task complete or no action needed
            final_model_message = (
                reasoning_text if reasoning_text else "No further actions from model."
            )
            self.logger.info(
                f"Gemini CUA: Task appears complete or requires user input. Reason: {final_model_message}",
                category="agent",
            )
            return [], reasoning_text, True, final_model_message, []

        # Process all function calls
        agent_actions: list[AgentAction] = []
        invoked_function_info: list[tuple[str, dict[str, Any]]] = []

        for function_call_part in function_call_parts:
            action_name = function_call_part.name
            action_args = function_call_part.args
            # Store both name and args for safety acknowledgement
            invoked_function_info.append(
                (action_name, action_args if action_args else {})
            )
            action_type_str = ""
            action_payload_dict = {}

            self.logger.info(
                f"Function call part: {function_call_part}", category="agent"
            )
            # Map Google's function calls to our AgentActionType
            # This requires knowing the Pydantic models in ..types.agent
            # ClickAction, TypeAction, KeyPressAction, ScrollAction, GoToAction, WaitAction, MoveAction
            if action_name == "open_web_browser":
                action_type_str = "function"
                # For function actions, the payload for AgentActionType's root will be a FunctionAction model
                # The FunctionAction model itself needs 'type', 'name', and 'arguments'.
                action_payload_dict = {
                    "type": "function",
                    "name": "open_web_browser",
                    "arguments": None,
                }
            elif action_name == "click_at":
                action_type_str = "click"
                x, y = self._normalize_coordinates(action_args["x"], action_args["y"])
                action_payload_dict = {
                    "type": "click",
                    "x": x,
                    "y": y,
                    "button": action_args.get("button", "left"),
                }
            elif action_name == "type_text_at":
                action_type_str = "type"
                x, y = self._normalize_coordinates(action_args["x"], action_args["y"])
                action_payload_dict = {
                    "type": "type",
                    "text": action_args["text"],
                    "x": x,
                    "y": y,
                    "press_enter_after": action_args.get("press_enter", False),
                }
            elif action_name == "key_combination":
                action_type_str = "keypress"
                keys = [
                    self.key_to_playwright(key.strip())
                    for key in action_args["keys"].split("+")
                ]
                action_payload_dict = {"type": "keypress", "keys": keys}
            elif action_name == "scroll_document":
                direction = action_args["direction"].lower()
                if direction == "up":
                    action_type_str = "keypress"
                    action_payload_dict = {
                        "type": "keypress",
                        "keys": [self.key_to_playwright("PageUp")],
                    }
                elif direction == "down":
                    action_type_str = "keypress"
                    action_payload_dict = {
                        "type": "keypress",
                        "keys": [self.key_to_playwright("PageDown")],
                    }
                else:
                    self.logger.error(
                        f"Unsupported scroll direction: {direction}", category="agent"
                    )
                    return (
                        [],
                        reasoning_text,
                        True,
                        f"Unsupported scroll direction: {direction}",
                        invoked_function_info,
                    )
            elif action_name == "scroll_at":
                action_type_str = "scroll"
                x, y = self._normalize_coordinates(action_args["x"], action_args["y"])
                direction = action_args["direction"].lower()
                magnitude = action_args.get("magnitude", 800)

                # Denormalize magnitude based on direction
                if direction in ("up", "down"):
                    magnitude = self._normalize_coordinates(0, magnitude)[1]
                elif direction in ("left", "right"):
                    magnitude = self._normalize_coordinates(magnitude, 0)[0]
                else:
                    self.logger.error(
                        f"Unsupported scroll direction: {direction}", category="agent"
                    )
                    return (
                        [],
                        reasoning_text,
                        True,
                        f"Unsupported scroll direction: {direction}",
                        invoked_function_info,
                    )

                action_payload_dict = {
                    "type": "scroll",
                    "x": x,
                    "y": y,
                    "direction": direction,
                    "magnitude": magnitude,
                }
            elif action_name == "drag_and_drop":
                action_type_str = "function"
                x, y = self._normalize_coordinates(action_args["x"], action_args["y"])
                dest_x, dest_y = self._normalize_coordinates(
                    action_args["destination_x"], action_args["destination_y"]
                )
                action_payload_dict = {
                    "type": "function",
                    "name": "drag_and_drop",
                    "arguments": {
                        "x": x,
                        "y": y,
                        "destination_x": dest_x,
                        "destination_y": dest_y,
                    },
                }
            elif action_name == "navigate":
                action_type_str = "function"
                action_payload_dict = {
                    "type": "function",
                    "name": "goto",
                    "arguments": {"url": action_args["url"]},
                }
            elif action_name == "go_back":
                action_type_str = "function"
                action_payload_dict = {
                    "type": "function",
                    "name": "navigate_back",
                    "arguments": None,
                }
            elif action_name == "go_forward":
                action_type_str = "function"
                action_payload_dict = {
                    "type": "function",
                    "name": "navigate_forward",
                    "arguments": None,
                }
            elif action_name == "wait_5_seconds":
                action_type_str = "wait"
                action_payload_dict = {"type": "wait", "miliseconds": 5000}
            elif action_name == "hover_at":
                action_type_str = "move"
                x, y = self._normalize_coordinates(action_args["x"], action_args["y"])
                action_payload_dict = {"type": "move", "x": x, "y": y}
            elif action_name == "search":
                action_type_str = "function"
                action_payload_dict = {
                    "type": "function",
                    "name": "goto",
                    "arguments": {"url": "https://www.google.com"},
                }
            else:
                self.logger.error(
                    f"Unsupported Gemini CUA function: {action_name}", category="agent"
                )
                return (
                    [],
                    reasoning_text,
                    True,
                    f"Unsupported function: {action_name}",
                    invoked_function_info,
                )

            if action_payload_dict:  # Check if a payload was successfully constructed
                try:
                    # Directly construct the AgentActionType using the payload.
                    # Pydantic will use the 'type' field in action_payload_dict to discriminate the Union.
                    action_payload_for_agent_action_type = TypeAdapter(
                        AgentActionType
                    ).validate_python(action_payload_dict)

                    agent_action = AgentAction(
                        action_type=action_type_str,  # This should match the 'type' in action_payload_dict
                        action=action_payload_for_agent_action_type,
                        reasoning=reasoning_text,
                        status="tool_code",
                    )
                    agent_actions.append(agent_action)
                except Exception as e_parse:
                    self.logger.error(
                        f"Error parsing Google action '{action_name}' with payload '{action_payload_dict}': {e_parse}",
                        category="agent",
                    )
                    return (
                        [],
                        reasoning_text,
                        True,
                        f"Error parsing action: {e_parse}",
                        invoked_function_info,
                    )

        return (
            agent_actions,
            reasoning_text,
            False,
            None,
            invoked_function_info,
        )

    def _format_action_feedback(
        self,
        function_name_called: str,  # Renamed from action_type_performed for clarity with Google's terminology
        action_result: ActionExecutionResult,
        new_screenshot_base64: str,
        current_url: str,
        function_call_args: Optional[dict[str, Any]] = None,
    ) -> Content:  # Returns a single Content object to append to history

        # The response to the model is a FunctionResponse part within a user role content.
        # It should contain the result of the function call, which includes the new screenshot and URL.
        response_data: dict[str, Any] = {
            "url": current_url,
        }

        # Acknowledge safety decision for evals (auto-acknowledge like in TS implementation)
        if function_call_args and function_call_args.get("safety_decision"):
            response_data["safety_acknowledgement"] = "true"
            self.logger.info(
                "Auto-acknowledging safety decision",
                category="agent",
            )

        if not action_result["success"]:
            # Include error information if the action failed
            response_data["error"] = action_result.get("error", "Unknown error")
            self.logger.info(
                f"Formatting failed action feedback for Gemini CUA: {response_data['error']}",
                category="agent",
            )

        function_response_part = Part(
            function_response=FunctionResponse(
                name=function_name_called,
                response=response_data,
                parts=[
                    FunctionResponsePart(
                        inline_data=FunctionResponseBlob(
                            mime_type="image/png", data=new_screenshot_base64
                        )
                    )
                ],
            )
        )

        feedback_content = Content(role="user", parts=[function_response_part])
        self.history.append(feedback_content)  # Add this feedback to history
        return feedback_content

    async def run_task(
        self,
        instruction: str,
        max_steps: int = 20,
        options: Optional[AgentExecuteOptions] = None,
    ) -> AgentResult:
        self.logger.debug(
            f"Gemini CUA starting task: '{instruction}' with max_steps: {max_steps}",
            category="agent",
        )

        if not self.handler:
            self.logger.error(
                "CUAHandler not available for GoogleCUAClient.", category="agent"
            )
            return AgentResult(
                completed=False,
                actions=[],
                message="Internal error: Handler not set.",
                usage={"input_tokens": 0, "output_tokens": 0, "inference_time_ms": 0},
            )

        await self.handler.inject_cursor()
        current_screenshot_b64 = await self.handler.get_screenshot_base64()
        current_url = self.handler.page.url

        # _format_initial_messages already initializes self.history
        self._format_initial_messages(instruction, current_screenshot_b64)

        actions_taken_detail: list[AgentAction] = (
            []
        )  # To store full AgentAction objects with reasoning, etc.
        actions_taken_summary: list[AgentActionType] = (
            []
        )  # To store just the action payloads for AgentResult

        total_input_tokens = 0  # Note: Google API does not directly return token counts per call in the same way as OpenAI.
        total_output_tokens = (
            0  # We might need to estimate or rely on aggregated billing data.
        )
        total_inference_time_ms = 0

        for step_count in range(max_steps):
            self.logger.info(
                f"Gemini CUA - Step {step_count + 1}/{max_steps}",
                category="agent",
            )

            start_time = asyncio.get_event_loop().time()
            try:
                model_response = self.genai_client.models.generate_content(
                    model=self.model,
                    contents=self.history,
                    config=self._generate_content_config,
                )
                end_time = asyncio.get_event_loop().time()
                total_inference_time_ms += int((end_time - start_time) * 1000)

                # Token count handling (placeholder as Google API differs from OpenAI here)
                # For now, we won't get precise token counts from the response object directly.
                # If available through another means (e.g. response.usage_metadata), it can be added.
                if (
                    hasattr(model_response, "usage_metadata")
                    and model_response.usage_metadata
                ):
                    # Example: total_input_tokens += model_response.usage_metadata.prompt_token_count
                    # Example: total_output_tokens += model_response.usage_metadata.candidates_token_count
                    pass  # Adjust if actual fields are known

            except Exception as e:
                self.logger.error(f"Google API call failed: {e}", category="agent")
                usage_obj = {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "inference_time_ms": total_inference_time_ms,
                }
                return AgentResult(
                    actions=actions_taken_summary,
                    message=f"Google API error: {e}",
                    completed=False,  # Changed to False as task did not complete successfully
                    usage=usage_obj,
                )

            (
                agent_actions,
                reasoning_text,
                task_completed,
                final_model_message,
                invoked_function_info_list,
            ) = self._process_provider_response(model_response)

            if reasoning_text:
                self.logger.info(f"Model reasoning: {reasoning_text}", category="agent")

            if agent_actions:
                for idx, agent_action in enumerate(agent_actions):
                    actions_taken_detail.append(agent_action)
                    if agent_action.action:
                        actions_taken_summary.append(agent_action.action)

                    invoked_function_name, function_call_args = (
                        invoked_function_info_list[idx]
                    )

                    if invoked_function_name == "open_web_browser":
                        action_result: ActionExecutionResult = {
                            "success": True,
                            "error": None,
                        }
                    else:
                        action_result: ActionExecutionResult = (
                            await self.handler.perform_action(agent_action)
                        )
                        current_screenshot_b64 = (
                            await self.handler.get_screenshot_base64()
                        )
                        current_url = self.handler.page.url

                    if not invoked_function_name:
                        self.logger.error(
                            "Original Google function name not found for feedback loop (was None).",
                            category="agent",
                        )

                    self._format_action_feedback(
                        function_name_called=invoked_function_name,
                        action_result=action_result,
                        new_screenshot_base64=current_screenshot_b64,
                        current_url=current_url,
                        function_call_args=function_call_args,
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
                    actions=actions_taken_summary,
                    message=final_model_message or "Task completed.",
                    completed=True,
                    usage=usage_obj,
                )

            if not agent_action and not task_completed:
                self.logger.debug(
                    "Model did not request an action and task not marked complete. Ending task.",
                    category="agent",
                )
                usage_obj = {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "inference_time_ms": total_inference_time_ms,
                }
                return AgentResult(
                    actions=actions_taken_summary,
                    message=final_model_message or "Model provided no further actions.",
                    completed=False,  # Task did not complete as expected
                    usage=usage_obj,
                )

        self.logger.debug("Max steps reached for Gemini CUA task.", category="agent")
        usage_obj = {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "inference_time_ms": total_inference_time_ms,
        }
        return AgentResult(
            actions=actions_taken_summary,
            message="Max steps reached.",
            completed=False,
            usage=usage_obj,
        )

    def key_to_playwright(self, key: str) -> str:
        """Converts a key name if Gemini CUA uses specific names not covered by CUAHandler."""
        # This largely mirrors CUAHandler._convert_key_name, but can be adapted for Google specifics if any.
        # Google's `key_combination` takes strings like "control+c", so this function might be used to map
        # individual key names if they differ from Playwright standards *before* CUAHandler gets them.
        # However, CUAHandler already has a robust _convert_key_name. So, this client-side one
        # might only be needed if Google uses names that _convert_key_name doesn't already handle
        # or if we want to pre-process them.
        # For now, assume direct pass-through or simple mappings if Google uses very different names.
        # The CUAHandler._convert_key_name is quite comprehensive.
        # Let's make this a simple pass-through and rely on CUAHandler's conversion.
        # If Google sends "ENTER", CUAHandler will map it. If Google sends "Enter", it still works.
        # If Google has a special name like "GOOGLE_SEARCH_KEY", it would be mapped here.
        custom_map = {
            # e.g., "SpecificGoogleKey": "PlaywrightEquivalentKey"
        }
        return custom_map.get(
            key, key
        )  # Return mapped key or original if not in custom_map

    def get_text(self, candidate: Candidate) -> Optional[str]:
        """Extracts the text from the candidate."""
        text = []
        for part in candidate.content.parts:
            if part.text:
                text.append(part.text)
        return " ".join(text) or None

    def get_function_call(self, candidate: Candidate) -> Optional[types.FunctionCall]:
        """Extracts the function call from the candidate."""
        for part in candidate.content.parts:
            if part.function_call:
                return part.function_call
        return None
