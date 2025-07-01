import json
from collections.abc import Coroutine
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from stagehand.page import StagehandPage

from playwright.async_api import Locator, Page


@dataclass
class MethodHandlerContext:
    method: str
    locator: Locator
    xpath: str
    args: list[Any]
    stagehand_page: "StagehandPage"
    initial_url: str
    logger: Callable = None
    dom_settle_timeout_ms: Optional[int] = None


async def scroll_to_next_chunk(ctx: MethodHandlerContext) -> None:
    ctx.logger.debug(
        message="scrolling to next chunk",
        category="action",
        auxiliary={"xpath": {"value": ctx.xpath, "type": "string"}},
    )
    try:
        await ctx.stagehand_page._page.evaluate(
            """
            ({ xpath }) => {
                const getNodeFromXpath = (xpath) => { // Placeholder
                    return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                };
                window.waitForElementScrollEnd = (element) => { // Placeholder
                    return new Promise(resolve => {
                        let lastScrollTime = Date.now();
                        const scrollListener = () => {
                            if (Date.now() - lastScrollTime > 100) { // 100ms of no scrolling
                                element.removeEventListener('scroll', scrollListener);
                                resolve();
                            }
                            lastScrollTime = Date.now();
                        };
                        element.addEventListener('scroll', scrollListener);
                        // Initial check in case it's already not scrolling
                        setTimeout(() => {
                             if (Date.now() - lastScrollTime > 100) {
                                element.removeEventListener('scroll', scrollListener);
                                resolve();
                            }
                        },150);

                    });
                };

                const elementNode = getNodeFromXpath(xpath);
                if (!elementNode || elementNode.nodeType !== Node.ELEMENT_NODE) {
                    console.warn(`Could not locate element to scroll by its height.`);
                    return Promise.resolve();
                }

                const element = elementNode;
                const tagName = element.tagName.toLowerCase();
                let height;

                if (tagName === "html" || tagName === "body") {
                    height = window.visualViewport.height;
                    window.scrollBy({
                        top: height,
                        left: 0,
                        behavior: "smooth",
                    });
                    const scrollingEl = document.scrollingElement || document.documentElement;
                    return window.waitForElementScrollEnd(scrollingEl);
                } else {
                    height = element.getBoundingClientRect().height;
                    element.scrollBy({
                        top: height,
                        left: 0,
                        behavior: "smooth",
                    });
                    return window.waitForElementScrollEnd(element);
                }
            }
            """,
            {"xpath": ctx.xpath},
        )
    except Exception as e:
        ctx.logger.error(
            message="error scrolling to next chunk",
            category="action",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "xpath": {"value": ctx.xpath, "type": "string"},
            },
        )
        raise e


async def scroll_to_previous_chunk(ctx: MethodHandlerContext) -> None:
    ctx.logger.debug(
        message="scrolling to previous chunk",
        category="action",
        auxiliary={"xpath": {"value": ctx.xpath, "type": "string"}},
    )
    try:
        await ctx.stagehand_page._page.evaluate(
            """
            ({ xpath }) => {
                const getNodeFromXpath = (xpath) => { // Placeholder
                     return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                };
                 window.waitForElementScrollEnd = (element) => { // Placeholder
                    return new Promise(resolve => {
                        let lastScrollTime = Date.now();
                        const scrollListener = () => {
                            if (Date.now() - lastScrollTime > 100) { // 100ms of no scrolling
                                element.removeEventListener('scroll', scrollListener);
                                resolve();
                            }
                            lastScrollTime = Date.now();
                        };
                        element.addEventListener('scroll', scrollListener);
                        setTimeout(() => {
                             if (Date.now() - lastScrollTime > 100) {
                                element.removeEventListener('scroll', scrollListener);
                                resolve();
                            }
                        },150);
                    });
                };

                const elementNode = getNodeFromXpath(xpath);
                if (!elementNode || elementNode.nodeType !== Node.ELEMENT_NODE) {
                    console.warn(`Could not locate element to scroll by its height.`);
                    return Promise.resolve();
                }

                const element = elementNode;
                const tagName = element.tagName.toLowerCase();
                let height;

                if (tagName === "html" || tagName === "body") {
                    height = window.visualViewport.height;
                    window.scrollBy({
                        top: -height,
                        left: 0,
                        behavior: "smooth",
                    });
                     const scrollingEl = document.scrollingElement || document.documentElement;
                    return window.waitForElementScrollEnd(scrollingEl);
                } else {
                    height = element.getBoundingClientRect().height;
                    element.scrollBy({
                        top: -height,
                        left: 0,
                        behavior: "smooth",
                    });
                    return window.waitForElementScrollEnd(element);
                }
            }
            """,
            {"xpath": ctx.xpath},
        )
    except Exception as e:
        ctx.logger.error(
            message="error scrolling to previous chunk",
            category="action",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "xpath": {"value": ctx.xpath, "type": "string"},
            },
        )
        raise e


