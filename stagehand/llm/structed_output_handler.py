import json
from pydantic import BaseModel, ValidationError
from typing import Any, Final, Type
from collections.abc import Callable
from copy import deepcopy
import re
from litellm import completion, acompletion 

LITE_AGENT_RESPONSE_FORMAT: Final[str] = "Ensure your final answer strictly adheres to the following OpenAPI schema: {response_format}\n\nDo not include the OpenAPI schema in the final output. Ensure the final output does not include any code block markers like ```json or ```python."
FORMATTED_TASK_INSTRUCTIONS: Final[str] = "Ensure your final answer strictly adheres to the following OpenAPI schema: {output_format}\n\nDo not include the OpenAPI schema in the final output. Ensure the final output does not include any code block markers like ```json or ```python."
_JSON_PATTERN: Final[re.Pattern[str]] = re.compile(r"({.*})", re.DOTALL)


def resolve_refs(schema: dict[str, Any]) -> dict[str, Any]:
    """Recursively resolve all local $refs in the given JSON Schema using $defs as the source.

    This is needed because Pydantic generates $ref-based schemas that
    some consumers (e.g. LLMs, tool frameworks) don't handle well.

    Args:
        schema: JSON Schema dict that may contain "$refs" and "$defs".

    Returns:
        A new schema dictionary with all local $refs replaced by their definitions.
    """
    defs = schema.get("$defs", {})
    schema_copy = deepcopy(schema)

    def _resolve(node: Any) -> Any:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                def_name = ref.replace("#/$defs/", "")
                if def_name in defs:
                    return _resolve(deepcopy(defs[def_name]))
                raise KeyError(f"Definition '{def_name}' not found in $defs.")
            return {k: _resolve(v) for k, v in node.items()}

        if isinstance(node, list):
            return [_resolve(i) for i in node]

        return node

    return _resolve(schema_copy)  # type: ignore[no-any-return]


def add_key_in_dict_recursively(
    d: dict[str, Any], key: str, value: Any, criteria: Callable[[dict[str, Any]], bool]
) -> dict[str, Any]:
    """Recursively adds a key/value pair to all nested dicts matching `criteria`."""
    if isinstance(d, dict):
        if criteria(d) and key not in d:
            d[key] = value
        for v in d.values():
            add_key_in_dict_recursively(v, key, value, criteria)
    elif isinstance(d, list):
        for i in d:
            add_key_in_dict_recursively(i, key, value, criteria)
    return d


def fix_discriminator_mappings(schema: dict[str, Any]) -> dict[str, Any]:
    """Replace '#/$defs/...' references in discriminator.mapping with just the model name."""
    output = schema.get("properties", {}).get("output")
    if not output:
        return schema

    disc = output.get("discriminator")
    if not disc or "mapping" not in disc:
        return schema

    disc["mapping"] = {k: v.split("/")[-1] for k, v in disc["mapping"].items()}
    return schema


def add_const_to_oneof_variants(schema: dict[str, Any]) -> dict[str, Any]:
    """Add const fields to oneOf variants for discriminated unions.

    The json_schema_to_pydantic library requires each oneOf variant to have
    a const field for the discriminator property. This function adds those
    const fields based on the discriminator mapping.

    Args:
        schema: JSON Schema dict that may contain discriminated unions

    Returns:
        Modified schema with const fields added to oneOf variants
    """

    def _process_oneof(node: dict[str, Any]) -> dict[str, Any]:
        """Process a single node that might contain a oneOf with discriminator."""
        if not isinstance(node, dict):
            return node

        if "oneOf" in node and "discriminator" in node:
            discriminator = node["discriminator"]
            property_name = discriminator.get("propertyName")
            mapping = discriminator.get("mapping", {})

            if property_name and mapping:
                one_of_variants = node.get("oneOf", [])

                for variant in one_of_variants:
                    if isinstance(variant, dict) and "properties" in variant:
                        variant_title = variant.get("title", "")

                        matched_disc_value = None
                        for disc_value, schema_name in mapping.items():
                            if variant_title == schema_name or variant_title.endswith(
                                schema_name
                            ):
                                matched_disc_value = disc_value
                                break

                        if matched_disc_value is not None:
                            props = variant["properties"]
                            if property_name in props:
                                props[property_name]["const"] = matched_disc_value

        for key, value in node.items():
            if isinstance(value, dict):
                node[key] = _process_oneof(value)
            elif isinstance(value, list):
                node[key] = [
                    _process_oneof(item) if isinstance(item, dict) else item
                    for item in value
                ]

        return node

    return _process_oneof(deepcopy(schema))


