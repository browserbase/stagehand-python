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

import sys
import platform
import argparse
import urllib.request
from pathlib import Path


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
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")

        urllib.request.urlretrieve(url, dest_path, reporthook)
        print()  # New line after progress

        # Make executable on Unix
        if plat != "win32":
            import os
            os.chmod(dest_path, 0o755)

        size_mb = dest_path.stat().st_size / (1024 * 1024)
        print(f"✅ Downloaded successfully: {dest_path} ({size_mb:.1f} MB)")
        print(f"\n💡 You can now run: uv run python test_local_mode.py")

    except urllib.error.HTTPError as e:
        print(f"\n❌ Error: Failed to download binary (HTTP {e.code})")
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
        default="v3.2.0",
        help="Version to download (default: v3.2.0)",
    )

    args = parser.parse_args()
    download_binary(args.version)


if __name__ == "__main__":
    main()
