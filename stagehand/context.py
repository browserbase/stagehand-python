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
        return self.page_map[pw_page]

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
        # Optionally update the active page in the stagehand client if needed
        if hasattr(self.stagehand, "_set_active_page"):
            self.stagehand._set_active_page(stagehand_page)

    def get_active_page(self) -> StagehandPage:
        return self.active_stagehand_page

    @classmethod
    async def init(cls, context: BrowserContext, stagehand):
        instance = cls(context, stagehand)
        # Pre-initialize StagehandPages for any existing pages
        for pw_page in instance._context.pages:
            await instance.create_stagehand_page(pw_page)
        if instance._context.pages:
            first_page = instance._context.pages[0]
            stagehand_page = await instance.get_stagehand_page(first_page)
            instance.set_active_page(stagehand_page)
        return instance

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
            # Wrap the pages method to return StagehandPage objects
            def wrapped_pages(*args, **kwargs):
                pw_pages = self._context.pages(*args, **kwargs)
                # This is synchronous, so we can't await here
                # We'll return the unwrapped pages and let the caller handle wrapping if needed
                return pw_pages

            return wrapped_pages
        return attr
