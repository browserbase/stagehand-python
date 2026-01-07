from __future__ import annotations

import os
import sys
import hashlib
import platform
import importlib.resources as importlib_resources
from pathlib import Path
from contextlib import suppress


def _platform_tag() -> tuple[str, str]:
    plat = "win32" if sys.platform.startswith("win") else ("darwin" if sys.platform == "darwin" else "linux")
    machine = platform.machine().lower()
    arch = "arm64" if machine in ("arm64", "aarch64") else "x64"
    return plat, arch


def default_binary_filename() -> str:
    plat, arch = _platform_tag()
    name = f"stagehand-{plat}-{arch}"
    return name + (".exe" if plat == "win32" else "")


def _cache_dir() -> Path:
    # Avoid extra deps (e.g. platformdirs) for now.
    if sys.platform == "darwin":
        root = Path.home() / "Library" / "Caches"
    elif sys.platform.startswith("win"):
        root = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))
    return root / "stagehand" / "sea"


def _ensure_executable(path: Path) -> None:
    if sys.platform.startswith("win"):
        return
    with suppress(OSError):
        mode = path.stat().st_mode
        path.chmod(mode | 0o100)


def _resource_binary_path(filename: str) -> Path | None:
    # Expect binaries to live at stagehand/_sea/<filename> inside the installed package.
    try:
        root = importlib_resources.files("stagehand")
    except Exception:
        return None

    candidate = root.joinpath("_sea").joinpath(filename)
    try:
        if not candidate.is_file():
            return None
    except Exception:
        return None

    with importlib_resources.as_file(candidate) as extracted:
        return extracted


def _copy_to_cache(*, src: Path, filename: str, version: str) -> Path:
    cache_root = _cache_dir() / version
    cache_root.mkdir(parents=True, exist_ok=True)
    dst = cache_root / filename

    if dst.exists():
        _ensure_executable(dst)
        return dst

    data = src.read_bytes()
    tmp = cache_root / f".{filename}.{hashlib.sha256(data).hexdigest()}.tmp"
    tmp.write_bytes(data)
    tmp.replace(dst)
    _ensure_executable(dst)
    return dst


def resolve_binary_path(
    *,
    local_binary_path: str | os.PathLike[str] | None = None,
    version: str | None = None,
) -> Path:
    if local_binary_path is not None:
        path = Path(local_binary_path)
        _ensure_executable(path)
        return path

    env = os.environ.get("STAGEHAND_SEA_BINARY")
    if env:
        path = Path(env)
        _ensure_executable(path)
        return path

    filename = default_binary_filename()

    # Prefer packaged resources (works for wheel installs).
    resource_path = _resource_binary_path(filename)
    if resource_path is not None:
        # Best-effort versioning to keep cached binaries stable across upgrades.
        if version is None:
            version = os.environ.get("STAGEHAND_VERSION", "dev")
        return _copy_to_cache(src=resource_path, filename=filename, version=version)

    # Fallback: source checkout layout (works for local dev in-repo).
    here = Path(__file__).resolve()
    repo_root = here.parents[3]  # stagehand-python/
    candidate = repo_root / "bin" / "sea" / filename

    if not candidate.exists():
        raise FileNotFoundError(
            f"Stagehand SEA binary not found at {candidate}.\n"
            f"For local development, download the binary using:\n"
            f"  uv run python scripts/download-binary.py\n"
            f"Or set the STAGEHAND_SEA_BINARY environment variable to point to your binary.\n"
            f"For production use, install a platform-specific wheel from PyPI.\n"
            f"See: https://github.com/browserbase/stagehand-python#local-development"
        )

    _ensure_executable(candidate)
    return candidate