async def scroll_element_into_view(ctx: MethodHandlerContext) -> None:
    ctx.logger.debug(
        message="scrolling element into view",
        category="action",
        auxiliary={"xpath": {"value": ctx.xpath, "type": "string"}},
    )
    try:
        await ctx.locator.evaluate(
            "(element) => { element.scrollIntoView({ behavior: 'smooth', block: 'center' }); }"
        )
    except Exception as e:
        ctx.logger.error(
            message="error scrolling element into view",
            category="action",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "xpath": {"value": ctx.xpath, "type": "string"},
            },
        )
        raise e


async def scroll_element_to_percentage(ctx: MethodHandlerContext) -> None:
    ctx.logger.debug(
        message="scrolling element vertically to specified percentage",
        category="action",
        auxiliary={
            "xpath": {"value": ctx.xpath, "type": "string"},
            "coordinate": {"value": json.dumps(ctx.args), "type": "string"},
        },
    )
    try:
        y_arg = ctx.args[0] if ctx.args else "0%"
        await ctx.stagehand_page._page.evaluate(
            """
            ({ xpath, yArg }) => {
                const getNodeFromXpath = (xpath) => { // Placeholder
                     return document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                };
                function parsePercent(val) {
                    const cleaned = val.trim().replace("%", "");
                    const num = parseFloat(cleaned);
                    return Number.isNaN(num) ? 0 : Math.max(0, Math.min(num, 100));
                }

                const elementNode = getNodeFromXpath(xpath);
                if (!elementNode || elementNode.nodeType !== Node.ELEMENT_NODE) {
                    console.warn(`Could not locate element to scroll on.`);
                    return;
                }

                const element = elementNode;
                const yPct = parsePercent(yArg);

                if (element.tagName.toLowerCase() === "html") {
                    const scrollHeight = document.body.scrollHeight;
                    const viewportHeight = window.innerHeight;
                    const scrollTop = (scrollHeight - viewportHeight) * (yPct / 100);
                    window.scrollTo({
                        top: scrollTop,
                        left: window.scrollX,
                        behavior: "smooth",
                    });
                } else {
                    const scrollHeight = element.scrollHeight;
                    const clientHeight = element.clientHeight;
                    const scrollTop = (scrollHeight - clientHeight) * (yPct / 100);
                    element.scrollTo({
                        top: scrollTop,
                        left: element.scrollLeft,
                        behavior: "smooth",
                    });
                }
            }
            """,
            {"xpath": ctx.xpath, "yArg": y_arg},
        )
    except Exception as e:
        ctx.logger.error(
            message="error scrolling element vertically to percentage",
            category="action",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "xpath": {"value": ctx.xpath, "type": "string"},
                "args": {"value": json.dumps(ctx.args), "type": "object"},
            },
        )
        raise e


async def fill_or_type(ctx: MethodHandlerContext) -> None:
    try:
        await ctx.locator.fill("", force=True)
        text = str(ctx.args[0]) if ctx.args and ctx.args[0] is not None else ""
        await ctx.locator.fill(text, force=True)
    except Exception as e:
        ctx.logger.error(
            message="error filling element",
            category="action",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "xpath": {"value": ctx.xpath, "type": "string"},
            },
        )
        raise e


async def press_key(ctx: MethodHandlerContext) -> None:
    try:
        key = str(ctx.args[0]) if ctx.args and ctx.args[0] is not None else ""
        await ctx.locator._page.keyboard.press(key)
        await handle_possible_page_navigation(
            "press",
            ctx.xpath,
            ctx.initial_url,
            ctx.stagehand_page,
            ctx.logger,
            ctx.dom_settle_timeout_ms,
        )
    except Exception as e:
        ctx.logger.error(
            message="error pressing key",
            category="action",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "key": {
                    "value": (
                        str(ctx.args[0])
                        if ctx.args and ctx.args[0] is not None
                        else "unknown"
                    ),
                    "type": "string",
                },
            },
        )
        raise e


