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
        self, stagehand_page, stagehand_client, user_provided_instructions=None
    ):
        """
        Initialize the ActHandler.

        Args:
            stagehand_page: StagehandPage instance
            stagehand_client: Stagehand client instance
            user_provided_instructions: Optional custom system instructions
        """
        self.stagehand_page = stagehand_page
        self.stagehand = stagehand_client
        self.logger = stagehand_client.logger
        self.user_provided_instructions = user_provided_instructions

    async def act(self, options: Union[ActOptions, ObserveResult]) -> ActResult:
        """
        Perform an act based on an instruction.
        This method will observe the page and then perform the act on the first element returned.
        """
        if "selector" in options and "method" in options:
            options = ObserveResult(**options)
            return await self._act_from_observe_result(options)

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

        observe_results: list[ObserveResult] = (
            await self.stagehand_page._observe_handler.observe(
                observe_options, from_act=True
            )
        )

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

    async def _act_from_observe_result(
        self, observe_result: ObserveResult
    ) -> ActResult:
        # This method in the original TypeScript (`actFromObserveResult`) contained logic
        # for self-healing if an action failed, by re-observing and trying again.
        # The current `act` method above has been refactored to call `_perform_playwright_method`
        # directly after the initial observe. To restore self-healing, this method would need
        # to be fully implemented with that logic, and `act` would call this method.
        self.logger.debug(
            message="_act_from_observe_result called",
            category="act",
            auxiliary={
                "observe_result": (
                    observe_result.model_dump_json()
                    if hasattr(observe_result, "model_dump_json")
                    else str(observe_result)
                )
            },
        )

        # Placeholder: The actual implementation of self-healing would go here.
        # For now, it just logs and indicates it's not fully implemented to match TS.
        action_description = (
            observe_result.description
            or f"ObserveResult action ({observe_result.method})"
        )
        try:
            await self._perform_playwright_method(
                method=observe_result.method,
                args=observe_result.arguments or [],
                xpath=observe_result.selector.replace("xpath=", ""),
            )
            return ActResult(
                success=True,
                message=f"Action [{observe_result.method}] performed successfully on selector: {observe_result.selector}",
                action=observe_result.description
                or f"ObserveResult action ({observe_result.method})",
            )
        except Exception as e:
            self.logger.error(
                message=f"{str(e)}",
            )
            return ActResult(
                success=False,
                message=f"Failed to perform act: {str(e)}",
                action=action_description,
            )
        # This would typically attempt the action, catch errors, and then potentially call
        # self.stagehand_page.act(...) with the original instruction for self-healing.

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
                self.logger.warning(
                    message="chosen method is invalid",
                    category="act",
                    auxiliary={"method": {"value": method, "type": "string"}},
                )

            await self.stagehand_page._wait_for_settled_dom(dom_settle_timeout_ms)
        except Exception as e:
            self.logger.error(
                message=f"{str(e)}",
            )
