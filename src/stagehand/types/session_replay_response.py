# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SessionReplayResponse", "Data", "DataPage", "DataPageAction", "DataPageActionTokenUsage"]


class DataPageActionTokenUsage(BaseModel):
    cached_input_tokens: Optional[float] = FieldInfo(alias="cachedInputTokens", default=None)

    input_tokens: Optional[float] = FieldInfo(alias="inputTokens", default=None)

    output_tokens: Optional[float] = FieldInfo(alias="outputTokens", default=None)

    reasoning_tokens: Optional[float] = FieldInfo(alias="reasoningTokens", default=None)

    time_ms: Optional[float] = FieldInfo(alias="timeMs", default=None)


class DataPageAction(BaseModel):
    method: Optional[str] = None

    token_usage: Optional[DataPageActionTokenUsage] = FieldInfo(alias="tokenUsage", default=None)


class DataPage(BaseModel):
    actions: Optional[List[DataPageAction]] = None


class Data(BaseModel):
    pages: Optional[List[DataPage]] = None


class SessionReplayResponse(BaseModel):
    data: Data

    success: bool
    """Indicates whether the request was successful"""
