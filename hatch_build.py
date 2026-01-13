from __future__ import annotations

import os
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def _infer_platform_tag() -> str:
    from packaging.tags import sys_tags

    # Linux tag is after many/musl; skip those to get the generic platform tag.
    tag = next(iter(t for t in sys_tags() if "manylinux" not in t.platform and "musllinux" not in t.platform))
    return tag.platform


def _has_embedded_sea_binaries() -> bool:
    sea_dir = Path(__file__).resolve().parent / "src" / "stagehand" / "_sea"
    if not sea_dir.exists():
        return False

    for path in sea_dir.iterdir():
        if not path.is_file():
            continue
        if path.name in {".keep"}:
            continue
        if path.name.startswith("."):
            continue
        return True

    return False


class CustomBuildHook(BuildHookInterface):
    def initialize(self, _version: str, build_data: dict) -> None:
        if not _has_embedded_sea_binaries():
            return

        # We are bundling a platform-specific executable, so this must not be a
        # "pure python" wheel.
        build_data["pure_python"] = False

        # CI sets this so we get deterministic wheel tags that match the SEA
        # artifact we're embedding (e.g. "py3-none-macosx_11_0_arm64").
        wheel_tag = os.environ.get("STAGEHAND_WHEEL_TAG", "").strip()
        if wheel_tag:
            if wheel_tag.count("-") != 2:
                raise ValueError(
                    "Invalid STAGEHAND_WHEEL_TAG. Expected a full wheel tag like 'py3-none-macosx_11_0_arm64'."
                )
            build_data["tag"] = wheel_tag
            build_data["infer_tag"] = False
        else:
            # For local builds, infer just the platform portion so the wheel
            # remains Python-version agnostic (our embedded server binary is not
            # tied to a specific Python ABI).
            build_data["tag"] = f"py3-none-{_infer_platform_tag()}"
            build_data["infer_tag"] = False
