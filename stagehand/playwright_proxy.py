# 1. Introduce a Playwright Layer in Python
# Create a new module, for instance, something like:
# • stagehand/playwright_proxy.py
# This will house our Playwright integration logic.
# Within this module, define a new class, e.g., StagehandPage. This class:
# • Subclasses (or composes) Playwright’s async Page object.
# • Intercepts calls relevant to AI features (act, extract, observe) and redirects them to the NextJS Stagehand server via the existing _execute() or similar proxy method.
# • Directly calls standard Playwright APIs (e.g. wait_for_selector, goto) for normal browser operations.
# Also define a context manager or initialization pattern for connecting to the remote browser context on Browserbase. That might look like:
# • Using Playwright’s remote connect methods, such as async_playwright() alongside a browser_type.connect(ws_endpoint) if you have a local WebSocket or CDP endpoint from Browserbase.
# • Managing the “session_id” as a key to tie into the remote browser in your NextJS server so the Python layer and NextJS share the same context.

# for connecting to remote browser, you can use the following code (but in typescript)


# async function getBrowser(
#   apiKey: string | undefined,
#   projectId: string | undefined,
#   env: "LOCAL" | "BROWSERBASE" = "LOCAL",
#   headless: boolean = false,
#   logger: (message: LogLine) => void,
#   browserbaseSessionCreateParams?: Browserbase.Sessions.SessionCreateParams,
#   browserbaseSessionID?: string,
# ): Promise<BrowserResult> {
#   if (env === "BROWSERBASE") {
#     if (!apiKey) {
#       logger({
#         category: "init",
#         message:
#           "BROWSERBASE_API_KEY is required to use BROWSERBASE env. Defaulting to LOCAL.",
#         level: 0,
#       });
#       env = "LOCAL";
#     }
#     if (!projectId) {
#       logger({
#         category: "init",
#         message:
#           "BROWSERBASE_PROJECT_ID is required for some Browserbase features that may not work without it.",
#         level: 1,
#       });
#     }
#   }

#   if (env === "BROWSERBASE") {
#     if (!apiKey) {
#       throw new Error("BROWSERBASE_API_KEY is required.");
#     }

#     let debugUrl: string | undefined = undefined;
#     let sessionUrl: string | undefined = undefined;
#     let sessionId: string;
#     let connectUrl: string;

#     const browserbase = new Browserbase({
#       apiKey,
#     });

#     if (browserbaseSessionID) {
#       // Validate the session status
#       try {
#         const sessionStatus =
#           await browserbase.sessions.retrieve(browserbaseSessionID);

#         if (sessionStatus.status !== "RUNNING") {
#           throw new Error(
#             `Session ${browserbaseSessionID} is not running (status: ${sessionStatus.status})`,
#           );
#         }

#         sessionId = browserbaseSessionID;
#         const browserbaseDomain =
#           BROWSERBASE_REGION_DOMAIN[sessionStatus.region] ||
#           "wss://connect.browserbase.com";
#         connectUrl = `${browserbaseDomain}?apiKey=${apiKey}&sessionId=${sessionId}`;

#         logger({
#           category: "init",
#           message: "resuming existing browserbase session...",
#           level: 1,
#           auxiliary: {
#             sessionId: {
#               value: sessionId,
#               type: "string",
#             },
#           },
#         });
#       } catch (error) {
#         logger({
#           category: "init",
#           message: "failed to resume session",
#           level: 1,
#           auxiliary: {
#             error: {
#               value: error.message,
#               type: "string",
#             },
#             trace: {
#               value: error.stack,
#               type: "string",
#             },
#           },
#         });
#         throw error;
#       }
#     } else {
#       // Create new session (existing code)
#       logger({
#         category: "init",
#         message: "creating new browserbase session...",
#         level: 0,
#       });

#       if (!projectId) {
#         throw new Error(
#           "BROWSERBASE_PROJECT_ID is required for new Browserbase sessions.",
#         );
#       }

#       const session = await browserbase.sessions.create({
#         projectId,
#         ...browserbaseSessionCreateParams,
#       });

#       sessionId = session.id;
#       connectUrl = session.connectUrl;
#       logger({
#         category: "init",
#         message: "created new browserbase session",
#         level: 1,
#         auxiliary: {
#           sessionId: {
#             value: sessionId,
#             type: "string",
#           },
#         },
#       });
#     }

#     const browser = await chromium.connectOverCDP(connectUrl);
#     const { debuggerUrl } = await browserbase.sessions.debug(sessionId);

#     debugUrl = debuggerUrl;
#     sessionUrl = `https://www.browserbase.com/sessions/${sessionId}`;

#     logger({
#       category: "init",
#       message: browserbaseSessionID
#         ? "browserbase session resumed"
#         : "browserbase session started",
#       level: 0,
#       auxiliary: {
#         sessionUrl: {
#           value: sessionUrl,
#           type: "string",
#         },
#         debugUrl: {
#           value: debugUrl,
#           type: "string",
#         },
#         sessionId: {
#           value: sessionId,
#           type: "string",
#         },
#       },
#     });

#     const context = browser.contexts()[0];

#     return { browser, context, debugUrl, sessionUrl, sessionId, env };

# 3. StagehandPage Implementation Details
# Here’s an example sketch for StagehandPage:
# • It has a private _page attribute referencing the actual playwright.async_api.Page.
# • It implements standard “browser control” methods by directly calling _page (e.g., _page.goto(url)).
# • If a user calls act/extract/observe, it calls the existing Stagehand Python client _execute(...) function to proxy the request to NextJS (like your original client.py does today).
# # Example snippet (pseudocode):

