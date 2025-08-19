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
        # Map frame IDs to StagehandPage instances
        self.frame_id_map = {}

    async def new_page(self) -> StagehandPage:
        pw_page: Page = await self._context.new_page()
        stagehand_page = await self.create_stagehand_page(pw_page)
        self.set_active_page(stagehand_page)
        return stagehand_page

    async def create_stagehand_page(self, pw_page: Page) -> StagehandPage:
        # Create a StagehandPage wrapper for the given Playwright page
        stagehand_page = StagehandPage(pw_page, self.stagehand, self)
        await self.inject_custom_scripts(pw_page)
        self.page_map[pw_page] = stagehand_page

        # Initialize frame tracking for this page
        await self._attach_frame_navigated_listener(pw_page, stagehand_page)

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

    def register_frame_id(self, frame_id: str, page: StagehandPage):
        """Register a frame ID to StagehandPage mapping."""
        self.frame_id_map[frame_id] = page

    def unregister_frame_id(self, frame_id: str):
        """Unregister a frame ID from the mapping."""
        if frame_id in self.frame_id_map:
            del self.frame_id_map[frame_id]

    def get_stagehand_page_by_frame_id(self, frame_id: str) -> StagehandPage:
        """Get StagehandPage by frame ID."""
        return self.frame_id_map.get(frame_id)

    @classmethod
    async def init(cls, context: BrowserContext, stagehand):
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

    async def _attach_frame_navigated_listener(
        self, pw_page: Page, stagehand_page: StagehandPage
    ):
        """
        Attach CDP listener for frame navigation events to track frame IDs.
        This mirrors the TypeScript implementation's frame tracking.
        """
        try:
            # Create CDP session for the page
            cdp_session = await self._context.new_cdp_session(pw_page)
            await cdp_session.send("Page.enable")

            # Get the current root frame ID
            frame_tree = await cdp_session.send("Page.getFrameTree")
            root_frame_id = frame_tree.get("frameTree", {}).get("frame", {}).get("id")

            if root_frame_id:
                # Initialize the page with its frame ID
                stagehand_page.update_root_frame_id(root_frame_id)
                self.register_frame_id(root_frame_id, stagehand_page)

            # Set up event listener for frame navigation
            def on_frame_navigated(params):
                """Handle Page.frameNavigated events"""
                frame = params.get("frame", {})
                frame_id = frame.get("id")
                parent_id = frame.get("parentId")

                # Only track root frames (no parent)
                if not parent_id and frame_id:
                    # Skip if it's the same frame ID
                    if frame_id == stagehand_page.frame_id:
                        return

                    # Unregister old frame ID if exists
                    old_id = stagehand_page.frame_id
                    if old_id:
                        self.unregister_frame_id(old_id)

                    # Register new frame ID
                    self.register_frame_id(frame_id, stagehand_page)
                    stagehand_page.update_root_frame_id(frame_id)

                    self.stagehand.logger.debug(
                        f"Frame navigated from {old_id} to {frame_id}",
                        category="context",
                    )

            # Register the event listener
            cdp_session.on("Page.frameNavigated", on_frame_navigated)

            # Clean up frame ID when page closes
            def on_page_close():
                if stagehand_page.frame_id:
                    self.unregister_frame_id(stagehand_page.frame_id)

            pw_page.once("close", on_page_close)

        except Exception as e:
            self.stagehand.logger.error(
                f"Failed to attach frame navigation listener: {str(e)}",
                category="context",
            )
