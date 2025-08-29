import inspect
import os
from typing import Any, Union, get_args, get_origin

from pydantic import AnyUrl, BaseModel, Field, HttpUrl, create_model
from pydantic.fields import FieldInfo

from stagehand.types.a11y import AccessibilityNode


def snake_to_camel(snake_str: str) -> str:
    """
    Convert a snake_case string to camelCase.

    Args:
        snake_str: The snake_case string to convert

    Returns:
        The converted camelCase string
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])





def camel_to_snake(camel_str: str) -> str:
    """
    Convert a camelCase or PascalCase string to snake_case.

    Args:
        camel_str: The camelCase/PascalCase string to convert

    Returns:
        The converted snake_case string
    """
    result_chars = []
    for index, char in enumerate(camel_str):
        if char.isupper() and index != 0 and (not camel_str[index - 1].isupper()):
            result_chars.append("_")
        result_chars.append(char.lower())
    return "".join(result_chars)


def convert_dict_keys_to_snake_case(data: Any) -> Any:
    """
    Convert all dictionary keys from camelCase/PascalCase to snake_case.
    Works recursively for nested dictionaries and lists. Non-dict/list inputs are returned as-is.

    Args:
        data: Potentially nested structure with dictionaries/lists

    Returns:
        A new structure with all dict keys converted to snake_case
    """
    if isinstance(data, dict):
        converted: dict[str, Any] = {}
        for key, value in data.items():
            converted_key = camel_to_snake(key) if isinstance(key, str) else key
            converted[converted_key] = convert_dict_keys_to_snake_case(value)
        return converted
    if isinstance(data, list):
        return [convert_dict_keys_to_snake_case(item) for item in data]
    return data


def format_simplified_tree(node: AccessibilityNode, level: int = 0) -> str:
    """Formats a node and its children into a simplified string representation."""
    indent = "  " * level
    name_part = f": {node.get('name')}" if node.get("name") else ""
    result = f"{indent}[{node.get('nodeId')}] {node.get('role')}{name_part}\n"

    children = node.get("children", [])
    if children:
        result += "".join(
            format_simplified_tree(child, level + 1) for child in children
        )
    return result


async def draw_observe_overlay(page, elements):
    """
    Draw an overlay on the page highlighting the observed elements.

    Args:
        page: Playwright page object
        elements: list of observation results with selectors
    """
    if not elements:
        return

    # Create a function to inject and execute in the page context
    script = """
    (elements) => {
        // First remove any existing overlays
        document.querySelectorAll('.stagehand-observe-overlay').forEach(el => el.remove());
        
        // Create container for overlays
        const container = document.createElement('div');
        container.style.position = 'fixed';
        container.style.top = '0';
        container.style.left = '0';
        container.style.width = '100%';
        container.style.height = '100%';
        container.style.pointerEvents = 'none';
        container.style.zIndex = '10000';
        container.className = 'stagehand-observe-overlay';
        document.body.appendChild(container);
        
        // Process each element
        elements.forEach((element, index) => {
            try {
                // Parse the selector
                let selector = element.selector;
                if (selector.startsWith('xpath=')) {
                    selector = selector.substring(6);
                    
                    // Evaluate the XPath to get the element
                    const result = document.evaluate(
                        selector, document, null, 
                        XPathResult.FIRST_ORDERED_NODE_TYPE, null
                    );
                    
                    if (result.singleNodeValue) {
                        // Get the element's position
                        const el = result.singleNodeValue;
                        const rect = el.getBoundingClientRect();
                        
                        // Create the overlay
                        const overlay = document.createElement('div');
                        overlay.style.position = 'absolute';
                        overlay.style.left = rect.left + 'px';
                        overlay.style.top = rect.top + 'px';
                        overlay.style.width = rect.width + 'px';
                        overlay.style.height = rect.height + 'px';
                        overlay.style.border = '2px solid red';
                        overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                        overlay.style.boxSizing = 'border-box';
                        overlay.style.pointerEvents = 'none';
                        
                        // Add element ID
                        const label = document.createElement('div');
                        label.textContent = index + 1;
                        label.style.position = 'absolute';
                        label.style.left = '0';
                        label.style.top = '-20px';
                        label.style.backgroundColor = 'red';
                        label.style.color = 'white';
                        label.style.padding = '2px 5px';
                        label.style.borderRadius = '3px';
                        label.style.fontSize = '12px';
                        
                        overlay.appendChild(label);
                        container.appendChild(overlay);
                    }
                } else {
                    // Regular CSS selector
                    const el = document.querySelector(selector);
                    if (el) {
                        const rect = el.getBoundingClientRect();
                        
                        // Create the overlay (same as above)
                        const overlay = document.createElement('div');
                        overlay.style.position = 'absolute';
                        overlay.style.left = rect.left + 'px';
                        overlay.style.top = rect.top + 'px';
                        overlay.style.width = rect.width + 'px';
                        overlay.style.height = rect.height + 'px';
                        overlay.style.border = '2px solid red';
                        overlay.style.backgroundColor = 'rgba(255, 0, 0, 0.1)';
                        overlay.style.boxSizing = 'border-box';
                        overlay.style.pointerEvents = 'none';
                        
                        // Add element ID
                        const label = document.createElement('div');
                        label.textContent = index + 1;
                        label.style.position = 'absolute';
                        label.style.left = '0';
                        label.style.top = '-20px';
                        label.style.backgroundColor = 'red';
                        label.style.color = 'white';
                        label.style.padding = '2px 5px';
                        label.style.borderRadius = '3px';
                        label.style.fontSize = '12px';
                        
                        overlay.appendChild(label);
                        container.appendChild(overlay);
                    }
                }
            } catch (error) {
                console.error(`Error drawing overlay for element ${index}:`, error);
            }
        });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            document.querySelectorAll('.stagehand-observe-overlay').forEach(el => el.remove());
        }, 5000);
    }
    """

    # Execute the script in the page context
    await page.evaluate(script, elements)


# Add utility functions for extraction URL handling


def transform_url_strings_to_ids(schema):
    """
    Transforms a Pydantic schema by replacing URL fields with numeric fields.
    This is used to handle URL extraction from accessibility trees where URLs are represented by IDs.

    Args:
        schema: A Pydantic model class

    Returns:
        Tuple of (transformed_schema, url_paths) where url_paths is a list of paths to URL fields
    """
    if not schema or not inspect.isclass(schema) or not issubclass(schema, BaseModel):
        return schema, []

    return transform_model(schema)


# TODO: remove path?
def transform_model(model_cls, path=[]):  # noqa: F841 B006
    """
    Recursively transforms a Pydantic model by replacing URL fields with numeric fields.

    Args:
        model_cls: A Pydantic model class
        path: Current path in the schema (used for recursion)

    Returns:
        Tuple of (transformed_model_cls, url_paths)
    """
    # Get model fields based on Pydantic version
    try:
        # Pydantic V2 approach
        field_definitions = {}
        url_paths = []
        changed = False

        for field_name, field_info in model_cls.model_fields.items():
            field_type = field_info.annotation

            # Transform the field type and collect URL paths
            new_type, child_paths = transform_type(field_type, [field_name])

            if new_type != field_type:
                changed = True

            # Prepare field definition with the possibly transformed type
            field_definitions[field_name] = (new_type, field_info)

            # Add child paths to our collected paths
            if child_paths:
                for cp in child_paths:
                    if isinstance(cp, dict) and "segments" in cp:
                        segments = cp["segments"]
                        url_paths.append({"segments": [field_name] + segments})
                    else:
                        url_paths.append({"segments": [field_name]})

        if not changed:
            return model_cls, url_paths

        # Create a new model with transformed fields
        new_model = create_model(
            f"{model_cls.__name__}IdTransformed",
            __base__=None,  # Don't inherit since we're redefining all fields
            **field_definitions,
        )

        return new_model, url_paths

    except AttributeError:
        # Fallback to Pydantic V1 approach
        field_definitions = {}
        url_paths = []
        changed = False

        for field_name, field_info in model_cls.__fields__.items():
            field_type = field_info.annotation

            # Transform the field type and collect URL paths
            new_type, child_paths = transform_type(field_type, [field_name])

            if new_type != field_type:
                changed = True

            # Prepare field definition with the possibly transformed type
            field_kwargs = {}
            if field_info.default is not None and field_info.default is not ...:
                field_kwargs["default"] = field_info.default
            elif field_info.default_factory is not None:
                field_kwargs["default_factory"] = field_info.default_factory

            # Handle Field metadata
            if hasattr(field_info, "field_info") and isinstance(
                field_info.field_info, FieldInfo
            ):
                field_definitions[field_name] = (
                    new_type,
                    Field(**field_info.field_info.model_dump()),
                )
            else:
                field_definitions[field_name] = (new_type, Field(**field_kwargs))

            # Add child paths to our collected paths
            if child_paths:
                for cp in child_paths:
                    if isinstance(cp, dict) and "segments" in cp:
                        segments = cp["segments"]
                        url_paths.append({"segments": [field_name] + segments})
                    else:
                        url_paths.append({"segments": [field_name]})

        if not changed:
            return model_cls, url_paths

        # Create a new model with transformed fields
        new_model = create_model(
            f"{model_cls.__name__}IdTransformed",
            __base__=None,  # Don't inherit since we're redefining all fields
            **field_definitions,
        )

        return new_model, url_paths


def transform_type(annotation, path):
    """
    Recursively transforms a type annotation, replacing URL types with int.

    Args:
        annotation: Type annotation to transform
        path: Current path in the schema (used for recursion)

    Returns:
        Tuple of (transformed_annotation, url_paths)
    """
    # Handle None or Any
    if annotation is None:
        return annotation, []

    # Get the origin type for generic types (list, Optional, etc.)
    origin = get_origin(annotation)

    # Case 1: It's a URL type (AnyUrl, HttpUrl)
    if is_url_type(annotation):
        return int, [{"segments": []}]

    # Case 2: It's a list or other generic container
    if origin in (list, list):
        args = get_args(annotation)
        if not args:
            return annotation, []

        # Transform the element type
        elem_type = args[0]
        new_elem_type, child_paths = transform_type(elem_type, path + ["*"])

        if new_elem_type != elem_type:
            # Transform the list type to use the new element type
            if len(args) > 1:  # Handle list with multiple type args
                new_args = (new_elem_type,) + args[1:]
                new_type = origin[new_args]
            else:
                new_type = list[new_elem_type]

            # Update paths to include the array wildcard
            url_paths = []
            for cp in child_paths:
                if isinstance(cp, dict) and "segments" in cp:
                    segments = cp["segments"]
                    url_paths.append({"segments": ["*"] + segments})
                else:
                    url_paths.append({"segments": ["*"]})

            return new_type, url_paths

        return annotation, []

    # Case 3: It's a Union or Optional
    elif origin is Union:
        args = get_args(annotation)
        new_args = []
        url_paths = []
        changed = False

        for i, arg in enumerate(args):
            new_arg, child_paths = transform_type(arg, path + [f"union_{i}"])
            new_args.append(new_arg)

            if new_arg != arg:
                changed = True

            if child_paths:
                for cp in child_paths:
                    if isinstance(cp, dict) and "segments" in cp:
                        segments = cp["segments"]
                        url_paths.append({"segments": [f"union_{i}"] + segments})
                    else:
                        url_paths.append({"segments": [f"union_{i}"]})

        if changed:
            return Union[tuple(new_args)], url_paths

        return annotation, []

    # Case 4: It's a Pydantic model
    elif inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        new_model, child_paths = transform_model(annotation, path)

        if new_model != annotation:
            return new_model, child_paths

        return annotation, []

    # Case 5: Any other type (no transformation needed)
    return annotation, []


def is_url_type(annotation):
    """
    Checks if a type annotation is a URL type (directly or nested in a container).

    Args:
        annotation: Type annotation to check

    Returns:
        bool: True if it's a URL type, False otherwise
    """
    if annotation is None:
        return False

    # Direct URL type - handle subscripted generics safely
    # Pydantic V2 can generate complex type annotations that can't be used with issubclass()
    try:
        if inspect.isclass(annotation) and issubclass(annotation, (AnyUrl, HttpUrl)):
            return True
    except TypeError:
        # Handle subscripted generics that can't be used with issubclass
        # This commonly occurs with Pydantic V2's typing.Annotated[...] constructs
        # We gracefully skip these rather than crashing, as they're not simple URL types
        pass

    # Check for URL in generic containers
    origin = get_origin(annotation)

    # Handle list[URL]
    if origin in (list, list):
        args = get_args(annotation)
        if args:
            return is_url_type(args[0])

    # Handle Optional[URL] / Union[URL, None]
    elif origin is Union:
        args = get_args(annotation)
        return any(is_url_type(arg) for arg in args)

    return False


def inject_urls(result, url_paths, id_to_url_mapping):
    """
    Injects URLs back into the result data structure based on paths and ID-to-URL mapping.

    Args:
        result: The result data structure
        url_paths: list of paths to URL fields in the structure
        id_to_url_mapping: Dictionary mapping numeric IDs to URLs

    Returns:
        None (modifies result in-place)
    """
    if not result or not url_paths or not id_to_url_mapping:
        return

    for path in url_paths:
        segments = path.get("segments", [])
        if not segments:
            continue

        # Navigate the path recursively
        inject_url_at_path(result, segments, id_to_url_mapping)


def inject_url_at_path(obj, segments, id_to_url_mapping):
    """
    Helper function to recursively inject URLs at the specified path.
    Handles wildcards for lists and properly navigates the object structure.

    Args:
        obj: The object to inject URLs into
        segments: The path segments to navigate
        id_to_url_mapping: Dictionary mapping numeric IDs to URLs

    Returns:
        None (modifies obj in-place)
    """
    if not segments or obj is None:
        return

    key = segments[0]
    rest = segments[1:]

    # Handle wildcard for lists
    if key == "*":
        if isinstance(obj, list):
            for item in obj:
                inject_url_at_path(item, rest, id_to_url_mapping)
        return

    # Handle dictionary/object
    if isinstance(obj, dict) and key in obj:
        if not rest:
            # We've reached the target field, perform the ID-to-URL conversion
            id_value = obj[key]
            if id_value is not None and (isinstance(id_value, (int, str))):
                id_str = str(id_value)
                if id_str in id_to_url_mapping:
                    obj[key] = id_to_url_mapping[id_str]
        else:
            # Continue traversing the path
            inject_url_at_path(obj[key], rest, id_to_url_mapping)


# Convert any non-serializable objects to plain Python objects
def make_serializable(obj):
    """Recursively convert non-JSON-serializable objects to serializable ones."""
    if hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
        # Handle iterables (including ValidatorIterator)
        if hasattr(obj, "__next__"):  # It's an iterator
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, (list, tuple)):
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: make_serializable(value) for key, value in obj.items()}
    return obj


def get_download_path(stagehand):
    """Get the download path for local browser mode."""
    if stagehand.local_browser_launch_options.get("downloadPath"):
        return stagehand.local_browser_launch_options["downloadPath"]
    else:
        path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(path, exist_ok=True)
        return path


# Configuration validation utilities

def validate_model_name(model_name: str) -> dict[str, Any]:
    """
    Validate a model name and provide suggestions if invalid.
    
    Args:
        model_name: The model name to validate
        
    Returns:
        Dictionary with validation results and suggestions
    """
    result = {
        "valid": True,
        "warnings": [],
        "suggestions": []
    }
    
    if not model_name or not isinstance(model_name, str):
        result["valid"] = False
        result["suggestions"].append("Model name must be a non-empty string")
        return result
    
    # Common model name patterns and suggestions
    common_models = {
        "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "together": ["meta-llama/Llama-2-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
        "groq": ["llama2-70b-4096", "mixtral-8x7b-32768"],
        "google": ["gemini-pro", "gemini-pro-vision"]
    }
    
    model_lower = model_name.lower()
    
    # Check for deprecated or potentially incorrect model names
    if "davinci" in model_lower or "curie" in model_lower or "babbage" in model_lower:
        result["warnings"].append("This appears to be a legacy OpenAI model name. Consider using gpt-3.5-turbo or gpt-4o instead.")
    
    if model_lower.startswith("text-") and "openai" in model_lower:
        result["warnings"].append("Text completion models are deprecated. Consider using chat models like gpt-3.5-turbo.")
    
    # Provide suggestions based on partial matches
    if "gpt" in model_lower and not any(valid in model_lower for valid in ["gpt-3.5", "gpt-4"]):
        result["suggestions"].extend(common_models["openai"])
    elif "claude" in model_lower and not model_lower.startswith("claude-3"):
        result["suggestions"].extend(common_models["anthropic"])
    
    return result


def check_environment_setup() -> dict[str, Any]:
    """
    Check the environment setup for common configuration issues.
    
    Returns:
        Dictionary with environment check results
    """
    result = {
        "issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check for common environment variables
    api_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic", 
        "TOGETHER_API_KEY": "Together AI",
        "GROQ_API_KEY": "Groq",
        "GOOGLE_API_KEY": "Google"
    }
    
    found_keys = []
    for env_var, provider in api_keys.items():
        if os.getenv(env_var):
            found_keys.append(provider)
    
    if not found_keys:
        result["warnings"].append("No API keys found in environment variables. You'll need to provide them in configuration.")
    else:
        result["recommendations"].append(f"Found API keys for: {', '.join(found_keys)}")
    
    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        result["issues"].append(f"Python {sys.version_info.major}.{sys.version_info.minor} detected. Python 3.8+ is recommended.")
    
    # Check for required packages
    try:
        import playwright
        result["recommendations"].append("Playwright is available for browser automation")
    except ImportError:
        result["issues"].append("Playwright not found. Install with: pip install playwright")
    
    try:
        import litellm
        result["recommendations"].append("LiteLLM is available for LLM integration")
    except ImportError:
        result["issues"].append("LiteLLM not found. Install with: pip install litellm")
    
    return result


def suggest_configuration_fixes(validation_errors: list[str]) -> list[str]:
    """
    Suggest fixes for common configuration errors.
    
    Args:
        validation_errors: List of validation error messages
        
    Returns:
        List of suggested fixes
    """
    suggestions = []
    
    for error in validation_errors:
        error_lower = error.lower()
        
        if "api key" in error_lower and "openai" in error_lower:
            suggestions.append(
                "Set your OpenAI API key:\n"
                "  - Environment: export OPENAI_API_KEY=your-key\n"
                "  - Config: model_client_options={'api_key': 'your-key'}"
            )
        elif "api key" in error_lower and "anthropic" in error_lower:
            suggestions.append(
                "Set your Anthropic API key:\n"
                "  - Environment: export ANTHROPIC_API_KEY=your-key\n"
                "  - Config: model_client_options={'api_key': 'your-key'}"
            )
        elif "api_base" in error_lower:
            suggestions.append(
                "Fix your API base URL:\n"
                "  - Must start with http:// or https://\n"
                "  - Example: 'https://api.openai.com/v1'\n"
                "  - For local servers: 'http://localhost:8000/v1'"
            )
        elif "model_name" in error_lower:
            suggestions.append(
                "Specify a valid model name:\n"
                "  - OpenAI: 'gpt-4o', 'gpt-3.5-turbo'\n"
                "  - Anthropic: 'claude-3-opus-20240229'\n"
                "  - Together: 'meta-llama/Llama-2-70b-chat-hf'"
            )
        elif "timeout" in error_lower:
            suggestions.append(
                "Fix timeout configuration:\n"
                "  - Must be a positive number (seconds)\n"
                "  - Example: model_client_options={'timeout': 30}"
            )
    
    return suggestions
