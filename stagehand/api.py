import json
from typing import Any

from .utils import convert_dict_keys_to_camel_case

__all__ = ["_create_session", "_execute"]


async def _create_session(self):
    """
    Create a new session by calling /sessions/start on the server.
    Depends on browserbase_api_key, browserbase_project_id, and model_api_key.
    """
    if not self.browserbase_api_key:
        raise ValueError("browserbase_api_key is required to create a session.")
    if not self.browserbase_project_id:
        raise ValueError("browserbase_project_id is required to create a session.")
    if not self.model_api_key:
        raise ValueError("model_api_key is required to create a session.")

    browserbase_session_create_params = (
        convert_dict_keys_to_camel_case(self.browserbase_session_create_params)
        if self.browserbase_session_create_params
        else None
    )

    payload = {
        "modelName": self.model_name,
        "verbose": 2 if self.verbose == 3 else self.verbose,
        "domSettleTimeoutMs": self.dom_settle_timeout_ms,
        "browserbaseSessionCreateParams": (
            browserbase_session_create_params
            if browserbase_session_create_params
            else {
                "browserSettings": {
                    "blockAds": True,
                    "viewport": {
                        "width": 1024,
                        "height": 768,
                    },
                },
            }
        ),
    }

    # Add the new parameters if they have values
    if hasattr(self, "self_heal") and self.self_heal is not None:
        payload["selfHeal"] = self.self_heal

    if (
        hasattr(self, "wait_for_captcha_solves")
        and self.wait_for_captcha_solves is not None
    ):
        payload["waitForCaptchaSolves"] = self.wait_for_captcha_solves

    if hasattr(self, "act_timeout_ms") and self.act_timeout_ms is not None:
        payload["actTimeoutMs"] = self.act_timeout_ms

    if hasattr(self, "system_prompt") and self.system_prompt:
        payload["systemPrompt"] = self.system_prompt

    if hasattr(self, "model_client_options") and self.model_client_options:
        payload["modelClientOptions"] = self.model_client_options

    headers = {
        "x-bb-api-key": self.browserbase_api_key,
        "x-bb-project-id": self.browserbase_project_id,
        "x-model-api-key": self.model_api_key,
        "Content-Type": "application/json",
        "x-language": "python",
    }

    # async with self._client:
    resp = await self._client.post(
        f"{self.api_url}/sessions/start",
        json=payload,
        headers=headers,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to create session: {resp.text}")
    data = resp.json()
    self.logger.debug(f"Session created: {data}")
    if not data.get("success") or "sessionId" not in data.get("data", {}):
        raise RuntimeError(f"Invalid response format: {resp.text}")

    self.session_id = data["data"]["sessionId"]


async def _execute(self, method: str, payload: dict[str, Any]) -> Any:
    """
    Internal helper to call /sessions/{session_id}/{method} with the given method and payload.
    Streams line-by-line, returning the 'result' from the final message (if any).
    """
    headers = {
        "x-bb-api-key": self.browserbase_api_key,
        "x-bb-project-id": self.browserbase_project_id,
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        # Always enable streaming for better log handling
        "x-stream-response": "true",
    }
    if self.model_api_key:
        headers["x-model-api-key"] = self.model_api_key

    # Convert snake_case keys to camelCase for the API
    modified_payload = convert_dict_keys_to_camel_case(payload)

    # async with self._client:
    try:
        # Always use streaming for consistent log handling
        async with self._client.stream(
            "POST",
            f"{self.api_url}/sessions/{self.session_id}/{method}",
            json=modified_payload,
            headers=headers,
        ) as response:
            if response.status_code != 200:
                error_text = await response.aread()
                error_message = error_text.decode("utf-8")
                self.logger.error(
                    f"[HTTP ERROR] Status {response.status_code}: {error_message}"
                )
                raise RuntimeError(
                    f"Request failed with status {response.status_code}: {error_message}"
                )
            result = None

            async for line in response.aiter_lines():
                # Skip empty lines
                if not line.strip():
                    continue

                try:
                    # Handle SSE-style messages that start with "data: "
                    if line.startswith("data: "):
                        line = line[len("data: ") :]

                    message = json.loads(line)
                    # Handle different message types
                    msg_type = message.get("type")

                    if msg_type == "system":
                        status = message.get("data", {}).get("status")
                        if status == "error":
                            error_msg = message.get("data", {}).get(
                                "error", "Unknown error"
                            )
                            self.logger.error(f"[ERROR] {error_msg}")
                            raise RuntimeError(f"Server returned error: {error_msg}")
                        elif status == "finished":
                            result = message.get("data", {}).get("result")
                    elif msg_type == "log":
                        # Process log message using _handle_log
                        await self._handle_log(message)
                    else:
                        # Log any other message types
                        self.logger.debug(f"[UNKNOWN] Message type: {msg_type}")
                except json.JSONDecodeError:
                    self.logger.error(f"Could not parse line as JSON: {line}")

            # Return the final result
            return result
    except Exception as e:
        self.logger.error(f"[EXCEPTION] {str(e)}")
        raise
