"""Extract handler for performing data extraction from page elements using LLMs."""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from stagehand.a11y.utils import get_accessibility_tree, get_xpath_by_resolved_object_id
from stagehand.llm.inference import extract as extract_inference
from stagehand.schemas import ExtractOptions, ExtractResult
from stagehand.utils import transform_url_strings_to_ids, inject_urls


T = TypeVar('T', bound=BaseModel)


class ExtractHandler:
    """Handler for processing extract operations locally."""

    def __init__(
        self, stagehand_page, stagehand_client, user_provided_instructions=None
    ):
        """
        Initialize the ExtractHandler.

        Args:
            stagehand_page: StagehandPage instance
            stagehand_client: Stagehand client instance
            user_provided_instructions: Optional custom system instructions
        """
        self.stagehand_page = stagehand_page
        self.stagehand = stagehand_client
        self.logger = stagehand_client.logger
        self.user_provided_instructions = user_provided_instructions

    async def extract(
        self,
        options: Optional[ExtractOptions] = None,
        request_id: str = "",
        schema: Optional[Type[BaseModel]] = None,
    ) -> ExtractResult:
        """
        Execute an extraction operation locally.

        Args:
            options: ExtractOptions containing the instruction and other parameters
            request_id: Unique identifier for the request
            schema: Optional Pydantic model for structured output

        Returns:
            ExtractResult instance
        """
        if not options:
            # If no options provided, extract the entire page text
            self.logger.info("Extracting entire page text")
            return await self._extract_page_text()
        
        instruction = options.instruction
        selector = options.selector

        self.logger.info(
            "Starting extraction",
            category="extract",
            auxiliary={"instruction": instruction},
        )

        # Wait for DOM to settle
        await self.stagehand_page._wait_for_settled_dom()

        # Get DOM representation using accessibility tree
        target_xpath = selector.replace("xpath=", "") if selector and selector.startswith("xpath=") else ""
        
        # Get accessibility tree data
        tree = await get_accessibility_tree(self.stagehand_page, self.logger)
        self.logger.info("Getting accessibility tree data")
        output_string = tree["simplified"]
        id_to_url_mapping = tree.get("idToUrl", {})

        # Transform schema URL fields to numeric IDs if necessary
        transformed_schema = schema
        url_paths = []
        if schema:
            # TODO: Remove this once we have a better way to handle URLs
            transformed_schema, url_paths = transform_url_strings_to_ids(schema)

        # Use inference to call the LLM
        extraction_response = extract_inference(
            instruction=instruction,
            dom_elements=output_string,
            schema=transformed_schema,
            llm_client=self.stagehand.llm,
            request_id=request_id,
            user_provided_instructions=self.user_provided_instructions,
            logger=self.logger,
            log_inference_to_file=False,  # TODO: Implement logging to file if needed
        )

        # Process extraction response
        result = extraction_response.get("data", {})
        metadata = extraction_response.get("metadata", {})
        prompt_tokens = extraction_response.get("prompt_tokens", 0)
        completion_tokens = extraction_response.get("completion_tokens", 0)
        inference_time_ms = extraction_response.get("inference_time_ms", 0)

        # Inject URLs back into result if necessary
        if url_paths:
            inject_urls(result, url_paths, id_to_url_mapping)

        self.logger.info(
            "Extraction completed",
            auxiliary={
                "metadata": metadata,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "inference_time_ms": inference_time_ms,
            },
        )

        # Create ExtractResult object
        return ExtractResult(
            data=result,
            metadata=metadata,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            inference_time_ms=inference_time_ms,
        )

    async def _extract_page_text(self) -> ExtractResult:
        """Extract just the text content from the page."""
        await self.stagehand_page._wait_for_settled_dom()
        
        # Get page text using DOM evaluation
        # I don't love using js inside of python
        page_text = await self.stagehand_page.page.evaluate("""
            () => {
                // Simple function to get all visible text from the page
                function getVisibleText(node) {
                    let text = '';
                    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                        text += node.textContent.trim() + ' ';
                    } else if (node.nodeType === Node.ELEMENT_NODE) {
                        const style = window.getComputedStyle(node);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            for (const child of node.childNodes) {
                                text += getVisibleText(child);
                            }
                        }
                    }
                    return text;
                }
                
                return getVisibleText(document.body).trim();
            }
        """)
        
        return ExtractResult(
            data={"page_text": page_text},
            metadata={"completed": True},
            prompt_tokens=0,
            completion_tokens=0,
            inference_time_ms=0,
        ) 