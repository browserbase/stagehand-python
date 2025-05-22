from typing import Literal, Optional, TypedDict, Union


class ChatMessageImageUrl(TypedDict):
    url: str


class ChatMessageSource(TypedDict):
    type: str
    media_type: str
    data: str


class ChatMessageImageContent(TypedDict):
    type: Literal["image_url"]
    image_url: Optional[ChatMessageImageUrl]  # Make optional based on TS def
    text: Optional[str]  # Added based on TS def
    source: Optional[ChatMessageSource]  # Added based on TS def


class ChatMessageTextContent(TypedDict):
    type: Literal["text"]
    text: str


# ChatMessageContent can be a string or a list of text/image content parts
ChatMessageContent = Union[
    str, list[Union[ChatMessageImageContent, ChatMessageTextContent]]
]


# Updated ChatMessage type definition
class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: ChatMessageContent
