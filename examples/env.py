from __future__ import annotations

import os
from pathlib import Path

REQUIRED_KEYS = {
    "MODEL_API_KEY",
    "BROWSERBASE_API_KEY",
}


def _find_env_path() -> Path | None:
    current = Path.cwd()
    while True:
        candidate = current / "examples" / ".env"
        if candidate.exists():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def load_example_env() -> None:
    env_path = _find_env_path()
    if not env_path:
        raise RuntimeError("Missing examples/.env (expected in repo examples/ directory).")

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key] = value

    missing = [key for key in sorted(REQUIRED_KEYS) if not os.environ.get(key)]
    if missing:
        raise RuntimeError(
            "Missing required env vars: "
            + ", ".join(missing)
            + " (from examples/.env)"
        )

    # Use the repo-local SEA binary when available (avoid global installs).
    sea_binary = env_path.parent.parent / "bin" / "sea" / "stagehand-darwin-arm64"
    if sea_binary.exists():
        os.environ.setdefault("STAGEHAND_SEA_BINARY", str(sea_binary))
