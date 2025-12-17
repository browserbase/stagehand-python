# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionExecuteResponse", "Data", "DataResult", "DataResultAction", "DataResultUsage"]


class DataResultAction(BaseModel):
    type: str
    """Type of action taken"""

    action: Optional[str] = None

    instruction: Optional[str] = None

    page_text: Optional[str] = FieldInfo(alias="pageText", default=None)

    page_url: Optional[str] = FieldInfo(alias="pageUrl", default=None)

    reasoning: Optional[str] = None
    """Agent's reasoning for taking this action"""

    task_completed: Optional[bool] = FieldInfo(alias="taskCompleted", default=None)

    time_ms: Optional[float] = FieldInfo(alias="timeMs", default=None)
    """Time taken for this action in ms"""

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
    else:
        __pydantic_extra__: Dict[str, object]


class DataResultUsage(BaseModel):
    inference_time_ms: float

    input_tokens: float

    output_tokens: float

    cached_input_tokens: Optional[float] = None

    reasoning_tokens: Optional[float] = None


class DataResult(BaseModel):
    actions: List[DataResultAction]

    completed: bool
    """Whether the agent finished its task"""

    message: str
    """Summary of what the agent accomplished"""

    success: bool
    """Whether the agent completed successfully"""

    metadata: Optional[Dict[str, object]] = None

    usage: Optional[DataResultUsage] = None


class Data(BaseModel):
    result: DataResult


class SessionExecuteResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
