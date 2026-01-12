#!/usr/bin/env python3
"""
Download the stagehand-server binary for local development.

This script downloads the appropriate binary for your platform from GitHub releases
and places it in bin/sea/ for use during development and testing.

Usage:
    python scripts/download-binary.py [--version VERSION]

Examples:
    python scripts/download-binary.py
    python scripts/download-binary.py --version v3.2.0
"""
from __future__ import annotations

import sys
import os
import json
import argparse
import platform
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def get_platform_info() -> tuple[str, str]:
    """Determine platform and architecture."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        plat = "darwin"
    elif system == "windows":
        plat = "win32"
    else:
        plat = "linux"

    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    return plat, arch


def get_binary_filename(plat: str, arch: str) -> str:
    """Get the expected binary filename for this platform."""
    name = f"stagehand-server-{plat}-{arch}"
    return name + (".exe" if plat == "win32" else "")


def get_local_filename(plat: str, arch: str) -> str:
    """Get the local filename (what the code expects to find)."""
    name = f"stagehand-{plat}-{arch}"
    return name + (".exe" if plat == "win32" else "")

def _parse_server_tag(tag: str) -> tuple[int, int, int] | None:
    # Expected: stagehand-server/vX.Y.Z
    if not tag.startswith("stagehand-server/v"):
        return None

    ver = tag.removeprefix("stagehand-server/v")
    # Drop any pre-release/build metadata (we only expect stable tags here).
    ver = ver.split("-", 1)[0].split("+", 1)[0]
    parts = ver.split(".")
    if len(parts) != 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None


def _http_get_json(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "stagehand-python/download-binary",
    }
    # Optional, but helps avoid rate limits in CI.
    token = (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def resolve_latest_server_tag() -> str:
    """Resolve the latest stagehand-server/v* tag from GitHub releases."""
    repo = "browserbase/stagehand"
    releases_url = f"https://api.github.com/repos/{repo}/releases?per_page=100"
    try:
        releases = _http_get_json(releases_url)
    except urllib.error.HTTPError as e:  # type: ignore[misc]
        raise RuntimeError(f"Failed to query GitHub releases (HTTP {e.code}): {releases_url}") from e  # type: ignore[union-attr]
    except Exception as e:
        raise RuntimeError(f"Failed to query GitHub releases: {releases_url}") from e

    if not isinstance(releases, list):
        raise RuntimeError(f"Unexpected GitHub API response for releases: {type(releases).__name__}")

    best: tuple[tuple[int, int, int], str] | None = None
    for r in releases:
        if not isinstance(r, dict):
            continue
        tag = r.get("tag_name")
        if not isinstance(tag, str):
            continue
        parsed = _parse_server_tag(tag)
        if parsed is None:
            continue
        if best is None or parsed > best[0]:
            best = (parsed, tag)

    if best is None:
        raise RuntimeError("No stagehand-server/v* GitHub Releases found for browserbase/stagehand")

    return best[1]


def download_binary(version: str) -> None:
    """Download the binary for the current platform."""
    plat, arch = get_platform_info()
    binary_filename = get_binary_filename(plat, arch)
    local_filename = get_local_filename(plat, arch)

    # GitHub release URL
    repo = "browserbase/stagehand"
    tag = version if version.startswith("stagehand-server/v") else f"stagehand-server/{version}"
    url = f"https://github.com/{repo}/releases/download/{tag}/{binary_filename}"

    # Destination path
    repo_root = Path(__file__).parent.parent
    dest_dir = repo_root / "bin" / "sea"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / local_filename

    if dest_path.exists():
        print(f"✓ Binary already exists: {dest_path}")
        response = input("  Overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("  Skipping download.")
            return

    print(f"📦 Downloading binary for {plat}-{arch}...")
    print(f"   From: {url}")
    print(f"   To: {dest_path}")

    try:
        # Download with progress
        def reporthook(block_num: int, block_size: int, total_size: int) -> None:
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")

        urllib.request.urlretrieve(url, dest_path, reporthook)  # type: ignore[arg-type]
        print()  # New line after progress

        # Make executable on Unix
        if plat != "win32":
            import os
            os.chmod(dest_path, 0o755)

        size_mb = dest_path.stat().st_size / (1024 * 1024)
        print(f"✅ Downloaded successfully: {dest_path} ({size_mb:.1f} MB)")
        print(f"\n💡 You can now run: uv run python test_local_mode.py")

    except urllib.error.HTTPError as e:  # type: ignore[misc]
        print(f"\n❌ Error: Failed to download binary (HTTP {e.code})")  # type: ignore[union-attr]
        print(f"   URL: {url}")
        print(f"\n   Available releases at: https://github.com/{repo}/releases")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download stagehand-server binary for local development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/download-binary.py
  python scripts/download-binary.py --version v3.2.0
  python scripts/download-binary.py --version stagehand-server/v3.2.0
        """,
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Stagehand server release tag/version to download (e.g. v3.2.0 or stagehand-server/v3.2.0). Defaults to latest stagehand-server/* GitHub Release.",
    )

    args = parser.parse_args()
    version = str(args.version).strip() if args.version is not None else ""
    if not version:
        latest_tag = resolve_latest_server_tag()
        download_binary(latest_tag)
        return

    download_binary(version)


if __name__ == "__main__":
    main()