# import playwright.async_api as pw

# class StagehandPage:
#     def __init__(self, playwright_page: pw.Page, stagehand_client: "Stagehand"):
#         self._page = playwright_page
#         self._stagehand = stagehand_client

#     async def goto(self, url: str, **kwargs):
#         return await self._page.goto(url, **kwargs)

#     async def wait_for_selector(self, selector: str, **kwargs):
#         return await self._page.wait_for_selector(selector, **kwargs)

#     # Proxy methods:
#     async def act(self, action: str):
#         # Proxy to NextJS server via the stagehand_client
#         return await self._stagehand._execute("act", [{"action": action}])

#     async def observe(self, options=None):
#         # Proxy to NextJS server
#         return await self._stagehand._execute("observe", [options or {}])

#     async def extract(self, instruction, schema, **kwargs):
#         # Proxy to NextJS server
#         return await self._stagehand._execute("extract", [{"instruction": instruction, ...}])

# This class can either:
# Subclass pw.Page directly (though that can be tricky with Python’s dynamic nature), or
# Forward all non-“AI” methods to self._page via __getattr__.

# # For example, an approach using __getattr__:
# class StagehandPage:
#     def __init__(self, playwright_page, stagehand):
#         self._page = playwright_page
#         self._stagehand = stagehand

#     def __getattr__(self, item):
#         # If the attr is one of your AI methods, handle specially
#         if item in ["act", "observe", "extract"]:
#             # Return a bound method that calls stagehand._execute
#             return getattr(self, item)

#         # Otherwise forward to the raw Playwright page
#         return getattr(self._page, item)

# This way a user can run:
# await stagehand.page.wait_for_selector(".grid-container", timeout=10000)
# await stagehand.page.click("#submit-button")

# and it’s pure Playwright. But calls like await stagehand.page.act("...") are forwarded to your _execute method.
# . Managing the Remote Browser Context
# Connect to Browserbase:
# If Browserbase provides a WebSocket/CDP endpoint for the remote browser, call browser = await playwright.chromium.connect_over_cdp(remote_endpoint) or a similar method. Then fetch the relevant context/page.
# Alternatively, if you must spin up a local browser and the NextJS side does the same, that’s more complicated. Generally, you want them to share the same underlying browser session.
# Tie in the session_id to ensure both the NextJS server and Python are operating on the same remote instance. That might happen automatically if you connect to an endpoint that’s pinned to the session, or you might have to pass the session ID as part of the browser’s connect arguments.
# Once connected, create or retrieve the page object:
#    context = await browser.new_context()  # or get the existing context
#    playwright_page = await context.new_page()
#    self.page = StagehandPage(playwright_page, self)
# Or if you’re reusing an existing context from the NextJS session, you might do context.pages[0] to retrieve the page.
import asyncio
from typing import Optional, Dict, Any, Union
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from pydantic import BaseModel

class StagehandPage:
    """Wrapper around Playwright Page that integrates with Stagehand server"""
    
    def __init__(self, page: Page, stagehand_client):
        self.page = page
        self._stagehand = stagehand_client
        
    async def goto(self, url: str, **kwargs):
        """Navigate to URL using Playwright directly"""
        return await self.page.goto(url, **kwargs)

    # add server side navigate
    async def navigate(self, url: str, **kwargs):
        """Navigate to URL using Stagehand server"""
        return await self._stagehand._execute("goto", [url])
    
    async def act(self, action: str):
        """Execute AI action via Stagehand server"""
        return await self._stagehand._execute("act", [{"action": action}])
        
    async def observe(self, options: Optional[Dict[str, Any]] = None):
        """Make AI observation via Stagehand server"""
        return await self._stagehand._execute("observe", [options or {}])
        
    async def extract(self, instruction: str, schema: Union[Dict[str, Any], type(BaseModel)], **kwargs):
        """Extract data using AI via Stagehand server"""
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            schema_definition = schema.schema()
        elif isinstance(schema, dict):
            schema_definition = schema
        else:
            raise ValueError("schema must be a dict or Pydantic model class")
            
        args = {"instruction": instruction, "schemaDefinition": schema_definition}
        args.update(kwargs)
        return await self._stagehand._execute("extract", [args])

    # Forward other Page methods to underlying Playwright page
    def __getattr__(self, name):
        return getattr(self.page, name)

# # TODO - we may not need the below.
# class PlaywrightProxy:
#     """Manages Playwright browser connection to Browserbase"""
    
#     def __init__(self, api_key: str, project_id: str):
#         self.api_key = api_key
#         self.project_id = project_id
#         self.browser: Optional[Browser] = None
#         self.context: Optional[BrowserContext] = None
        
#     async def connect(self, connect_url: str):
#         """Connect to remote Browserbase browser"""
#         playwright = await async_playwright().start()
#         self.browser = await playwright.chromium.connect_over_cdp(connect_url)
#         self.context = self.browser.contexts[0]
#         return self.context
        
#     async def new_page(self, stagehand_client) -> StagehandPage:
#         """Create new page wrapped in StagehandPage"""
#         if not self.context:
#             raise RuntimeError("Must connect() before creating pages")
#         page = await self.context.new_page()
#         return StagehandPage(page, stagehand_client)
        
#     async def close(self):
#         """Clean up browser resources"""
#         if self.browser:
#             await self.browser.close()
