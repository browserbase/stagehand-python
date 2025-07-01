import asyncio
import json
import re
import time
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from stagehand.page import StagehandPage

from ..logging import StagehandLogger
from ..types.a11y import (
    AccessibilityNode,
    AXNode,
    CDPSession,
    TreeResult,
)
from ..utils import format_simplified_tree


async def _clean_structural_nodes(
    node: AccessibilityNode,
    page: Optional["StagehandPage"],
    logger: Optional[StagehandLogger],
) -> Optional[AccessibilityNode]:
    """Helper function to remove or collapse unnecessary structural nodes."""
    # 1) Filter out nodes with negative IDs
    node_id_str = node.get("nodeId")
    if node_id_str and int(node_id_str) < 0:
        return None

    # 2) Base case: if no children exist, this is effectively a leaf.
    children = node.get("children", [])
    if not children:
        return None if node.get("role") in ("generic", "none") else node

    # 3) Recursively clean children
    cleaned_children_tasks = [
        _clean_structural_nodes(child, page, logger) for child in children
    ]
    resolved_children = await asyncio.gather(*cleaned_children_tasks)
    cleaned_children = [child for child in resolved_children if child is not None]

    # 4) Prune "generic" or "none" nodes first
    node_role = node.get("role")
    if node_role in ("generic", "none"):
        if len(cleaned_children) == 1:
            # Collapse single-child structural node
            return cleaned_children[0]
        elif len(cleaned_children) == 0:
            # Remove empty structural node
            return None
        # Keep node if multiple children, try resolving role below

    # 5) Resolve role to DOM tag name if still generic/none and multiple children
    backend_node_id = node.get("backendDOMNodeId")
    if (
        page
        and logger
        and backend_node_id is not None
        and node_role in ("generic", "none")
    ):
        try:
            resolved_node = await page.send_cdp(
                "DOM.resolveNode", {"backendNodeId": backend_node_id}
            )
            object_info = resolved_node.get("object")
            if object_info and object_info.get("objectId"):
                object_id = object_info["objectId"]
                try:
                    function_declaration = 'function() { return this.tagName ? this.tagName.toLowerCase() : ""; }'
                    tag_name_result = await page.send_cdp(
                        "Runtime.callFunctionOn",
                        {
                            "objectId": object_id,
                            "functionDeclaration": function_declaration,
                            "returnByValue": True,
                        },
                    )
                    result_value = tag_name_result.get("result", {}).get("value")
                    if result_value:
                        node["role"] = result_value
                        node_role = result_value
                except Exception as tag_name_error:
                    # Use logger.debug (level 2)
                    logger.debug(
                        message=f"Could not fetch tagName for node {backend_node_id}",
                        auxiliary={
                            "error": {"value": str(tag_name_error), "type": "string"}
                        },
                    )
        except Exception as resolve_error:
            # Use logger.debug (level 2)
            logger.debug(
                message=f"Could not resolve DOM node ID {backend_node_id}",
                auxiliary={"error": {"value": str(resolve_error), "type": "string"}},
            )

    # Remove redundant StaticText children
    cleaned_children = _remove_redundant_static_text_children(node, cleaned_children)

    # If no children left after cleaning and role is structural, remove node
    if not cleaned_children:
        # Only remove node if its role is explicitly generic or none
        return None if node_role in ("generic", "none") else {**node, "children": []}

    # 6) Return the updated node
    updated_node = {**node, "children": cleaned_children}
    return updated_node


def _extract_url_from_ax_node(
    ax_node: Union[AccessibilityNode, AXNode],
) -> Optional[str]:
    """Extracts URL from the properties of an Accessibility Node."""
    properties = ax_node.get("properties")
    if not properties:
        return None
    for prop in properties:
        if prop.get("name") == "url":
            value_obj = prop.get("value")
            if value_obj and isinstance(value_obj.get("value"), str):
                return value_obj["value"].strip()
    return None


