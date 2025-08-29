import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Playwright,
)

from .context import StagehandContext
from .logging import StagehandLogger
from .page import StagehandPage


async def connect_browser(
    playwright: Playwright,
    browser_launch_options: dict[str, Any],
    stagehand_instance: Any,
    logger: StagehandLogger,
) -> tuple[
    Optional[Browser], BrowserContext, StagehandContext, StagehandPage, Optional[Path]
]:
    """
    Connect to a local browser via CDP or launch a new browser context.

    Args:
        playwright: The Playwright instance
        browser_launch_options: Options for launching the browser
        stagehand_instance: The Stagehand instance (for context initialization)
        logger: The logger instance

    Returns:
        tuple of (browser, context, stagehand_context, page, temp_user_data_dir)
    """
    cdp_url = browser_launch_options.get("cdp_url")
    temp_user_data_dir = None

    if cdp_url:
        logger.info(f"Connecting to browser via CDP URL: {cdp_url}")
        try:
            browser = await playwright.chromium.connect_over_cdp(
                cdp_url, headers=browser_launch_options.get("headers")
            )

            if not browser.contexts:
                raise RuntimeError(f"No browser contexts found at CDP URL: {cdp_url}")
            context = browser.contexts[0]
            stagehand_context = await StagehandContext.init(context, stagehand_instance)
            logger.debug(f"Connected via CDP. Using context: {context}")
        except Exception as e:
            logger.error(f"Failed to connect via CDP URL ({cdp_url}): {str(e)}")
            raise
    else:
        logger.info("Launching new browser context...")
        browser = None

        user_data_dir_option = browser_launch_options.get("user_data_dir")
        if user_data_dir_option:
            user_data_dir = Path(user_data_dir_option).resolve()
        else:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="stagehand_ctx_")
            temp_user_data_dir = Path(temp_dir)
            user_data_dir = temp_user_data_dir
            # Create Default profile directory and Preferences file like in TS
            default_profile_path = user_data_dir / "Default"
            default_profile_path.mkdir(parents=True, exist_ok=True)
            prefs_path = default_profile_path / "Preferences"
            default_prefs = {"plugins": {"always_open_pdf_externally": True}}
            try:
                with open(prefs_path, "w") as f:
                    json.dump(default_prefs, f)
                logger.debug(
                    f"Created temporary user_data_dir with default preferences: {user_data_dir}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to write default preferences to {prefs_path}: {e}"
                )

        downloads_path_option = browser_launch_options.get("downloads_path")
        if downloads_path_option:
            downloads_path = str(Path(downloads_path_option).resolve())
        else:
            downloads_path = str(Path.cwd() / "downloads")
        try:
            os.makedirs(downloads_path, exist_ok=True)
            logger.debug(f"Using downloads_path: {downloads_path}")
        except Exception as e:
            logger.error(f"Failed to create downloads_path {downloads_path}: {e}")

        # Prepare Launch Options (translate keys if needed)
        launch_options = {
            "headless": browser_launch_options.get("headless", False),
            "accept_downloads": browser_launch_options.get(
                "acceptDownloads", True
            ),
            "downloads_path": downloads_path,
            "args": browser_launch_options.get(
                "args",
                [
                    "--disable-blink-features=AutomationControlled",
                ],
            ),
            "viewport": browser_launch_options.get(
                "viewport", {"width": 1024, "height": 768}
            ),
            "locale": browser_launch_options.get("locale", "en-US"),
            "timezone_id": browser_launch_options.get(
                "timezoneId", "America/New_York"
            ),
            "bypass_csp": browser_launch_options.get("bypassCSP", True),
            "proxy": browser_launch_options.get("proxy"),
            "ignore_https_errors": browser_launch_options.get(
                "ignoreHTTPSErrors", True
            ),
        }
        launch_options = {k: v for k, v in launch_options.items() if v is not None}

        # Launch Context
        try:
            context = await playwright.chromium.launch_persistent_context(
                str(user_data_dir),  # Needs to be string path
                **launch_options,
            )
            stagehand_context = await StagehandContext.init(context, stagehand_instance)
            logger.info("Browser context launched successfully.")
            browser = context.browser

        except Exception as e:
            logger.error(f"Failed to launch browser context: {str(e)}")
            if temp_user_data_dir:
                try:
                    shutil.rmtree(temp_user_data_dir)
                except Exception:
                    pass
            raise

        cookies = browser_launch_options.get("cookies")
        if cookies:
            try:
                await context.add_cookies(cookies)
                logger.debug(f"Added {len(cookies)} cookies to the context.")
            except Exception as e:
                logger.error(f"Failed to add cookies: {e}")

    # Apply stealth scripts
    await apply_stealth_scripts(context, logger)

    # Get the initial page (usually one is created by default)
    if context.pages:
        playwright_page = context.pages[0]
        logger.debug("Using initial page from context.")
        page = await stagehand_context.get_stagehand_page(playwright_page)
    else:
        logger.debug("No initial page found, creating a new one.")
        page = await stagehand_context.new_page()

    return browser, context, stagehand_context, page, temp_user_data_dir


async def apply_stealth_scripts(context: BrowserContext, logger: StagehandLogger):
    """Applies JavaScript init scripts to make the browser less detectable."""
    logger.debug("Applying stealth scripts to the context...")
    stealth_script = """
    (() => {
        // Override navigator.webdriver
        if (navigator.webdriver) {
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        }

        // Mock languages and plugins
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Avoid complex plugin mocking, just return a non-empty array like structure
        if (navigator.plugins instanceof PluginArray && navigator.plugins.length === 0) {
             Object.defineProperty(navigator, 'plugins', {
                get: () => Object.values({
                    'plugin1': { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                    'plugin2': { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
                    'plugin3': { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
                }),
            });
        }

        // Remove Playwright-specific properties from window
        try {
            delete window.__playwright_run; // Example property, check actual properties if needed
            delete window.navigator.__proto__.webdriver; // Another common place
        } catch (e) {}

        // Override permissions API (example for notifications)
        if (window.navigator && window.navigator.permissions) {
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => {
                if (parameters && parameters.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission });
                }
                // Call original for other permissions
                return originalQuery.apply(window.navigator.permissions, [parameters]);
            };
        }
    })();
    """
    try:
        await context.add_init_script(stealth_script)
    except Exception as e:
        logger.error(f"Failed to add stealth init script: {str(e)}")


async def cleanup_browser_resources(
    browser: Optional[Browser],
    context: Optional[BrowserContext],
    playwright: Optional[Playwright],
    temp_user_data_dir: Optional[Path],
    logger: StagehandLogger,
):
    """
    Clean up browser resources.

    Args:
        browser: The browser instance (if any)
        context: The browser context
        playwright: The Playwright instance
        temp_user_data_dir: Temporary user data directory to remove (if any)
        logger: The logger instance
    """
    if context:
        try:
            logger.debug("Closing browser context...")
            await context.close()
        except Exception as e:
            logger.error(f"Error closing context: {str(e)}")
    if browser:
        try:
            logger.debug("Closing browser...")
            await browser.close()
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

    # Clean up temporary user data directory if created
    if temp_user_data_dir:
        try:
            logger.debug(
                f"Removing temporary user data directory: {temp_user_data_dir}"
            )
            shutil.rmtree(temp_user_data_dir)
        except Exception as e:
            logger.error(
                f"Error removing temporary directory {temp_user_data_dir}: {str(e)}"
            )

    if playwright:
        try:
            logger.debug("Stopping Playwright...")
            await playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping Playwright: {str(e)}")
