import asyncio
import os
import weakref

from playwright.async_api import BrowserContext, Page

from .page import StagehandPage


class StagehandContext:
    def __init__(self, context: BrowserContext, stagehand):
        self._context = context
        self.stagehand = stagehand
        # Use a weak key dictionary to map Playwright Pages to our StagehandPage wrappers
        self.page_map = weakref.WeakKeyDictionary()
        self.active_stagehand_page = None

    async def new_page(self) -> StagehandPage:
        pw_page: Page = await self._context.new_page()
        stagehand_page = await self.create_stagehand_page(pw_page)
        self.set_active_page(stagehand_page)
        return stagehand_page

    async def create_stagehand_page(self, pw_page: Page) -> StagehandPage:
        # Create a StagehandPage wrapper for the given Playwright page
        stagehand_page = StagehandPage(pw_page, self.stagehand)
        await self.inject_custom_scripts(pw_page)
        self.page_map[pw_page] = stagehand_page
        return stagehand_page

    async def inject_custom_scripts(self, pw_page: Page):
        script_path = os.path.join(os.path.dirname(__file__), "domScripts.js")
        try:
            with open(script_path) as f:
                script = f.read()
        except Exception as e:
            self.stagehand.logger.error(f"Error reading domScripts.js: {e}")
            script = "/* fallback injection script */"
        await pw_page.add_init_script(script)

    async def get_stagehand_page(self, pw_page: Page) -> StagehandPage:
        if pw_page not in self.page_map:
            return await self.create_stagehand_page(pw_page)
        stagehand_page = self.page_map[pw_page]
        return stagehand_page

    async def get_stagehand_pages(self) -> list:
        # Return a list of StagehandPage wrappers for all pages in the context
        pages = self._context.pages
        result = []
        for pw_page in pages:
            stagehand_page = await self.get_stagehand_page(pw_page)
            result.append(stagehand_page)
        return result

    def set_active_page(self, stagehand_page: StagehandPage):
        self.active_stagehand_page = stagehand_page
        # Update the active page in the stagehand client
        if hasattr(self.stagehand, "_set_active_page"):
            self.stagehand._set_active_page(stagehand_page)
            self.stagehand.logger.debug(
                f"Set active page to: {stagehand_page.url}", category="context"
            )
        else:
            self.stagehand.logger.debug(
                "Stagehand does not have _set_active_page method", category="context"
            )

    def get_active_page(self) -> StagehandPage:
        return self.active_stagehand_page

    @classmethod
    async def init(cls, context: BrowserContext, stagehand):
        stagehand.logger.debug("StagehandContext.init() called", category="context")
        instance = cls(context, stagehand)
        # Pre-initialize StagehandPages for any existing pages
        stagehand.logger.debug(
            f"Found {len(instance._context.pages)} existing pages", category="context"
        )
        for pw_page in instance._context.pages:
            await instance.create_stagehand_page(pw_page)
        if instance._context.pages:
            first_page = instance._context.pages[0]
            stagehand_page = await instance.get_stagehand_page(first_page)
            instance.set_active_page(stagehand_page)

        # Add event listener for new pages (popups, new tabs from window.open, etc.)
        def handle_page_event(pw_page):
            # Playwright expects sync handler, so we schedule the async work
            asyncio.create_task(instance._handle_new_page(pw_page))

        context.on("page", handle_page_event)

        return instance

    async def _handle_new_page(self, pw_page: Page):
        """
        Handle new pages created by the browser (popups, window.open, etc.).
        Uses the page switch lock to prevent race conditions with ongoing operations.
        """
        try:
            # Use wait_for for Python 3.10 compatibility (timeout prevents indefinite blocking)
            async def handle_with_lock():
                async with self.stagehand._page_switch_lock:
                    self.stagehand.logger.debug(
                        f"Creating StagehandPage for new page with URL: {pw_page.url}",
                        category="context",
                    )
                    stagehand_page = await self.create_stagehand_page(pw_page)
                    self.set_active_page(stagehand_page)
                    self.stagehand.logger.debug(
                        "New page detected and initialized", category="context"
                    )

            await asyncio.wait_for(handle_with_lock(), timeout=30)
        except asyncio.TimeoutError:
            self.stagehand.logger.error(
                f"Timeout waiting for page switch lock when handling new page: {pw_page.url}",
                category="context",
            )
        except Exception as e:
            self.stagehand.logger.error(
                f"Failed to initialize new page: {str(e)}", category="context"
            )

    def __getattr__(self, name):
        # Forward attribute lookups to the underlying BrowserContext
        attr = getattr(self._context, name)

        # Special handling for methods that return pages
        if name == "new_page":
            # Replace with our own implementation that wraps the page
            async def wrapped_new_page(*args, **kwargs):
                pw_page = await self._context.new_page(*args, **kwargs)
                stagehand_page = await self.create_stagehand_page(pw_page)
                self.set_active_page(stagehand_page)
                return stagehand_page

            return wrapped_new_page
        elif name == "pages":

            async def wrapped_pages():
                pw_pages = self._context.pages
                # Return StagehandPage objects
                result = []
                for pw_page in pw_pages:
                    stagehand_page = await self.get_stagehand_page(pw_page)
                    result.append(stagehand_page)
                return result

            return wrapped_pages
        return attr
