from typing import Any


def find_items_with_images(items: list[dict[str, Any]]) -> list[int]:
    """
    Finds all items in the conversation history that contain images

    Args:
        items: Array of conversation items to check

    Returns:
        Array of indices where images were found
    """
    items_with_images = []

    for index, item in enumerate(items):
        has_image = False

        if isinstance(item.get("content"), list):
            has_image = any(
                content_item.get("type") == "tool_result"
                and "content" in content_item
                and isinstance(content_item["content"], list)
                and any(
                    nested_item.get("type") == "image"
                    for nested_item in content_item["content"]
                    if isinstance(nested_item, dict)
                )
                for content_item in item["content"]
                if isinstance(content_item, dict)
            )

        if has_image:
            items_with_images.append(index)

    return items_with_images


def compress_conversation_images(
    items: list[dict[str, Any]], keep_most_recent_count: int = 2
) -> dict[str, list[dict[str, Any]]]:
    """
    Compresses conversation history by removing images from older items
    while keeping the most recent images intact

    Args:
        items: Array of conversation items to process
        keep_most_recent_count: Number of most recent image-containing items to preserve (default: 2)

    Returns:
        Dictionary with processed items
    """
    items_with_images = find_items_with_images(items)

    for index, item in enumerate(items):
        image_index = -1
        if index in items_with_images:
            image_index = items_with_images.index(index)

        should_compress = (
            image_index >= 0
            and image_index < len(items_with_images) - keep_most_recent_count
        )

        if should_compress:
            if isinstance(item.get("content"), list):
                new_content = []
                for content_item in item["content"]:
                    if isinstance(content_item, dict):
                        if (
                            content_item.get("type") == "tool_result"
                            and "content" in content_item
                            and isinstance(content_item["content"], list)
                            and any(
                                nested_item.get("type") == "image"
                                for nested_item in content_item["content"]
                                if isinstance(nested_item, dict)
                            )
                        ):
                            # Replace the content with a text placeholder
                            new_content.append(
                                {**content_item, "content": "screenshot taken"}
                            )
                        else:
                            new_content.append(content_item)
                    else:
                        new_content.append(content_item)

                item["content"] = new_content

    return {"items": items}
