import traceback
from typing import Any, Optional, Union

from stagehand.handlers.act_handler_utils import (
    MethodHandlerContext,
    fallback_locator_method,
    method_handler_map,
)
from stagehand.llm.prompts import build_act_observe_prompt
from stagehand.types import ActOptions, ActResult, ObserveOptions, ObserveResult


class ActHandler:
    """Handler for processing observe operations locally."""

    def __init__(
        self,
        stagehand_page,
        stagehand_client,
        user_provided_instructions=None,
        self_heal: bool = True,
    ):
        """
        Initialize the ActHandler.

        Args:
            stagehand_page: StagehandPage instance
            stagehand_client: Stagehand client instance
            user_provided_instructions: Optional custom system instructions
            self_heal: Whether to attempt self-healing on failed actions from ObserveResult.
        """
        self.stagehand_page = stagehand_page
        self.stagehand = stagehand_client
        self.logger = stagehand_client.logger
        self.user_provided_instructions = user_provided_instructions
        self.self_heal = self_heal

    async def act(self, options: Union[ActOptions, ObserveResult]) -> ActResult:
        """
        Perform an act based on an instruction.
        This method will observe the page and then perform the act on the first element returned.
        """
        if "selector" in options and "method" in options:
            options = ObserveResult(**options)
            return await self._act_from_observe_result(
                options, self.stagehand.dom_settle_timeout_ms
            )

        # Start inference timer if available
        if hasattr(self.stagehand, "start_inference_timer"):
            self.stagehand.start_inference_timer()

        action_task = options.get("action")
        self.logger.info(
            f"Starting action for task: '{action_task}'",
            category="act",
        )
        prompt = build_act_observe_prompt(
            action=action_task,
            supported_actions=list(method_handler_map.keys()),
            variables=options.get("variables"),
        )

        observe_options_dict = {"instruction": prompt}
        # Add other observe options from ActOptions if they exist
        if options.get("model_name"):
            observe_options_dict["model_name"] = options.get("model_name")
        if options.get("model_client_options"):
            observe_options_dict["model_client_options"] = options.get(
                "model_client_options"
            )

        observe_options = ObserveOptions(**observe_options_dict)

        try:
            observe_results: list[ObserveResult] = (
                await self.stagehand_page._observe_handler.observe(
                    observe_options, from_act=True
                )
            )

            # The metrics are now updated in ObserveHandler directly
            if hasattr(self.stagehand, "get_inference_time_ms"):
                self.stagehand.get_inference_time_ms()  # Just call the method without assigning

            if not observe_results:
                return ActResult(
                    success=False,
                    message="No observe results found for action",
                    action=action_task,
                )

            element_to_act_on = observe_results[0]

            # Substitute variables in arguments
            if options.get("variables"):
                variables = options.get("variables", {})
                element_to_act_on.arguments = [
                    str(arg).replace(f"%{key}%", str(value))
                    for arg in (element_to_act_on.arguments or [])
                    for key, value in variables.items()
                ]

            # domSettleTimeoutMs might come from options if specified for act
            dom_settle_timeout_ms = options.get("dom_settle_timeout_ms")

            try:
                await self._perform_playwright_method(
                    method=element_to_act_on.method,
                    args=element_to_act_on.arguments or [],
                    xpath=element_to_act_on.selector.replace("xpath=", ""),
                    dom_settle_timeout_ms=dom_settle_timeout_ms,
                )
                return ActResult(
                    success=True,
                    message=f"Action [{element_to_act_on.method}] performed successfully on selector: {element_to_act_on.selector}",
                    action=element_to_act_on.description
                    or f"ObserveResult action ({element_to_act_on.method})",
                )
            except Exception as e:
                self.logger.error(
                    message=f"{str(e)}",
                )
                return ActResult(
                    success=False,
                    message=f"Failed to perform act: {str(e)}",
                    action=action_task,
                )
        except Exception as e:
            self.logger.error(
                message=f"Error in act: {str(e)}",
                category="act",
                auxiliary={"exception": str(e), "stack_trace": traceback.format_exc()},
            )
            return ActResult(
                success=False,
                message=f"Failed to perform act: {str(e)}",
                action=action_task,
            )

    async def _act_from_observe_result(
        self, observe_result: ObserveResult, dom_settle_timeout_ms: Optional[int] = None
    ) -> ActResult:

        self.logger.debug(
            message="_act_from_observe_result called",
            category="act",
            auxiliary={
                "observe_result": (
                    observe_result.model_dump_json()
                    if hasattr(observe_result, "model_dump_json")
                    else str(observe_result)
                ),
                "dom_settle_timeout_ms": dom_settle_timeout_ms,
            },
        )

        if observe_result.method == "not-supported":
            self.logger.error(
                message="Cannot execute ObserveResult with unsupported method",
                category="act",
                auxiliary={
                    "error": {
                        "value": (
                            "NotSupportedError: The method requested in this ObserveResult is not supported by Stagehand."
                        ),
                        "type": "string",
                    },
                    "trace": {
                        "value": (
                            f"Cannot execute act from ObserveResult with unsupported method: {observe_result.method}"
                        ),
                        "type": "string",
                    },
                },
            )
            return ActResult(
                success=False,
                message=f"Unable to perform action: The method '{observe_result.method}' is not supported in ObserveResult. Please use a supported Playwright locator method.",
                action=observe_result.description
                or f"ObserveResult action ({observe_result.method})",
            )

        action_description = (
            observe_result.description
            or f"ObserveResult action ({observe_result.method})"
        )
        self.logger.info(
            message=f"Attempting to perform action: {action_description}",
            category="act",
        )
        try:
            await self._perform_playwright_method(
                method=observe_result.method,
                args=observe_result.arguments or [],
                xpath=observe_result.selector.replace("xpath=", ""),
                dom_settle_timeout_ms=dom_settle_timeout_ms,
            )
            return ActResult(
                success=True,
                message=f"Action [{observe_result.method}] performed successfully on selector: {observe_result.selector}",
                action=action_description,
            )
        except Exception as e:
            self.logger.error(
                message=f"Error performing act from ObserveResult: {str(e)}",
                category="act",
                auxiliary={"exception": str(e), "stack_trace": traceback.format_exc()},
            )

            if not self.self_heal:
                return ActResult(
                    success=False,
                    message=f"Failed to perform act: {str(e)}",
                    action=action_description,
                )

            # Construct act_command for self-heal
            method_name = observe_result.method
            current_description = observe_result.description or ""

            if current_description.lower().startswith(method_name.lower()):
                act_command = current_description
            elif method_name:  # method_name is not None/empty
                act_command = f"{method_name} {current_description}".strip()
            else:  # method_name is None or empty
                act_command = current_description

            if (
                not act_command
            ):  # If both method and description were empty or resulted in an empty command
                self.logger.error(
                    "Self-heal attempt aborted: could not construct a valid command from ObserveResult.",
                    category="act",
                    auxiliary={
                        "observe_result": (
                            observe_result.model_dump_json()
                            if hasattr(observe_result, "model_dump_json")
                            else str(observe_result)
                        )
                    },
                )
                return ActResult(
                    success=False,
                    message=f"Failed to perform act: {str(e)}. Self-heal aborted due to empty command.",
                    action=action_description,
                )

            try:
                self.logger.info(
                    f"Attempting self-heal by calling page.act with command: '{act_command}'",
                    category="act",
                )
                # This will go through the full act flow, including a new observe if necessary
                return await self.stagehand_page.act(act_command)
            except Exception as fallback_e:
                self.logger.error(
                    message=f"Error performing act on fallback self-heal attempt: {str(fallback_e)}",
                    category="act",
                    auxiliary={
                        "exception": str(fallback_e),
                        "stack_trace": traceback.format_exc(),
                    },
                )
                return ActResult(
                    success=False,
                    message=f"Failed to perform act on fallback: {str(fallback_e)}",
                    action=action_description,  # Original action description
                )

    async def _perform_playwright_method(
        self,
        method: str,
        args: list[Any],
        xpath: str,
        dom_settle_timeout_ms: Optional[int] = None,
    ):
        locator = self.stagehand_page._page.locator(f"xpath={xpath}").first
        initial_url = self.stagehand_page._page.url

        self.logger.debug(
            message="performing playwright method",
            category="act",
            auxiliary={
                "xpath": {"value": xpath, "type": "string"},
                "method": {"value": method, "type": "string"},
            },
        )

        context = MethodHandlerContext(
            method=method,
            locator=locator,
            xpath=xpath,
            args=args,
            logger=self.logger,
            stagehand_page=self.stagehand_page,
            initial_url=initial_url,
            dom_settle_timeout_ms=dom_settle_timeout_ms,
        )

        try:
            method_fn = method_handler_map.get(method)

            if method_fn:
                await method_fn(context)
            # Check if the method exists on the locator object and is callable
            elif hasattr(locator, method) and callable(getattr(locator, method)):
                await fallback_locator_method(context)
            else:
                self.logger.error(
                    message="chosen method is invalid",
                    category="act",
                    auxiliary={"method": {"value": method, "type": "string"}},
                )

            await self.stagehand_page._wait_for_settled_dom(dom_settle_timeout_ms)
        except Exception as e:
            self.logger.error(
                message=f"{str(e)}",
            )
            raise e
