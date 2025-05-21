"""Inference module for calling LLMs to perform various tasks."""

import json
import time
from typing import Any, Callable, Optional, Union

from pydantic import BaseModel

from stagehand.llm.prompts import (
    build_extract_system_prompt,
    build_extract_user_prompt,
    build_metadata_prompt,
    build_metadata_system_prompt,
    build_observe_system_prompt,
    build_observe_user_message,
)
from stagehand.types import (
    MetadataSchema,
    ObserveInferenceSchema,
)


# TODO: kwargs
def observe(
    instruction: str,
    tree_elements: str,
    llm_client: Any,
    user_provided_instructions: Optional[str] = None,
    logger: Optional[Callable] = None,
    log_inference_to_file: bool = False,
    from_act: bool = False,
) -> dict[str, Any]:
    """
    Call LLM to find elements in the DOM/accessibility tree based on an instruction.

    Args:
        instruction: The instruction to follow when finding elements
        tree_elements: String representation of DOM/accessibility tree elements
        llm_client: Client for calling LLM
        user_provided_instructions: Optional custom system instructions
        logger: Optional logger function
        log_inference_to_file: Whether to log inference to file
        from_act: Whether this observe call is part of an act operation

    Returns:
        dict containing elements found and token usage information
    """

    # Build the prompts
    system_prompt = build_observe_system_prompt(
        user_provided_instructions=user_provided_instructions,
    )

    user_prompt = build_observe_user_message(
        instruction=instruction,
        tree_elements=tree_elements,
    )

    messages = [
        system_prompt,
        user_prompt,
    ]

    start_time = time.time()

    try:
        # Call the LLM
        logger.info("Calling LLM")
        response = llm_client.create_response(
            model=llm_client.default_model,
            messages=messages,
            response_format=ObserveInferenceSchema,
            temperature=0.1,
            function_name="ACT" if from_act else "OBSERVE",
        )
        inference_time_ms = int((time.time() - start_time) * 1000)

        # Extract token counts
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens

        # Parse the response
        content = response.choices[0].message.content
        logger.info("Got LLM response")
        logger.debug(
            "LLM Response",
            auxiliary={
                "content": content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "inference_time_ms": inference_time_ms,
            },
        )
        if isinstance(content, str):
            try:
                parsed_response = json.loads(content)
            except json.JSONDecodeError:
                if logger:
                    logger.error(f"Failed to parse JSON response: {content}")
                parsed_response = {"elements": []}
        else:
            parsed_response = content

        elements = parsed_response.get("elements", [])

        return {
            "elements": elements,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "inference_time_ms": inference_time_ms,
        }

    except Exception as e:
        if logger:
            logger.error(f"Error in observe inference: {str(e)}")

        # Return empty response on error
        return {
            "elements": [],
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "inference_time_ms": int((time.time() - start_time) * 1000),
        }


def extract(
    instruction: str,
    tree_elements: str,
    schema: Optional[Union[type[BaseModel], dict]] = None,
    llm_client: Any = None,
    user_provided_instructions: Optional[str] = None,
    logger: Optional[Callable] = None,
    log_inference_to_file: bool = False,
    is_using_text_extract: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Call LLM to extract structured data from the page based on the provided instruction and schema.

    Args:
        instruction: The instruction for what data to extract
        tree_elements: The DOM or accessibility tree representation
        schema: Pydantic model defining the structure of the data to extract
        llm_client: The LLM client to use for the request
        user_provided_instructions: Optional custom system instructions
        logger: Logger instance for logging
        log_inference_to_file: Whether to log inference to file
        is_using_text_extract: Whether using text extraction (vs. DOM/a11y tree)
        **kwargs: Additional parameters to pass to the LLM client

    Returns:
        dict containing the extraction results and metadata
    """
    logger.info("Calling LLM")

    # Create system and user messages for extraction
    system_message = build_extract_system_prompt(
        is_using_text_extract=is_using_text_extract,
        user_provided_instructions=user_provided_instructions,
    )
    user_message = build_extract_user_prompt(instruction, tree_elements)

    extract_messages = [
        system_message,
        user_message,
    ]

    # Call LLM for extraction
    start_time = time.time()

    # Determine if we need to use schema-based response format
    # TODO: if schema is json, return json
    response_format = {"type": "json_object"}
    if schema:
        # If schema is a Pydantic model, use it directly
        response_format = schema

    # Call the LLM with appropriate parameters
    try:
        extract_response = llm_client.create_response(
            model=llm_client.default_model,
            messages=extract_messages,
            response_format=response_format,
            temperature=0.1,
            function_name="EXTRACT",  # Always set to EXTRACT
            **kwargs,
        )
        extract_time_ms = int((time.time() - start_time) * 1000)

        # Extract token counts
        prompt_tokens = extract_response.usage.prompt_tokens
        completion_tokens = extract_response.usage.completion_tokens

        # Parse the response
        extract_content = extract_response.choices[0].message.content
        if isinstance(extract_content, str):
            try:
                extracted_data = json.loads(extract_content)
            except json.JSONDecodeError:
                logger.error(
                    f"Failed to parse JSON extraction response: {extract_content}"
                )
                extracted_data = {}
        else:
            extracted_data = extract_content
    except Exception as e:
        logger.error(f"Error in extract inference: {str(e)}")

        # In case of failure, return empty data
        extracted_data = {}
        prompt_tokens = 0
        completion_tokens = 0
        extract_time_ms = int((time.time() - start_time) * 1000)

    # Generate metadata about the extraction
    metadata_system_message = build_metadata_system_prompt()
    metadata_user_message = build_metadata_prompt(instruction, extracted_data, 1, 1)

    metadata_messages = [
        metadata_system_message,
        metadata_user_message,
    ]

    # Define the metadata schema
    metadata_schema = MetadataSchema

    # Call LLM for metadata
    try:
        metadata_start_time = time.time()
        metadata_response = llm_client.create_response(
            model=llm_client.default_model,
            messages=metadata_messages,
            response_format=metadata_schema,
            temperature=0.1,
            function_name="EXTRACT",  # Metadata for extraction should also be tracked as EXTRACT
        )
        metadata_end_time = time.time()
        metadata_time_ms = int((metadata_end_time - metadata_start_time) * 1000)
        logger.info("Got LLM response")

        # Extract metadata content
        metadata_content = metadata_response.choices[0].message.content

        # Parse metadata content
        if isinstance(metadata_content, str):
            try:
                metadata = json.loads(metadata_content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse metadata response: {metadata_content}")
                metadata = {"completed": False, "progress": "Failed to parse metadata"}
        else:
            metadata = metadata_content

        # Get token usage for metadata
        metadata_prompt_tokens = metadata_response.usage.prompt_tokens
        metadata_completion_tokens = metadata_response.usage.completion_tokens
    except Exception as e:
        logger.error(f"Error in metadata inference: {str(e)}")

        # In case of failure, use default metadata
        metadata = {"completed": False, "progress": "Metadata generation failed"}
        metadata_prompt_tokens = 0
        metadata_completion_tokens = 0
        metadata_time_ms = 0

    # Calculate total tokens and time
    total_prompt_tokens = prompt_tokens + metadata_prompt_tokens
    total_completion_tokens = completion_tokens + metadata_completion_tokens
    total_inference_time_ms = extract_time_ms + metadata_time_ms

    # Create the final result
    result = {
        "data": extracted_data,
        "metadata": metadata,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "inference_time_ms": total_inference_time_ms,
    }

    logger.debug(
        "LLM response",
        auxiliary={
            "metadata": metadata,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "inference_time_ms": total_inference_time_ms,
        },
    )

    return result
