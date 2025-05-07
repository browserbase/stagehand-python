import json
from typing import Any, Optional

from stagehand.handlers.act_handler_utils import method_handler_map
from stagehand.types.llm import ChatMessage


def build_user_instructions_string(
    user_provided_instructions: Optional[str] = None,
) -> str:
    if not user_provided_instructions:
        return ""

    return f"""

# Custom Instructions Provided by the User

Please keep the user's instructions in mind when performing actions. If the user's instructions are not relevant to the current task, ignore them.

User Instructions:
{user_provided_instructions}"""


# extract
def build_extract_system_prompt(
    is_anthropic: bool = False, 
    is_using_text_extract: bool = False,
    user_provided_instructions: str = None
) -> str:
    """
    Build the system prompt for extraction.

    Args:
        is_anthropic: Whether we're using an Anthropic model
        is_using_text_extract: Whether we're using text extraction
        user_provided_instructions: Optional custom system instructions

    Returns:
        System prompt for extract
    """
    if user_provided_instructions:
        return user_provided_instructions

    human_prefix = "<human>: " if is_anthropic else ""
    assistant_prefix = "<assistant>: " if is_anthropic else ""
    
    extract_instructions = f"""You are an AI assistant capable of extracting structured information from web pages.

Your job is to extract specific information as requested by the user from the web page content that is provided.

The user will provide:
1. An instruction about what information to extract
2. A representation of the web page content

You should:
1. Carefully analyze the page content
2. Extract the information according to the user's instructions
3. Return the results in a structured format, following the required schema

Follow these guidelines:
- Extract exactly what was asked for, no more and no less
- If a piece of information is not in the page content, leave the corresponding field empty or null
- Do not make up information or hallucinate data not present in the content
- Be precise and accurate in your extraction
"""

    if is_using_text_extract:
        extract_instructions += """
Note: The page content provided includes positional information about where text appears on the page. This is represented as lines of text with annotations about their positions. Focus on extracting the relevant information while disregarding the positional details.
"""

    return extract_instructions


def build_extract_user_prompt(
    instruction: str, dom_elements: str, is_anthropic: bool = False
) -> str:
    """
    Build the user prompt for extraction.

    Args:
        instruction: The instruction for what to extract
        dom_elements: The DOM representation or text content
        is_anthropic: Whether we're using an Anthropic model

    Returns:
        User prompt for extract
    """
    human_prefix = "<human>: " if is_anthropic else ""
    
    if not instruction:
        instruction = "Extract all the relevant information from this page."
    
    return f"""Instruction: {instruction}

Page content:
{dom_elements}
"""


refine_system_prompt = """You are tasked with refining and filtering information for the final output based on newly extracted and previously extracted content. Your responsibilities are:
1. Remove exact duplicates for elements in arrays and objects.
2. For text fields, append or update relevant text if the new content is an extension, replacement, or continuation.
3. For non-text fields (e.g., numbers, booleans), update with new values if they differ.
4. Add any completely new fields or objects ONLY IF they correspond to the provided schema.

Return the updated content that includes both the previous content and the new, non-duplicate, or extended information."""


def build_refine_system_prompt() -> ChatMessage:
    return ChatMessage(role="system", content=refine_system_prompt)


def build_refine_user_prompt(
    instruction: str,
    previously_extracted_content: dict[str, Any],
    newly_extracted_content: dict[str, Any],
) -> ChatMessage:
    return ChatMessage(
        role="user",
        content=f"""Instruction: {instruction}
Previously extracted content: {json.dumps(previously_extracted_content, indent=2)}
Newly extracted content: {json.dumps(newly_extracted_content, indent=2)}
Refined content:""",
    )


def build_metadata_system_prompt() -> str:
    """
    Build the system prompt for metadata extraction.

    Returns:
        System prompt for metadata
    """
    return """You are an AI assistant that evaluates the completeness of information extraction.

Given:
1. An extraction instruction
2. The extracted data

Your task is to:
1. Determine if the extraction is complete based on the instruction
2. Provide a brief progress summary

Please respond with:
- "completed": A boolean indicating if the extraction is complete (true) or not (false)
- "progress": A brief summary of the extraction progress
"""


