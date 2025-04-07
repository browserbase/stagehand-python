import os
import weakref

from playwright.sync_api import BrowserContext, Page

from .page import SyncStagehandPage


class SyncStagehandContext:
    def __init__(self, context: BrowserContext, stagehand):
        self._context = context
        self.stagehand = stagehand
        # Use a weak key dictionary to map Playwright Pages to our StagehandPage wrappers
        self.page_map = weakref.WeakKeyDictionary()
        self.active_stagehand_page = None

    def new_page(self) -> SyncStagehandPage:
        pw_page: Page = self._context.new_page()
        stagehand_page = self.create_stagehand_page(pw_page)
        self.set_active_page(stagehand_page)
        return stagehand_page

    def create_stagehand_page(self, pw_page: Page) -> SyncStagehandPage:
        # Create a SyncStagehandPage wrapper for the given Playwright page
        stagehand_page = SyncStagehandPage(pw_page, self.stagehand)
        self.inject_custom_scripts(pw_page)
        self.page_map[pw_page] = stagehand_page
        return stagehand_page

    def inject_custom_scripts(self, pw_page: Page):
        script_path = os.path.join(os.path.dirname(__file__), "..", "domScripts.js")
        try:
            with open(script_path) as f:
                script = f.read()
        except Exception as e:
            self.stagehand.logger.error(f"Error reading domScripts.js: {e}")
            script = "/* fallback injection script */"
        pw_page.add_init_script(script)

    def get_stagehand_page(self, pw_page: Page) -> SyncStagehandPage:
        if pw_page not in self.page_map:
            return self.create_stagehand_page(pw_page)
        return self.page_map[pw_page]

    def get_stagehand_pages(self) -> list:
        # Return a list of SyncStagehandPage wrappers for all pages in the context
        pages = self._context.pages
        result = []
        for pw_page in pages:
            stagehand_page = self.get_stagehand_page(pw_page)
            result.append(stagehand_page)
        return result

    def set_active_page(self, stagehand_page: SyncStagehandPage):
        self.active_stagehand_page = stagehand_page
        # Optionally update the active page in the stagehand client if needed
        if hasattr(self.stagehand, "_set_active_page"):
            self.stagehand._set_active_page(stagehand_page)

    def get_active_page(self) -> SyncStagehandPage:
        return self.active_stagehand_page

    @classmethod
    def init(cls, context: BrowserContext, stagehand):
        instance = cls(context, stagehand)
        # Pre-initialize SyncStagehandPages for any existing pages
        for pw_page in instance._context.pages:
            instance.create_stagehand_page(pw_page)
        if instance._context.pages:
            first_page = instance._context.pages[0]
            stagehand_page = instance.get_stagehand_page(first_page)
            instance.set_active_page(stagehand_page)
        return instance

    def __getattr__(self, name):
        # Forward attribute lookups to the underlying BrowserContext
        return getattr(self._context, name)
