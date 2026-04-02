"""Utilities for Pydantic schema conversion in extract calls."""

from __future__ import annotations

import inspect
import logging
from typing import Any, Dict, Type, cast
from typing_extensions import Literal

from pydantic import BaseModel, ConfigDict

from ._utils import lru_cache

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


def validate_extract_response(
    result: object, schema: Type[BaseModel], *, strict_response_validation: bool
) -> Any:
    """Validate raw extract result data against a Pydantic model.

    Tries direct validation first. On failure, falls back to normalizing
    dict keys from camelCase to snake_case before retrying.

    Returns the validated Pydantic model instance, or the raw result if
    both attempts fail.
    """
    validation_schema = _validation_schema(schema, strict_response_validation)
    try:
        return validation_schema.model_validate(result)
    except Exception:
        try:
            normalized = _convert_dict_keys_to_snake_case(result)
            return validation_schema.model_validate(normalized)
        except Exception:
            logger.warning(
                "Failed to validate extracted data against schema %s. "
                "Returning raw data.",
                schema.__name__,
            )
            return result


@lru_cache(maxsize=None)
def _validation_schema(schema: Type[BaseModel], strict_response_validation: bool) -> Type[BaseModel]:
    extra_behavior: Literal["allow", "forbid"] = "forbid" if strict_response_validation else "allow"
    validation_schema = cast(
        Type[BaseModel],
        type(
            f"{schema.__name__}ExtractValidation",
            (schema,),
            {
                "__module__": schema.__module__,
                "model_config": ConfigDict(extra=extra_behavior),
            },
        ),
    )
    validation_schema.model_rebuild(force=True)
    return validation_schema


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
            for k, v in data.items()  # type: ignore[union-attr]
        }
    if isinstance(data, list):
        return [_convert_dict_keys_to_snake_case(item) for item in data]  # type: ignore[union-attr]
    return data
