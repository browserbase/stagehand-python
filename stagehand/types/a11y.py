from typing import Any, Optional, TypedDict, Union


class AXProperty(TypedDict):
    name: str
    value: Any  # Can be more specific if needed


class AXValue(TypedDict):
    type: str
    value: Optional[Union[str, int, float, bool]]


class AXNode(TypedDict):
    nodeId: str
    role: Optional[AXValue]
    name: Optional[AXValue]
    description: Optional[AXValue]
    value: Optional[AXValue]
    backendDOMNodeId: Optional[int]
    parentId: Optional[str]
    childIds: Optional[list[str]]
    properties: Optional[list[AXProperty]]


class AccessibilityNode(TypedDict, total=False):
    nodeId: str
    role: str
    name: Optional[str]
    description: Optional[str]
    value: Optional[str]
    backendDOMNodeId: Optional[int]
    parentId: Optional[str]
    childIds: Optional[list[str]]
    children: Optional[list["AccessibilityNode"]]
    properties: Optional[list[AXProperty]]  # Assuming structure from AXNode


class TreeResult(TypedDict):
    tree: list[AccessibilityNode]
    simplified: str
    iframes: list[AccessibilityNode]  # Simplified iframe info
    idToUrl: dict[str, str]


# Placeholder for Playwright Page/CDPSession/Locator if not using StagehandPage directly
# from playwright.async_api import Page, CDPSession, Locator
# Assuming types are imported if StagehandPage is not used directly
CDPSession = Any  # Replace with actual Playwright CDPSession type if needed
Locator = Any  # Replace with actual Playwright Locator type if needed


# --- Placeholder Exceptions ---
class PlaywrightCommandError(Exception):
    pass


class PlaywrightMethodNotSupportedError(Exception):
    pass