def build_metadata_prompt(
    instruction: str, extracted_data: dict, chunks_seen: int, chunks_total: int
) -> str:
    """
    Build the user prompt for metadata extraction.

    Args:
        instruction: The original extraction instruction
        extracted_data: The data that was extracted
        chunks_seen: Number of chunks processed
        chunks_total: Total number of chunks

    Returns:
        User prompt for metadata
    """
    return f"""Extraction instruction: {instruction}

Extracted data: {extracted_data}

Chunks processed: {chunks_seen} of {chunks_total}

Evaluate if this extraction is complete according to the instruction.
"""


# observe
def build_observe_system_prompt(
    user_provided_instructions: Optional[str] = None,
) -> ChatMessage:
    tree_type_desc = "a hierarchical accessibility tree showing the semantic structure of the page. The tree is a hybrid of the DOM and the accessibility tree."

    observe_system_prompt_base = f"""
You are helping the user automate the browser by finding elements based on what the user wants to observe in the page.

You will be given:
1. an instruction of elements to observe
2. {tree_type_desc}

Return an array of elements that match the instruction if they exist, otherwise return an empty array. Whenever suggesting actions, use supported playwright locator methods or preferably one of the following supported actions:
{', '.join(method_handler_map.keys())}"""

    content = " ".join(observe_system_prompt_base.split())
    user_instructions_str = build_user_instructions_string(user_provided_instructions)

    final_content = content
    if user_instructions_str:
        final_content += "\n\n" + user_instructions_str

    return ChatMessage(
        role="system",
        content=final_content,
    )


def build_observe_user_message(
    instruction: str,
    tree_elements: str,
) -> ChatMessage:
    tree_or_dom = "Accessibility Tree"
    return ChatMessage(
        role="user",
        content=f"""instruction: {instruction}
{tree_or_dom}: {tree_elements}""",
    )


def build_act_observe_prompt(
    action: str,
    supported_actions: list[str],
    variables: Optional[dict[str, str]] = None,
) -> str:
    """
    Builds the instruction for the observeAct method to find the most relevant element for an action
    """
    instruction = f"""Find the most relevant element to perform an action on given the following action: {action}.
Provide an action for this element such as {', '.join(supported_actions)}, or any other playwright locator method. Remember that to users, buttons and links look the same in most cases.
If the action is completely unrelated to a potential action to be taken on the page, return an empty array.
ONLY return one action. If multiple actions are relevant, return the most relevant one.
If the user is asking to scroll to a position on the page, e.g., 'halfway' or 0.75, etc, you must return the argument formatted as the correct percentage, e.g., '50%' or '75%', etc.
If the user is asking to scroll to the next chunk/previous chunk, choose the nextChunk/prevChunk method. No arguments are required here.
If the action implies a key press, e.g., 'press enter', 'press a', 'press space', etc., always choose the press method with the appropriate key as argument — e.g. 'a', 'Enter', 'Space'. Do not choose a click action on an on-screen keyboard. Capitalize the first character like 'Enter', 'Tab', 'Escape' only for special keys."""

    if variables and len(variables) > 0:
        variables_prompt = f"The following variables are available to use in the action: {', '.join(variables.keys())}. Fill the argument variables with the variable name."
        instruction += f" {variables_prompt}"

    return instruction


def build_operator_system_prompt(goal: str) -> ChatMessage:
    return ChatMessage(
        role="system",
        content=f"""You are a general-purpose agent whose job is to accomplish the user's goal across multiple model calls by running actions on the page.

You will be given a goal and a list of steps that have been taken so far. Your job is to determine if either the user's goal has been completed or if there are still steps that need to be taken.

# Your current goal
{goal}

# Important guidelines
1. Break down complex actions into individual atomic steps
2. For `act` commands, use only one action at a time, such as:
   - Single click on a specific element
   - Type into a single input field
   - Select a single option
3. Avoid combining multiple actions in one instruction
4. If multiple actions are needed, they should be separate steps""",
    )
