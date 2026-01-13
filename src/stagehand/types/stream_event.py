# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = ["StreamEvent", "Data", "DataStreamEventSystemDataOutput", "DataStreamEventLogDataOutput"]


class DataStreamEventSystemDataOutput(BaseModel):
    status: Literal["starting", "connected", "running", "finished", "error"]
    """Current status of the streaming operation"""

    error: Optional[str] = None
    """Error message (present when status is 'error')"""

    result: Optional[object] = None
    """Operation result (present when status is 'finished')"""


class DataStreamEventLogDataOutput(BaseModel):
    message: str
    """Log message from the operation"""

    status: Literal["running"]


Data: TypeAlias = Union[DataStreamEventSystemDataOutput, DataStreamEventLogDataOutput]


class StreamEvent(BaseModel):
    """Server-Sent Event emitted during streaming responses.

    Events are sent as `data: <JSON>\n\n`. Key order: data (with status first), type, id.
    """

    id: str
    """Unique identifier for this event"""

    data: Data

    type: Literal["system", "log"]
    """Type of stream event - system events or log messages"""