async def build_hierarchical_tree(
    nodes: list[AXNode],
    page: Optional["StagehandPage"],
    logger: Optional[StagehandLogger],
) -> TreeResult:
    """Builds a hierarchical tree structure from a flat array of accessibility nodes."""
    id_to_url: dict[str, str] = {}
    node_map: dict[str, AccessibilityNode] = {}
    iframe_list: list[AccessibilityNode] = []  # Simplified iframe node info

    # First pass: Create meaningful nodes
    for node_data in nodes:
        node_id = node_data.get("nodeId")
        if not node_id or int(node_id) < 0:
            continue

        url = _extract_url_from_ax_node(node_data)
        if url:
            id_to_url[node_id] = url

        has_children = bool(node_data.get("childIds"))
        name_value = node_data.get("name", {}).get("value")
        has_valid_name = bool(name_value and str(name_value).strip())
        role_value = node_data.get("role", {}).get("value", "")

        is_interactive = role_value not in ("none", "generic", "InlineTextBox")

        if not has_valid_name and not has_children and not is_interactive:
            continue

        processed_node: AccessibilityNode = {
            "nodeId": node_id,
            "role": role_value,
            # Optional fields
            **({"name": str(name_value)} if has_valid_name else {}),
            **(
                {"description": str(node_data.get("description", {}).get("value"))}
                if node_data.get("description", {}).get("value")
                else {}
            ),
            **(
                {"value": str(node_data.get("value", {}).get("value"))}
                if node_data.get("value", {}).get("value")
                else {}
            ),
            **(
                {"backendDOMNodeId": node_data["backendDOMNodeId"]}
                if "backendDOMNodeId" in node_data
                else {}
            ),
            **(
                {"properties": node_data["properties"]}
                if "properties" in node_data
                else {}
            ),
            **({"parentId": node_data["parentId"]} if "parentId" in node_data else {}),
            **({"childIds": node_data["childIds"]} if "childIds" in node_data else {}),
        }
        node_map[node_id] = processed_node

    # Second pass: Establish parent-child relationships using childIds and node_map
    all_nodes_in_map = list(node_map.values())
    for node in all_nodes_in_map:
        node_id = node["nodeId"]
        parent_id = node.get("parentId")

        # Add iframes to list
        if node.get("role") == "Iframe":
            iframe_list.append({"role": "Iframe", "nodeId": node_id})

        if parent_id and parent_id in node_map:
            parent_node = node_map[parent_id]
            if "children" not in parent_node:
                parent_node["children"] = []
            # Ensure we add the node from the map, not the original iteration node
            if node_id in node_map:
                parent_node["children"].append(node_map[node_id])

    # Final pass: Build root-level tree and clean up
    root_nodes = [node for node in node_map.values() if not node.get("parentId")]

    cleaned_tree_tasks = [
        _clean_structural_nodes(node, page, logger) for node in root_nodes
    ]
    final_tree_nullable = await asyncio.gather(*cleaned_tree_tasks)
    final_tree = [node for node in final_tree_nullable if node is not None]

    # Generate simplified string representation
    simplified_format = "\n".join(format_simplified_tree(node) for node in final_tree)

    return {
        "tree": final_tree,
        "simplified": simplified_format,
        "iframes": iframe_list,
        "idToUrl": id_to_url,
    }


async def get_accessibility_tree(
    page: "StagehandPage",
    logger: StagehandLogger,
) -> TreeResult:
    """Retrieves the full accessibility tree via CDP and transforms it."""
    try:
        start_time = time.time()
        scrollable_backend_ids = await find_scrollable_element_ids(page)
        cdp_result = await page.send_cdp("Accessibility.getFullAXTree")
        nodes: list[AXNode] = cdp_result.get("nodes", [])
        processing_start_time = time.time()

        for node_data in nodes:
            backend_id = node_data.get("backendDOMNodeId")
            role_value_obj = node_data.get("role")
            role_value = role_value_obj.get("value", "") if role_value_obj else ""

            if backend_id in scrollable_backend_ids:
                if role_value in ("generic", "none", ""):
                    new_role = "scrollable"
                else:
                    new_role = f"scrollable, {role_value}"
                # Update the node data directly before passing to build_hierarchical_tree
                if role_value_obj:
                    role_value_obj["value"] = new_role
                else:
                    node_data["role"] = {
                        "type": "string",
                        "value": new_role,
                    }  # Create role if missing

        hierarchical_tree = await build_hierarchical_tree(nodes, page, logger)

        end_time = time.time()
        # Use logger.debug
        logger.debug(
            message=(
                f"got accessibility tree in {int((end_time - start_time) * 1000)}ms "
                f"(processing: {int((end_time - processing_start_time) * 1000)}ms)"
            ),
        )
        return hierarchical_tree

    except Exception as error:
        # Use logger.error (level 0)
        logger.error(
            message="Error getting accessibility tree",
            auxiliary={"error": {"value": str(error), "type": "string"}},
        )
        raise error
    finally:
        # Ensure Accessibility domain is disabled even if errors occur
        # Need to check if page object still exists and has a CDP session
        if page and hasattr(page, "_cdp_session") and page._cdp_session:
            try:
                await page.disable_cdp_domain("Accessibility")
            except Exception:
                # Use logger.debug (level 2)
                logger.debug("Failed to disable Accessibility domain on cleanup.")


# JavaScript function to get XPath (remains JavaScript)
_GET_NODE_PATH_FUNCTION_STRING = """
function getNodePath(el) {
  if (!el || (el.nodeType !== Node.ELEMENT_NODE && el.nodeType !== Node.TEXT_NODE)) {
    console.log("el is not a valid node type");
    return "";
  }

  const parts = [];
  let current = el;

  while (current && (current.nodeType === Node.ELEMENT_NODE || current.nodeType === Node.TEXT_NODE)) {
    let index = 0;
    let hasSameTypeSiblings = false;
    const siblings = current.parentElement
      ? Array.from(current.parentElement.childNodes)
      : [];

    for (let i = 0; i < siblings.length; i++) {
      const sibling = siblings[i];
      if (
        sibling.nodeType === current.nodeType &&
        sibling.nodeName === current.nodeName
      ) {
        index = index + 1;
        hasSameTypeSiblings = true;
        if (sibling.isSameNode(current)) {
          break;
        }
      }
    }

    if (!current || !current.parentNode) break;
    if (current.nodeName.toLowerCase() === "html"){
      parts.unshift("html");
      break;
    }

    // text nodes are handled differently in XPath
    if (current.nodeName !== "#text") {
      const tagName = current.nodeName.toLowerCase();
      const pathIndex = hasSameTypeSiblings ? `[${index}]` : "";
      parts.unshift(`${tagName}${pathIndex}`);
    }
    
    current = current.parentElement;
  }

  return parts.length ? `/${parts.join("/")}` : "";
}
"""


