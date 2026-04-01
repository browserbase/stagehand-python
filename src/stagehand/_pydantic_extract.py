"""Utilities for Pydantic schema conversion in extract calls."""

from __future__ import annotations

import inspect
import logging
from typing import Any, Dict, Type

from pydantic import BaseModel

logger = logging.getLogger(__name__)


def is_pydantic_model(schema: Any) -> bool:
    """Check if the given schema is a Pydantic BaseModel subclass."""
    return inspect.isclass(schema) and issubclass(schema, BaseModel)


def pydantic_model_to_json_schema(schema: Type[BaseModel]) -> Dict[str, object]:
    """Convert a Pydantic BaseModel class to a JSON Schema dict.

    Calls ``model_rebuild()`` first so that forward references created by
    ``from __future__ import annotations`` are resolved before schema
    generation.
    """
    schema.model_rebuild()
    return schema.model_json_schema()


def validate_extract_response(result: object, schema: Type[BaseModel]) -> Any:
    """Validate raw extract result data against a Pydantic model.

    Tries direct validation first. On failure, falls back to normalizing
    dict keys from camelCase to snake_case before retrying.

    Returns the validated Pydantic model instance, or the raw result if
    both attempts fail.
    """
    try:
        return schema.model_validate(result)
    except Exception:
        try:
            normalized = _convert_dict_keys_to_snake_case(result)
            return schema.model_validate(normalized)
        except Exception:
            logger.warning(
                "Failed to validate extracted data against schema %s. "
                "Returning raw data.",
                schema.__name__,
            )
            return result


def _camel_to_snake(name: str) -> str:
    """Convert a camelCase or PascalCase string to snake_case."""
    chars: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i != 0 and not name[i - 1].isupper():
            chars.append("_")
        chars.append(ch.lower())
    return "".join(chars)


def _convert_dict_keys_to_snake_case(data: Any) -> Any:
    """Recursively convert dict keys from camelCase to snake_case."""
    if isinstance(data, dict):
        return {
            _camel_to_snake(k) if isinstance(k, str) else k: _convert_dict_keys_to_snake_case(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_convert_dict_keys_to_snake_case(item) for item in data]
    return data
