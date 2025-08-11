import asyncio
import time
from typing import Optional, Union

from playwright.async_api import CDPSession, Page
from pydantic import BaseModel

from stagehand.handlers.act_handler import ActHandler
from stagehand.handlers.extract_handler import ExtractHandler
from stagehand.handlers.observe_handler import ObserveHandler

from .schemas import (
    DEFAULT_EXTRACT_SCHEMA,
    ActOptions,
    ActResult,
    ExtractOptions,
    ExtractResult,
    ObserveOptions,
    ObserveResult,
)
from .types import DefaultExtractSchema, EmptyExtractSchema

_INJECTION_SCRIPT = None


class StagehandPage:
    """Wrapper around Playwright Page that integrates with Stagehand server"""

    _cdp_client: Optional[CDPSession] = None

    def __init__(self, page: Page, stagehand_client, context=None):
        """
        Initialize a StagehandPage instance.

        Args:
            page (Page): The underlying Playwright page.
            stagehand_client: The client used to interface with the Stagehand server.
            context: The StagehandContext instance (optional).
        """
        self._page = page
        self._stagehand = stagehand_client
        self._context = context
        self._frame_id = None

    @property
    def frame_id(self) -> Optional[str]:
        """Get the current root frame ID."""
        return self._frame_id

    def update_root_frame_id(self, new_id: str):
        """Update the root frame ID."""
        self._frame_id = new_id
        self._stagehand.logger.debug(f"Updated frame ID to {new_id}", category="page")

    # TODO try catch here
    async def ensure_injection(self):
        """Ensure custom injection scripts are present on the page using domScripts.js."""
        exists_before = await self._page.evaluate(
            "typeof window.getScrollableElementXpaths === 'function'"
        )
        if not exists_before:
            global _INJECTION_SCRIPT
            if _INJECTION_SCRIPT is None:
                import os

                script_path = os.path.join(os.path.dirname(__file__), "domScripts.js")
                try:
                    with open(script_path) as f:
                        _INJECTION_SCRIPT = f.read()
                except Exception as e:
                    self._stagehand.logger.error(f"Error reading domScripts.js: {e}")
                    _INJECTION_SCRIPT = "/* fallback injection script */"
            # Inject the script into the current page context
            await self._page.evaluate(_INJECTION_SCRIPT)
            # Ensure that the script is injected on future navigations
            await self._page.add_init_script(_INJECTION_SCRIPT)

    async def goto(
        self,
        url: str,
        *,
        referer: Optional[str] = None,
        timeout: Optional[int] = None,
        wait_until: Optional[str] = None,
    ):
        """
        Navigate to URL using the Stagehand server.

        Args:
            url (str): The URL to navigate to.
            referer (Optional[str]): Optional referer URL.
            timeout (Optional[int]): Optional navigation timeout in milliseconds.
            wait_until (Optional[str]): Optional wait condition; one of ('load', 'domcontentloaded', 'networkidle', 'commit').

        Returns:
            The result from the Stagehand server's navigation execution.
        """
        if not self._stagehand.use_api:
            await self._page.goto(
                url, referer=referer, timeout=timeout, wait_until=wait_until
            )
            return
        options = {}
        if referer is not None:
            options["referer"] = referer
        if timeout is not None:
            options["timeout"] = timeout
        if wait_until is not None:
            options["wait_until"] = wait_until
            options["waitUntil"] = wait_until

        payload = {"url": url}
        if options:
            payload["options"] = options

        # Add frame ID if available
        if self._frame_id:
            payload["frameId"] = self._frame_id

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("navigate", payload)
        return result

    async def act(
        self, action_or_result: Union[str, ObserveResult, dict], **kwargs
    ) -> ActResult:
        """
        Execute an AI action or a pre-observed action via the Stagehand server.

        Args:
            action_or_result (Union[str, ObserveResult]):
                - A string with the action command to be executed by the AI.
                - An ObserveResult containing selector and method for direct execution.
            **kwargs: Additional options corresponding to fields in ActOptions
                      (e.g., model_name, timeout_ms). These are ignored if
                      action_or_result is an ObserveResult.

        Returns:
            ActResult: The result from the Stagehand server's action execution.
        """
        await self.ensure_injection()

        payload: dict
        # Check if it's an ObserveResult for direct execution
        if isinstance(action_or_result, ObserveResult):
            if kwargs:
                self._stagehand.logger.debug(
                    "Additional keyword arguments provided to 'act' when using an ObserveResult are ignored."
                )
            payload = action_or_result.model_dump(exclude_none=True, by_alias=True)
        # If it's a string, construct ActOptions using the string and kwargs
        elif isinstance(action_or_result, str):
            options = ActOptions(action=action_or_result, **kwargs)
            payload = options.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(action_or_result, ActOptions):
            payload = action_or_result.model_dump(exclude_none=True, by_alias=True)
        elif isinstance(action_or_result, dict):
            if "description" in action_or_result:
                payload = ObserveResult(**action_or_result).model_dump(
                    exclude_none=True, by_alias=True
                )
            else:
                payload = ActOptions(**action_or_result).model_dump(
                    exclude_none=True, by_alias=True
                )
        else:
            raise TypeError(
                "Invalid arguments for 'act'. Expected str, ObserveResult, or ActOptions."
            )

        # TODO: Temporary until we move api based logic to client
        if not self._stagehand.use_api:
            # TODO: revisit passing user_provided_instructions
            if not hasattr(self, "_observe_handler"):
                # TODO: revisit handlers initialization on page creation
                self._observe_handler = ObserveHandler(self, self._stagehand, "")
            if not hasattr(self, "_act_handler"):
                self._act_handler = ActHandler(
                    self, self._stagehand, "", self._stagehand.self_heal
                )
            self._stagehand.logger.debug("act", category="act", auxiliary=payload)
            if payload.get("iframes"):
                raise ValueError(
                    "iframes is not yet supported without API (to enable make sure you set env=BROWSERBASE and use_api=true)"
                )
            result = await self._act_handler.act(payload)
            return result

        # Add frame ID if available
        if self._frame_id:
            payload["frameId"] = self._frame_id

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("act", payload)
        if isinstance(result, dict):
            return ActResult(**result)
        return result

    async def observe(
        self,
        options_or_instruction: Union[str, ObserveOptions, None] = None,
        **kwargs,
    ) -> list[ObserveResult]:
        """
        Make an AI observation via the Stagehand server.

        Args:
            options_or_instruction (Union[str, ObserveOptions, None]):
                - A string with the observation instruction for the AI.
                - An ObserveOptions object.
                - None to use default options.
            **kwargs: Additional options corresponding to fields in ObserveOptions
                      (e.g., model_name, only_visible, return_action).

        Returns:
            list[ObserveResult]: A list of observation results from the Stagehand server.
        """
        await self.ensure_injection()

        options_dict = {}

        if isinstance(options_or_instruction, ObserveOptions):
            # Already a pydantic object – take it as is.
            options_obj = options_or_instruction
        else:
            if isinstance(options_or_instruction, str):
                options_dict["instruction"] = options_or_instruction

            # Merge any explicit keyword arguments (highest priority)
            options_dict.update(kwargs)

            if not options_dict:
                raise TypeError("No instruction provided for observe.")

            try:
                options_obj = ObserveOptions(**options_dict)
            except Exception as e:
                raise TypeError(f"Invalid observe options: {e}") from e

        # Serialized payload for server / local handlers
        payload = options_obj.model_dump(exclude_none=True, by_alias=True)

        # If in LOCAL mode, use local implementation
        if not self._stagehand.use_api:
            self._stagehand.logger.debug(
                "observe", category="observe", auxiliary=payload
            )
            # If we don't have an observe handler yet, create one
            # TODO: revisit passing user_provided_instructions
            if not hasattr(self, "_observe_handler"):
                self._observe_handler = ObserveHandler(self, self._stagehand, "")

            # Call local observe implementation
            result = await self._observe_handler.observe(
                options_obj,
                from_act=False,
            )

            return result

        # Add frame ID if available
        if self._frame_id:
            payload["frameId"] = self._frame_id

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result = await self._stagehand._execute("observe", payload)

        # Convert raw result to list of ObserveResult models
        if isinstance(result, list):
            return [ObserveResult(**item) for item in result]
        elif isinstance(result, dict):
            # If single dict, wrap in list (should ideally be list from server)
            return [ObserveResult(**result)]
        # Handle unexpected return types
        self._stagehand.logger.info(
            f"Unexpected result type from observe: {type(result)}"
        )
        return []

    async def extract(
        self,
        options_or_instruction: Union[str, ExtractOptions, None] = None,
        *,
        schema: Optional[type[BaseModel]] = None,
        **kwargs,
    ) -> ExtractResult:
        """
        Extract data using AI via the Stagehand server.

        Args:
            options_or_instruction (Union[str, ExtractOptions, None]):
                - A string with the instruction specifying what data to extract.
                - An ExtractOptions object.
                - None to extract the entire page content.
            schema (Optional[Union[type[BaseModel], None]]):
                A Pydantic model class that defines the structure
                of the expected extracted data.
            **kwargs: Additional options corresponding to fields in ExtractOptions
                      (e.g., model_name, use_text_extract, selector, dom_settle_timeout_ms).

        Returns:
            ExtractResult: Depending on the type of the schema provided, the result will be a Pydantic model or JSON representation of the extracted data.
        """
        await self.ensure_injection()

        options_dict = {}

        if isinstance(options_or_instruction, ExtractOptions):
            options_obj = options_or_instruction
        else:
            if isinstance(options_or_instruction, str):
                options_dict["instruction"] = options_or_instruction

            # Merge keyword overrides (highest priority)
            options_dict.update(kwargs)

            # Ensure schema_definition is only set once (explicit arg precedence)
            if schema is not None:
                options_dict["schema_definition"] = schema

            if options_dict:
                try:
                    options_obj = ExtractOptions(**options_dict)
                except Exception as e:
                    raise TypeError(f"Invalid extract options: {e}") from e
            else:
                # No options_dict provided and no ExtractOptions given: full page extract.
                options_obj = None

        # If we started with an existing ExtractOptions instance and the caller
        # explicitly provided a schema, override it
        if (
            schema is not None
            and isinstance(options_obj, ExtractOptions)
            and options_obj.schema_definition != schema
        ):
            options_obj = options_obj.model_copy(update={"schema_definition": schema})

        if options_obj is None:
            payload = {}
        else:
            payload = options_obj.model_dump(exclude_none=True, by_alias=True)

        # Determine the schema to pass to the handler
        schema_to_validate_with = None
        if (
            options_obj is not None
            and options_obj.schema_definition is not None
            and options_obj.schema_definition != DEFAULT_EXTRACT_SCHEMA
        ):
            if isinstance(options_obj.schema_definition, type) and issubclass(
                options_obj.schema_definition, BaseModel
            ):
                # Case 1: Pydantic model class
                schema_to_validate_with = options_obj.schema_definition
            elif isinstance(options_obj.schema_definition, dict):
                # TODO: revisit this case to pass the json_schema since litellm has a bug when passing it directly
                # Case 2: Dictionary
                # Assume it's a direct JSON schema dictionary
                schema_to_validate_with = options_obj.schema_definition
        else:
            schema_to_validate_with = DefaultExtractSchema

        if not self._stagehand.use_api:
            # If we don't have an extract handler yet, create one
            if not hasattr(self, "_extract_handler"):
                self._extract_handler = ExtractHandler(
                    self, self._stagehand, self._stagehand.system_prompt
                )

            # Allow for no options to extract the entire page
            if options_obj is None:
                # Call local extract implementation with no options
                result = await self._extract_handler.extract(
                    None,
                    None,  # Explicitly pass None for schema if no options
                )
                return result

            # Call local extract implementation
            result = await self._extract_handler.extract(
                options_obj,
                schema_to_validate_with,
            )
            return result.data

        # Use API
        # Add frame ID if available
        if self._frame_id:
            payload["frameId"] = self._frame_id

        lock = self._stagehand._get_lock_for_session()
        async with lock:
            result_dict = await self._stagehand._execute("extract", payload)

        if isinstance(result_dict, dict):
            # Pydantic will validate against known fields + allow extras if configured
            processed_data_payload = result_dict
            if schema_to_validate_with and isinstance(processed_data_payload, dict):
                try:
                    # For extract with no params
                    if not options_obj:
                        validated_model = EmptyExtractSchema.model_validate(
                            processed_data_payload
                        )
                        processed_data_payload = validated_model
                    else:
                        validated_model = schema_to_validate_with.model_validate(
                            processed_data_payload
                        )
                        processed_data_payload = validated_model
                except Exception as e:
                    self._stagehand.logger.error(
                        f"Failed to validate extracted data against schema {schema_to_validate_with.__name__}: {e}. Keeping raw data dict in .data field."
                    )
            return ExtractResult(data=processed_data_payload).data
        # Handle unexpected return types
        self._stagehand.logger.info(
            f"Unexpected result type from extract: {type(result_dict)}"
        )
        return result_dict

    # Method to get or initialize the persistent CDP client
    async def get_cdp_client(self) -> CDPSession:
        """Gets the persistent CDP client, initializing it if necessary."""
        # Check only if the client is None, rely on send_cdp's exception handling for disconnections
        if self._cdp_client is None:
            try:
                self._stagehand.logger.debug("Creating new persistent CDP session.")
                self._cdp_client = await self._page.context.new_cdp_session(self._page)
            except Exception as e:
                self._stagehand.logger.error(f"Failed to create CDP session: {e}")
                raise  # Re-raise the exception
        return self._cdp_client

    # Modified send_cdp to use the persistent client
    async def send_cdp(self, method: str, params: Optional[dict] = None) -> dict:
        """Sends a CDP command using the persistent session."""
        client = await self.get_cdp_client()
        try:
            # Type assertion might be needed depending on playwright version/typing
            result = await client.send(method, params or {})
        except Exception as e:
            self._stagehand.logger.debug(
                f"CDP command '{method}' failed: {e}. Attempting to reconnect..."
            )
            # Handle specific errors if needed (e.g., session closed)
            if "Target closed" in str(e) or "Session closed" in str(e):
                # Attempt to reset the client if the session closed unexpectedly
                self._cdp_client = None
                client = await self.get_cdp_client()  # Try creating a new one
                result = await client.send(method, params or {})
            else:
                raise  # Re-raise other errors
        return result

    # Method to enable a specific CDP domain
    async def enable_cdp_domain(self, domain: str):
        """Enables a specific CDP domain."""
        try:
            await self.send_cdp(f"{domain}.enable")
        except Exception as e:
            self._stagehand.logger.debug(f"Failed to enable CDP domain '{domain}': {e}")

    # Method to disable a specific CDP domain
    async def disable_cdp_domain(self, domain: str):
        """Disables a specific CDP domain."""
        try:
            await self.send_cdp(f"{domain}.disable")
        except Exception:
            # Ignore errors during disable, often happens during cleanup
            pass

    # Method to detach the persistent CDP client
    async def detach_cdp_client(self):
        """Detaches the persistent CDP client if it exists."""
        if self._cdp_client and self._cdp_client.is_connected():
            try:
                await self._cdp_client.detach()
                self._cdp_client = None
            except Exception as e:
                self._stagehand.logger.debug(f"Error detaching CDP client: {e}")
        self._cdp_client = None

    async def _wait_for_settled_dom(self, timeout_ms: int = None):
        """
        Wait for the DOM to settle (stop changing) before proceeding.

        **Definition of "settled"**
          • No in-flight network requests (except WebSocket / Server-Sent-Events).
          • That idle state lasts for at least **500 ms** (the "quiet-window").

        **How it works**
          1. Subscribes to CDP Network and Page events for the main target and all
             out-of-process iframes (via `Target.setAutoAttach { flatten:true }`).
          2. Every time `Network.requestWillBeSent` fires, the request ID is added
             to an **`inflight`** set.
          3. When the request finishes—`loadingFinished`, `loadingFailed`,
             `requestServedFromCache`, or a *data:* response—the request ID is
             removed.
          4. *Document* requests are also mapped **frameId → requestId**; when
             `Page.frameStoppedLoading` fires the corresponding Document request is
             removed immediately (covers iframes whose network events never close).
          5. A **stalled-request sweep timer** runs every 500 ms. If a *Document*
             request has been open for ≥ 2 s it is forcibly removed; this prevents
             ad/analytics iframes from blocking the wait forever.
          6. When `inflight` becomes empty the helper starts a 500 ms timer.
             If no new request appears before the timer fires, the promise
             resolves → **DOM is considered settled**.
          7. A global guard (`timeoutMs` or `stagehand.domSettleTimeoutMs`,
             default ≈ 30 s) ensures we always resolve; if it fires we log how many
             requests were still outstanding.

        Args:
            timeout_ms (int, optional): Maximum time to wait in milliseconds.
                If None, uses the stagehand client's dom_settle_timeout_ms.
        """

        timeout = timeout_ms or getattr(self._stagehand, "dom_settle_timeout_ms", 30000)
        client = await self.get_cdp_client()

        # Check if document exists
        try:
            await self._page.title()
        except Exception:
            await self._page.wait_for_load_state("domcontentloaded")

        # Enable CDP domains
        await client.send("Network.enable")
        await client.send("Page.enable")
        await client.send(
            "Target.setAutoAttach",
            {
                "autoAttach": True,
                "waitForDebuggerOnStart": False,
                "flatten": True,
                "filter": [
                    {"type": "worker", "exclude": True},
                    {"type": "shared_worker", "exclude": True},
                ],
            },
        )

        # Set up tracking structures
        inflight = set()  # Set of request IDs
        meta = {}  # Dict of request ID -> {"url": str, "start": float}
        doc_by_frame = {}  # Dict of frame ID -> request ID

        # Event tracking
        quiet_timer = None
        stalled_request_sweep_task = None
        loop = asyncio.get_event_loop()
        done_event = asyncio.Event()

        def clear_quiet():
            nonlocal quiet_timer
            if quiet_timer:
                quiet_timer.cancel()
                quiet_timer = None

        def resolve_done():
            """Cleanup and mark as done"""
            clear_quiet()
            if stalled_request_sweep_task and not stalled_request_sweep_task.done():
                stalled_request_sweep_task.cancel()
            done_event.set()

        def maybe_quiet():
            """Start quiet timer if no requests are in flight"""
            nonlocal quiet_timer
            if len(inflight) == 0 and not quiet_timer:
                quiet_timer = loop.call_later(0.5, resolve_done)

        def finish_req(request_id: str):
            """Mark a request as finished"""
            if request_id not in inflight:
                return
            inflight.remove(request_id)
            meta.pop(request_id, None)
            # Remove from frame mapping
            for fid, rid in list(doc_by_frame.items()):
                if rid == request_id:
                    doc_by_frame.pop(fid)
            clear_quiet()
            maybe_quiet()

        # Event handlers
        def on_request(params):
            """Handle Network.requestWillBeSent"""
            if params.get("type") in ["WebSocket", "EventSource"]:
                return

            request_id = params["requestId"]
            inflight.add(request_id)
            meta[request_id] = {"url": params["request"]["url"], "start": time.time()}

            if params.get("type") == "Document" and params.get("frameId"):
                doc_by_frame[params["frameId"]] = request_id

            clear_quiet()

        def on_finish(params):
            """Handle Network.loadingFinished"""
            finish_req(params["requestId"])

        def on_failed(params):
            """Handle Network.loadingFailed"""
            finish_req(params["requestId"])

        def on_cached(params):
            """Handle Network.requestServedFromCache"""
            finish_req(params["requestId"])

        def on_data_url(params):
            """Handle Network.responseReceived for data: URLs"""
            if params.get("response", {}).get("url", "").startswith("data:"):
                finish_req(params["requestId"])

        def on_frame_stop(params):
            """Handle Page.frameStoppedLoading"""
            frame_id = params["frameId"]
            if frame_id in doc_by_frame:
                finish_req(doc_by_frame[frame_id])

        # Register event handlers
        client.on("Network.requestWillBeSent", on_request)
        client.on("Network.loadingFinished", on_finish)
        client.on("Network.loadingFailed", on_failed)
        client.on("Network.requestServedFromCache", on_cached)
        client.on("Network.responseReceived", on_data_url)
        client.on("Page.frameStoppedLoading", on_frame_stop)

        async def sweep_stalled_requests():
            """Remove stalled document requests after 2 seconds"""
            while not done_event.is_set():
                await asyncio.sleep(0.5)
                now = time.time()
                for request_id, request_meta in list(meta.items()):
                    if now - request_meta["start"] > 2.0:
                        inflight.discard(request_id)
                        meta.pop(request_id, None)
                        self._stagehand.logger.debug(
                            "⏳ forcing completion of stalled iframe document",
                            auxiliary={"url": request_meta["url"][:120]},
                        )
                maybe_quiet()

        # Start stalled request sweeper
        stalled_request_sweep_task = asyncio.create_task(sweep_stalled_requests())

        # Set up timeout guard
        async def timeout_guard():
            await asyncio.sleep(timeout / 1000)
            if not done_event.is_set():
                if len(inflight) > 0:
                    self._stagehand.logger.debug(
                        "⚠️ DOM-settle timeout reached – network requests still pending",
                        auxiliary={"count": len(inflight)},
                    )
                resolve_done()

        timeout_task = asyncio.create_task(timeout_guard())

        # Initial check
        maybe_quiet()

        try:
            # Wait for completion
            await done_event.wait()
        finally:
            # Cleanup
            client.remove_listener("Network.requestWillBeSent", on_request)
            client.remove_listener("Network.loadingFinished", on_finish)
            client.remove_listener("Network.loadingFailed", on_failed)
            client.remove_listener("Network.requestServedFromCache", on_cached)
            client.remove_listener("Network.responseReceived", on_data_url)
            client.remove_listener("Page.frameStoppedLoading", on_frame_stop)

            if quiet_timer:
                quiet_timer.cancel()
            if stalled_request_sweep_task and not stalled_request_sweep_task.done():
                stalled_request_sweep_task.cancel()
                try:
                    await stalled_request_sweep_task
                except asyncio.CancelledError:
                    pass
            if timeout_task and not timeout_task.done():
                timeout_task.cancel()
                try:
                    await timeout_task
                except asyncio.CancelledError:
                    pass

    # Forward other Page methods to underlying Playwright page
    def __getattr__(self, name):
        """
        Forward attribute lookups to the underlying Playwright page.

        Args:
            name (str): Name of the attribute to access.

        Returns:
            The attribute from the underlying Playwright page.
        """
        # self._stagehand.logger.debug(f"Getting attribute: {name}")
        return getattr(self._page, name)
