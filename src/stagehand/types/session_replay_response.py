# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionReplayResponse", "Data", "DataPage", "DataPageAction", "DataPageActionTokenUsage"]


class DataPageActionTokenUsage(BaseModel):
    cost: Optional[float] = None

    input_tokens: Optional[float] = FieldInfo(alias="inputTokens", default=None)

    output_tokens: Optional[float] = FieldInfo(alias="outputTokens", default=None)

    time_ms: Optional[float] = FieldInfo(alias="timeMs", default=None)


class DataPageAction(BaseModel):
    method: str

    parameters: Dict[str, object]

    result: Dict[str, object]

    timestamp: float

    end_time: Optional[float] = FieldInfo(alias="endTime", default=None)

    token_usage: Optional[DataPageActionTokenUsage] = FieldInfo(alias="tokenUsage", default=None)


class DataPage(BaseModel):
    actions: List[DataPageAction]

    duration: float

    timestamp: float

    url: str


class Data(BaseModel):
    pages: List[DataPage]

    client_language: Optional[str] = FieldInfo(alias="clientLanguage", default=None)


class SessionReplayResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