async def get_xpath_by_resolved_object_id(
    cdp_client: CDPSession,  # Use Playwright CDPSession
    resolved_object_id: str,
) -> str:
    """Gets the XPath of an element given its resolved CDP object ID."""
    try:
        result = await cdp_client.send(
            "Runtime.callFunctionOn",
            {
                "objectId": resolved_object_id,
                "functionDeclaration": (
                    f"function() {{ {_GET_NODE_PATH_FUNCTION_STRING} return getNodePath(this); }}"
                ),
                "returnByValue": True,
            },
        )
        return result.get("result", {}).get("value") or ""
    except Exception:
        # Log or handle error appropriately
        return ""


async def find_scrollable_element_ids(stagehand_page: "StagehandPage") -> set[int]:
    """Identifies backendNodeIds of scrollable elements in the DOM."""
    # Ensure getScrollableElementXpaths is defined in the page context
    try:
        await stagehand_page.ensure_injection()
        xpaths = await stagehand_page.evaluate(
            "() => window.getScrollableElementXpaths()"
        )
        if not isinstance(xpaths, list):
            print("Warning: window.getScrollableElementXpaths() did not return a list.")
            xpaths = []
    except Exception as e:
        print(f"Error calling window.getScrollableElementXpaths: {e}")
        xpaths = []

    scrollable_backend_ids: set[int] = set()
    cdp_session = None
    try:
        # Create a single CDP session for efficiency
        cdp_session = await stagehand_page.context.new_cdp_session(stagehand_page._page)

        for xpath in xpaths:
            if not xpath or not isinstance(xpath, str):
                continue

            try:
                # Evaluate XPath to get objectId
                eval_result = await cdp_session.send(
                    "Runtime.evaluate",
                    {
                        "expression": (
                            f"""
                        (function() {{
                          try {{
                            const res = document.evaluate({json.dumps(xpath)}, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                            return res.singleNodeValue;
                          }} catch (e) {{
                             console.error('Error evaluating XPath:', {json.dumps(xpath)}, e);
                             return null;
                          }}
                        }})();
                    """
                        ),
                        "returnByValue": False,  # Get objectId
                        "awaitPromise": False,  # It's not a promise
                    },
                )

                object_id = eval_result.get("result", {}).get("objectId")
                if object_id:
                    try:
                        # Describe node to get backendNodeId
                        node_info = await cdp_session.send(
                            "DOM.describeNode",
                            {
                                "objectId": object_id,
                            },
                        )
                        backend_node_id = node_info.get("node", {}).get("backendNodeId")
                        if backend_node_id:
                            scrollable_backend_ids.add(backend_node_id)
                    except Exception:
                        # Log error describing node if needed
                        # print(f"Error describing node for xpath {xpath}: {desc_err}")
                        pass  # Continue to next xpath
            except Exception:
                # Log error evaluating xpath if needed
                # print(f"Error evaluating xpath {xpath}: {eval_err}")
                pass  # Continue to next xpath

    except Exception as session_err:
        print(f"Error creating or using CDP session: {session_err}")
        # Handle session creation error if necessary
    finally:
        if cdp_session:
            try:
                await cdp_session.detach()
            except Exception:
                pass  # Ignore detach error

    return scrollable_backend_ids


def _remove_redundant_static_text_children(
    parent: AccessibilityNode,
    children: list[AccessibilityNode],
) -> list[AccessibilityNode]:
    """Removes StaticText children if their combined text matches the parent's name."""
    parent_name = parent.get("name")
    if not parent_name:
        return children

    # Normalize parent name (replace multiple spaces with one and trim)
    normalized_parent_name = re.sub(r"\s+", " ", parent_name).strip()
    if not normalized_parent_name:  # Skip if parent name is only whitespace
        return children

    static_text_children = [
        child
        for child in children
        if child.get("role") == "StaticText" and child.get("name")
    ]

    # Normalize and combine child text
    combined_child_text = "".join(
        re.sub(r"\s+", " ", child.get("name", "")).strip()
        for child in static_text_children
    )

    # If combined text matches parent's name, filter out those StaticText nodes
    if combined_child_text == normalized_parent_name:
        return [
            child
            for child in children
            if child.get("role") != "StaticText" or not child.get("name")
        ]  # Keep StaticText without name if any

    return children
