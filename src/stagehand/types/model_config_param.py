# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["ModelConfigParam", "UnionMember1"]


class UnionMember1(TypedDict, total=False):
    model_name: Required[Annotated[str, PropertyInfo(alias="modelName")]]

    api_key: Annotated[str, PropertyInfo(alias="apiKey")]

    base_url: Annotated[str, PropertyInfo(alias="baseURL")]


ModelConfigParam: TypeAlias = Union[str, UnionMember1]
