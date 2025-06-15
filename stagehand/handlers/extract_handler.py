"""Extract handler for performing data extraction from page elements using LLMs."""

from typing import Optional, TypeVar

from pydantic import BaseModel

from stagehand.a11y.utils import get_accessibility_tree
from stagehand.llm.inference import extract as extract_inference
from stagehand.metrics import StagehandFunctionName  # Changed import location
from stagehand.types import DefaultExtractSchema, ExtractOptions, ExtractResult
from stagehand.utils import inject_urls, transform_url_strings_to_ids

T = TypeVar("T", bound=BaseModel)


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
        schema: Optional[type[BaseModel]] = None,
    ) -> ExtractResult:
        """
        Execute an extraction operation locally.

        Args:
            options: ExtractOptions containing the instruction and other parameters
            schema: Optional Pydantic model for structured output

        Returns:
            ExtractResult instance
        """
        if not options:
            # If no options provided, extract the entire page text
            self.logger.info("Extracting entire page text")
            return await self._extract_page_text()

        instruction = options.instruction
        # TODO add targeted extract
        # selector = options.selector

        # TODO: add schema to log
        self.logger.debug(
            "extract",
            category="extract",
            auxiliary={"instruction": instruction},
        )
        self.logger.info(
            f"Starting extraction with instruction: '{instruction}'", category="extract"
        )

        # Start inference timer if available
        if hasattr(self.stagehand, "start_inference_timer"):
            self.stagehand.start_inference_timer()

        # Wait for DOM to settle
        await self.stagehand_page._wait_for_settled_dom()

        # TODO add targeted extract
        # target_xpath = (
        #     selector.replace("xpath=", "")
        #     if selector and selector.startswith("xpath=")
        #     else ""
        # )

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
        else:
            schema = transformed_schema = DefaultExtractSchema

        # Use inference to call the LLM
        extraction_response = extract_inference(
            instruction=instruction,
            tree_elements=output_string,
            schema=transformed_schema,
            llm_client=self.stagehand.llm,
            user_provided_instructions=self.user_provided_instructions,
            logger=self.logger,
            log_inference_to_file=False,  # TODO: Implement logging to file if needed
        )

        # Extract metrics from response and update them directly
        prompt_tokens = extraction_response.get("prompt_tokens", 0)
        completion_tokens = extraction_response.get("completion_tokens", 0)
        inference_time_ms = extraction_response.get("inference_time_ms", 0)

        # Update metrics directly using the Stagehand client
        self.stagehand.update_metrics(
            StagehandFunctionName.EXTRACT,
            prompt_tokens,
            completion_tokens,
            inference_time_ms,
        )

        # Process extraction response
        raw_data_dict = extraction_response.get("data", {})
        metadata = extraction_response.get("metadata", {})

        # Inject URLs back into result if necessary
        if url_paths:
            inject_urls(
                raw_data_dict, url_paths, id_to_url_mapping
            )  # Modifies raw_data_dict in place

        if metadata.get("completed"):
            self.logger.debug(
                "Extraction completed successfully",
                auxiliary={"result": raw_data_dict},
            )
        else:
            self.logger.debug(
                "Extraction incomplete after processing all data",
                auxiliary={"result": raw_data_dict},
            )

        processed_data_payload = raw_data_dict  # Default to the raw dictionary

        if schema and isinstance(
            raw_data_dict, dict
        ):  # schema is the Pydantic model type
            try:
                validated_model_instance = schema.model_validate(raw_data_dict)
                processed_data_payload = validated_model_instance  # Payload is now the Pydantic model instance
            except Exception as e:
                self.logger.error(
                    f"Failed to validate extracted data against schema {schema.__name__}: {e}. Keeping raw data dict in .data field."
                )

        # Create ExtractResult object
        result = ExtractResult(
            data=processed_data_payload,
        )

        return result

    async def _extract_page_text(self) -> ExtractResult:
        """Extract just the text content from the page."""
        await self.stagehand_page._wait_for_settled_dom()

        tree = await get_accessibility_tree(self.stagehand_page, self.logger)
        output_string = tree["simplified"]
        return ExtractResult(data=output_string)
