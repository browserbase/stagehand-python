"""
Example: use Google Vertex AI model auth with the Stagehand Python SDK.

This runs the same model-backed flow against both:
- server="remote" (hosted Stagehand API + Browserbase browser)
- server="local" (local Stagehand server + local browser)

Required environment variables:
- BROWSERBASE_API_KEY
- GOOGLE_APPLICATION_CREDENTIALS: path to a service account JSON file
  OR VERTEX_SERVICE_ACCOUNT_JSON: raw service account JSON

Optional environment variables:
- VERTEX_PROJECT: Google Cloud project ID. Defaults to credentials.project_id.
- VERTEX_LOCATION: Google Cloud location. Defaults to us-central1.
- VERTEX_MODEL: Vertex model name. Defaults to vertex/gemini-2.5-flash.
- STAGEHAND_BOOTSTRAP_MODEL: session start model. Defaults to openai/gpt-4.1-mini.

The service account JSON is read by this script and sent inline as credentials.
Do not pass key file paths to the Stagehand API server.
"""

from __future__ import annotations

import os
import sys
import json
from typing import Any, Literal, cast
from pathlib import Path

from stagehand import Stagehand
from stagehand.types.session_extract_params import (
    OptionsModelVertexModelConfigObject as VertexModelConfig,
    OptionsModelVertexModelConfigObjectAuthCredentials as VertexCredentials,
)


def load_example_env() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def load_vertex_credentials() -> VertexCredentials:
    inline_json = os.environ.get("VERTEX_SERVICE_ACCOUNT_JSON")
    if inline_json:
        credentials = json.loads(inline_json)
    else:
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            sys.exit(
                "Set GOOGLE_APPLICATION_CREDENTIALS to a service account JSON file "
                "or VERTEX_SERVICE_ACCOUNT_JSON to raw service account JSON."
            )
        credentials = json.loads(Path(credentials_path).expanduser().read_text())

    if not isinstance(credentials, dict):
        sys.exit("Vertex credentials must be a JSON object.")

    missing = [
        key for key in ("client_email", "private_key") if not credentials.get(key)
    ]
    if missing:
        sys.exit("Vertex credentials are missing: " + ", ".join(missing))

    return cast(VertexCredentials, credentials)


def build_vertex_model_config() -> VertexModelConfig:
    credentials = load_vertex_credentials()
    project = os.environ.get("VERTEX_PROJECT") or credentials.get("project_id")
    if not project:
        sys.exit("Set VERTEX_PROJECT or include project_id in the credentials JSON.")

    location = os.environ.get("VERTEX_LOCATION", "us-central1")
    model_name = os.environ.get("VERTEX_MODEL", "vertex/gemini-2.5-flash")

    return {
        "provider": "vertex",
        "model_name": model_name,
        "auth": {
            "type": "googleServiceAccount",
            "credentials": credentials,
        },
        "provider_options": {
            "vertex": {
                "project": project,
                "location": location,
            }
        },
    }


def run_vertex_flow(
    server: Literal["remote", "local"], vertex_model: VertexModelConfig
) -> None:
    browserbase_api_key = os.environ.get("BROWSERBASE_API_KEY")
    if not browserbase_api_key:
        sys.exit("Set BROWSERBASE_API_KEY to run this example.")

    client_kwargs: dict[str, Any] = {
        "server": server,
        "browserbase_api_key": browserbase_api_key,
    }
    browser: dict[str, Any]

    if server == "local":
        client_kwargs["local_ready_timeout_s"] = 30.0
        browser = {
            "type": "local",
            "launchOptions": {
                "headless": True,
            },
        }
    else:
        browser = {"type": "browserbase"}

    bootstrap_model = os.environ.get("STAGEHAND_BOOTSTRAP_MODEL", "openai/gpt-4.1-mini")

    with Stagehand(**client_kwargs) as client:
        session = client.sessions.start(
            model_name=bootstrap_model,
            browser=browser,
        )

        try:
            session.navigate(url="https://example.com")

            observe_result = session.observe(
                instruction="Find the main heading on the page.",
                options={"model": vertex_model},
            )
            print(f"[{server}] observe:", observe_result)

            extract_result = session.extract(
                instruction="Extract the page title and main heading.",
                schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "heading": {"type": "string"},
                    },
                    "required": ["title", "heading"],
                    "additionalProperties": False,
                },
                options={"model": vertex_model},
            )
            print(f"[{server}] extract:", extract_result)

            execute_result = session.execute(
                agent_config={
                    "model": vertex_model,
                    "cua": False,
                },
                execute_options={
                    "instruction": "Summarize the current page in one sentence.",
                    "max_steps": 3,
                },
            )
            print(f"[{server}] execute:", execute_result)
        finally:
            session.end()


def main() -> None:
    load_example_env()
    vertex_model = build_vertex_model_config()
    run_vertex_flow("remote", vertex_model)
    run_vertex_flow("local", vertex_model)


if __name__ == "__main__":
    main()
