# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .action import Action

__all__ = ["SessionObserveResponse"]

SessionObserveResponse: TypeAlias = List[Action]
