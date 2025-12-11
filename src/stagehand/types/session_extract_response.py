# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["SessionExtractResponse", "Extraction"]


class Extraction(BaseModel):
    """Default extraction result"""

    extraction: Optional[str] = None


SessionExtractResponse: TypeAlias = Union[Extraction, Dict[str, object]]