async def click_element(ctx: MethodHandlerContext) -> None:
    ctx.logger.debug(
        message=f"page URL before click {ctx.stagehand_page._page.url}",
        category="action",
    )
    try:
        # Using JavaScript click
        await ctx.locator.evaluate("(el) => el.click()")
        await handle_possible_page_navigation(
            "click",
            ctx.xpath,
            ctx.initial_url,
            ctx.stagehand_page,
            ctx.logger,
            ctx.dom_settle_timeout_ms,
        )
    except Exception as e:
        ctx.logger.error(
            message="error performing click",
            category="act",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "xpath": {"value": ctx.xpath, "type": "string"},
                "method": {"value": "click", "type": "string"},
                "args": {"value": json.dumps(ctx.args), "type": "object"},
            },
        )
        raise e


async def fallback_locator_method(ctx: MethodHandlerContext) -> None:
    ctx.logger.debug(
        message="page URL before action",
        category="action",
        auxiliary={"url": {"value": ctx.locator._page.url, "type": "string"}},
    )
    try:
        method_to_call = getattr(ctx.locator, ctx.method)
        # Convert args to strings, handling None
        str_args = [str(arg) if arg is not None else "" for arg in ctx.args]
        await method_to_call(*str_args)
    except Exception as e:
        ctx.logger.error(
            message="error performing method",
            category="action",
            auxiliary={
                "error": {"value": str(e), "type": "string"},
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "xpath": {"value": ctx.xpath, "type": "string"},
                "method": {"value": ctx.method, "type": "string"},
                "args": {"value": json.dumps(ctx.args), "type": "object"},
            },
        )
        raise e


async def handle_possible_page_navigation(
    action_description: str,
    xpath: str,
    initial_url: str,
    stagehand_page: "StagehandPage",
    logger: Callable = None,
    dom_settle_timeout_ms: Optional[int] = None,
) -> None:

    logger.info(
        message=f"{action_description}, checking for page navigation",
        category="action",
        auxiliary={"xpath": {"value": xpath, "type": "string"}},
    )

    # TODO: check for stagehand_page
    new_opened_tab: Optional[Page] = None
    try:
        async with stagehand_page.context.expect_page(timeout=1500) as new_page_info:
            # The action that might open a new tab should have already been performed
            # This is a bit different from JS Promise.race.
            # We are checking if a page was opened recently.
            # A more robust way might involve listening to 'page' event *before* the action.
            # However, to closely match the TS logic's timing:
            pass  # If a page was opened by the action, it should be caught here.
        new_opened_tab = await new_page_info.value
    except Exception:
        new_opened_tab = None

        logger.info(
            message=f"{action_description} complete",
            category="action",
            auxiliary={
                "newOpenedTab": {
                    "value": (
                        "opened a new tab" if new_opened_tab else "no new tabs opened"
                    ),
                    "type": "string",
                }
            },
        )

    if new_opened_tab and new_opened_tab.url != "about:blank":
        logger.info(
            message="new page detected (new tab) with URL",
            category="action",
            auxiliary={"url": {"value": new_opened_tab.url, "type": "string"}},
        )
        new_tab_url = new_opened_tab.url
        await new_opened_tab.close()
        await stagehand_page._page.goto(new_tab_url)
        await stagehand_page._page.wait_for_load_state("domcontentloaded")

    try:
        await stagehand_page._wait_for_settled_dom(dom_settle_timeout_ms)
    except Exception as e:
        logger.debug(
            message="wait for settled DOM timeout hit",
            category="action",
            auxiliary={
                "trace": {
                    "value": getattr(e, "__traceback__", ""),
                    "type": "string",
                },
                "message": {"value": str(e), "type": "string"},
            },
        )

    logger.info(
        message="finished waiting for (possible) page navigation",
        category="action",
    )

    if stagehand_page._page.url != initial_url:
        logger.info(
            message="new page detected with URL",
            category="action",
            auxiliary={"url": {"value": stagehand_page._page.url, "type": "string"}},
        )


method_handler_map: dict[
    str, Callable[[MethodHandlerContext], Coroutine[None, None, None]]
] = {
    "scrollIntoView": scroll_element_into_view,
    "scrollTo": scroll_element_to_percentage,
    "scroll": scroll_element_to_percentage,
    "mouse.wheel": (
        scroll_element_to_percentage
    ),  # Playwright Python doesn't have mouse.wheel on locator directly.
    # This might need a page.mouse.wheel(x, y) or evaluate.
    # For now, mapping to scroll percentage as in TS.
    "fill": fill_or_type,
    "type": fill_or_type,
    "press": press_key,
    "click": click_element,
    "nextChunk": scroll_to_next_chunk,
    "prevChunk": scroll_to_previous_chunk,
}
