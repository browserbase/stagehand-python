"""Observe handler for performing observations of page elements using LLMs."""

from typing import Any

from stagehand.llm.inference import observe as observe_inference
from stagehand.schemas import ObserveOptions, ObserveResult
from stagehand.sync.a11y.utils import (
    get_accessibility_tree,
    get_xpath_by_resolved_object_id,
)
from stagehand.utils import draw_observe_overlay


class ObserveHandler:
    """Handler for processing observe operations locally."""

    def __init__(
        self, stagehand_page, stagehand_client, user_provided_instructions=None
    ):
        """
        Initialize the ObserveHandler.

        Args:
            stagehand_page: StagehandPage instance
            stagehand_client: Stagehand client instance
            user_provided_instructions: Optional custom system instructions
        """
        self.stagehand_page = stagehand_page
        self.stagehand = stagehand_client
        self.logger = stagehand_client.logger
        self.user_provided_instructions = user_provided_instructions

    # TODO: better kwargs
    def observe(
        self,
        options: ObserveOptions,
        *request_id: str,
        from_act: bool = False,
    ) -> list[ObserveResult]:
        """
        Execute an observation operation locally.

        Args:
            options: ObserveOptions containing the instruction and other parameters
            request_id: Unique identifier for the request

        Returns:
            list of ObserveResult instances
        """
        instruction = options.instruction
        if not instruction:
            instruction = (
                "Find elements that can be used for any future actions in the page. "
                "These may be navigation links, related pages, section/subsection links, "
                "buttons, or other interactive elements. Be comprehensive: if there are "
                "multiple elements that may be relevant for future actions, return all of them."
            )

        if not from_act:
            self.logger.info(
                "Starting observation",
                category="observe",
                auxiliary={"instruction": instruction},
            )

        # Get DOM representation
        output_string = ""
        iframes = []

        self.stagehand_page._wait_for_settled_dom()
        # TODO: temporary while we define the sync version of _wait_for_settled_dom
        # self.stagehand_page.wait_for_load_state("domcontentloaded")
        # Get accessibility tree data using our utility function
        self.logger.info("Getting accessibility tree data")
        tree = get_accessibility_tree(self.stagehand_page, self.logger)
        output_string = tree["simplified"]
        iframes = tree.get("iframes", [])

        # use inference to call the llm
        observation_response = observe_inference(
            instruction=instruction,
            tree_elements=output_string,
            llm_client=self.stagehand.llm,
            request_id=request_id,
            user_provided_instructions=self.user_provided_instructions,
            logger=self.logger,
            log_inference_to_file=False,  # TODO: Implement logging to file if needed
            from_act=False,
        )

        # TODO: Update metrics for token usage
        # prompt_tokens = observation_response.get("prompt_tokens", 0)
        # completion_tokens = observation_response.get("completion_tokens", 0)
        # inference_time_ms = observation_response.get("inference_time_ms", 0)

        # Add iframes to the response if any
        elements = observation_response.get("elements", [])
        for iframe in iframes:
            elements.append(
                {
                    "element_id": int(iframe.get("nodeId", 0)),
                    "description": "an iframe",
                    "method": "not-supported",
                    "arguments": [],
                }
            )

        # Generate selectors for all elements
        elements_with_selectors = self._add_selectors_to_elements(elements)

        self.logger.info(
            "Found elements", auxiliary={"elements": elements_with_selectors}
        )

        # Draw overlay if requested
        if options.draw_overlay:
            draw_observe_overlay(self.stagehand_page, elements_with_selectors)

        return elements_with_selectors

    def _add_selectors_to_elements(
        self,
        elements: list[dict[str, Any]],
    ) -> list[ObserveResult]:
        """
        Add selectors to elements based on their element IDs.

        Args:
            elements: list of elements from LLM response

        Returns:
            list of elements with selectors added (xpaths)
        """
        result = []

        print(elements)
        for element in elements:
            element_id = element.get("element_id")
            rest = {k: v for k, v in element.items() if k != "element_id"}

            # Generate xpath for element using CDP
            self.logger.info(
                "Getting xpath for element",
                auxiliary={"elementId": str(element_id)},
            )

            args = {"backendNodeId": element_id}
            print(args)
            response = self.stagehand_page.send_cdp("DOM.resolveNode", args)
            object_id = response.get("object", {}).get("objectId")

            if not object_id:
                self.logger.info(
                    f"Invalid object ID returned for element: {element_id}"
                )
                continue

            # Use our utility function to get the XPath
            cdp_client = self.stagehand_page.get_cdp_client()
            xpath = get_xpath_by_resolved_object_id(cdp_client, object_id)

            if not xpath:
                self.logger.info(f"Empty xpath returned for element: {element_id}")
                continue

            result.append(ObserveResult(**{**rest, "selector": f"xpath={xpath}"}))

        return result