def convert_oneof_to_anyof(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert oneOf to anyOf for OpenAI compatibility.

    OpenAI's Structured Outputs support anyOf better than oneOf.
    This recursively converts all oneOf occurrences to anyOf.

    Args:
        schema: JSON schema dictionary.

    Returns:
        Modified schema with anyOf instead of oneOf.
    """
    if isinstance(schema, dict):
        if "oneOf" in schema:
            schema["anyOf"] = schema.pop("oneOf")

        for value in schema.values():
            if isinstance(value, dict):
                convert_oneof_to_anyof(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_oneof_to_anyof(item)

    return schema


def ensure_all_properties_required(schema: dict[str, Any]) -> dict[str, Any]:
    """Ensure all properties are in the required array for OpenAI strict mode.

    OpenAI's strict structured outputs require all properties to be listed
    in the required array. This recursively updates all objects to include
    all their properties in required.

    Args:
        schema: JSON schema dictionary.

    Returns:
        Modified schema with all properties marked as required.
    """
    if isinstance(schema, dict):
        if schema.get("type") == "object" and "properties" in schema:
            properties = schema["properties"]
            if properties:
                schema["required"] = list(properties.keys())

        for value in schema.values():
            if isinstance(value, dict):
                ensure_all_properties_required(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        ensure_all_properties_required(item)

    return schema



def generate_model_description(model: type[BaseModel]) -> dict[str, Any]:
    """Generate JSON schema description of a Pydantic model. Dereferences $refs."""
    json_schema = model.model_json_schema(ref_template="#/$defs/{model}")

    json_schema = add_key_in_dict_recursively(
        json_schema,
        key="additionalProperties",
        value=False,
        criteria=lambda d: d.get("type") == "object"
        and "additionalProperties" not in d,
    )

    json_schema = resolve_refs(json_schema)

    json_schema.pop("$defs", None)
    json_schema = fix_discriminator_mappings(json_schema)
    json_schema = convert_oneof_to_anyof(json_schema)
    json_schema = ensure_all_properties_required(json_schema)

    return {
        "type": "json_schema",
        "json_schema": {
            "name": model.__name__,
            "strict": True,
            "schema": json_schema,
        },
    }


def handle_partial_json(
    result: str,
    model: type[BaseModel],
    is_json_output: bool,
) -> dict[str, Any] | BaseModel | str:
    """Handle partial JSON in a result string and convert to Pydantic model or dict."""
    match = _JSON_PATTERN.search(result)
    if match:
        try:
            exported_result = model.model_validate_json(match.group())
            if is_json_output:
                return exported_result.model_dump()
            return exported_result
        except json.JSONDecodeError:
            pass
        except ValidationError:
            raise
        except Exception as e:
            raise Exception(
                f"Unexpected error during partial JSON handling: {type(e).__name__}: {e}. Attempting alternative conversion method.",
            )
    return result

class Converter:
    """Handles retries and robust parsing for Pydantic conversion."""
    def __init__(self, litellm: Any, text: str, model: type[BaseModel], instructions: str, llm: str = 'deepseek/deepseek-chat'):
        self.litellm = litellm
        self.model = model 
        self.text = text 
        self.instructions = instructions
        self.llm = llm
        self.max_attempts = 3

    def to_pydantic(self, current_attempt: int = 1) -> BaseModel:
        while current_attempt <= self.max_attempts:
            try:
                response = self.litellm.completion(
                    model=self.llm,
                    messages=[
                        {"role": "system", "content": self.instructions},
                        {"role": "user", "content": self.text},
                    ]
                )
                content = response['choices'][0]['message']['content']

                try:
                    return self.model.model_validate_json(content)
                except ValidationError:
                    pass  

                result = handle_partial_json(result=content, model=self.model, is_json_output=False)

                if isinstance(result, BaseModel):
                    return result
                elif isinstance(result, dict):
                    return self.model.model_validate(result)
                elif isinstance(result, str):
                    return self.model.model_validate_json(result)
                else:
                    raise TypeError("handle_partial_json returned an unsupported type.")

            except (ValidationError, Exception) as e:
                current_attempt += 1
                if current_attempt > self.max_attempts:
                    raise Exception(f"Failed after {self.max_attempts} attempts: {e}") from e

        raise RuntimeError("Unexpected control flow in Converter.to_pydantic")

class StructuredOutputHandler:
    """
    Handles LLM inference with a Pydantic response format, including 
    schema enforcement, retry logic, and robust JSON parsing.
    """

    def __init__(self, litellm: Any):
        """
        Initializes the handler with a litellm client instance.
        
        Args:
            litellm: The litellm client (or equivalent object providing 
                     `acompletion` and `completion`).
        """
        self.litellm = litellm

    async def handle_structured_inference(self, **kwargs: Any) -> dict[str, Any]:
        """
        Performs the structured LLM inference, ensuring the output 
        conforms to the given Pydantic model.
        
        Args:
            **kwargs: Arguments intended for litellm.acompletion, 
                      must include 'response_format' (a Pydantic BaseModel class).

        Returns:
            The litellm response dictionary, with the content parsed into 
            a Python dictionary (from the Pydantic model).
        """
        response_format = kwargs.get('response_format', None)
        
        if not response_format or not issubclass(response_format, BaseModel):
            raise Exception(f'response_format:{response_format} is not a valid Pydantic BaseModel class')
            
        messages = kwargs.get('messages', [])
        if not messages:
            raise Exception('messages are required')

        formatted_messages = self.format_messages(messages, response_format)
        
        filtered_params = {k:v for k, v in kwargs.items() if k!='response_format'}
        filtered_params['messages'] = formatted_messages
        
        answer = await self.litellm.acompletion(**filtered_params)
        formatted_answer = answer['choices'][0]['message']['content']

        formatted_result = None
        try:
            formatted_result = response_format.model_validate_json(formatted_answer)

        except ValidationError:
            model_description = generate_model_description(response_format)
            schema_json = json.dumps(model_description, indent=2)
            instructions = FORMATTED_TASK_INSTRUCTIONS.format(output_format=schema_json)
            
            try:
                converter = Converter(
                    litellm = self.litellm, 
                    text = formatted_answer, 
                    model = response_format,
                    instructions = instructions,
                    llm = filtered_params.get('model') 
                )
                result = converter.to_pydantic()
                
                if isinstance(result, BaseModel):
                    formatted_result = result
            except Exception as e:
                raise Exception(f"Failed to parse output into response format after retries: {e}")

        if not isinstance(formatted_result, BaseModel):
             raise TypeError("Structured parsing failed to yield a Pydantic BaseModel.")

        answer['choices'][0]['message']['content'] = formatted_result.model_dump()

        return answer

    def format_messages(self, messages: list[dict[str, str]], response_format: Type[BaseModel]) -> list[dict[str, str]]:
        """Inject the structured output instructions into the system prompt."""
        model_description = generate_model_description(response_format)
        schema_json = json.dumps(model_description, indent=2)
        system_prompt = LITE_AGENT_RESPONSE_FORMAT.format(response_format=schema_json)
        
        formatted_messages = deepcopy(messages)

        if formatted_messages and formatted_messages[0]['role'] == 'system':
            formatted_messages[0]['content'] = formatted_messages[0]['content'] + "\n\n" + system_prompt
        else:
            new_system_message = {"role": "system", "content": system_prompt}
            formatted_messages.insert(0, new_system_message)

        return formatted_messages
