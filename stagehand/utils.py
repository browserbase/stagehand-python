import inspect
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


def convert_dict_keys_to_camel_case(data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert all keys in a dictionary from snake_case to camelCase.
    Works recursively for nested dictionaries.

    Args:
        data: Dictionary with snake_case keys

    Returns:
        Dictionary with camelCase keys
    """
    result = {}

    for key, value in data.items():
        if isinstance(value, dict):
            value = convert_dict_keys_to_camel_case(value)
        elif isinstance(value, list):
            value = [
                (
                    convert_dict_keys_to_camel_case(item)
                    if isinstance(item, dict)
                    else item
                )
                for item in value
            ]

        # Convert snake_case key to camelCase
        camel_key = snake_to_camel(key)
        result[camel_key] = value

    return result


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

    # Direct URL type
    if inspect.isclass(annotation) and issubclass(annotation, (AnyUrl, HttpUrl)):
        return True

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
