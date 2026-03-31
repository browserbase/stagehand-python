from __future__ import annotations

import importlib.util
from pathlib import Path

from stagehand.lib import sea_binary
from stagehand._version import __version__


def _load_download_binary_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "download-binary.py"
    spec = importlib.util.spec_from_file_location("download_binary_script", script_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


download_binary = _load_download_binary_module()


def test_resolve_binary_path_defaults_cache_version_to_package_version(
    monkeypatch,
    tmp_path: Path,
) -> None:
    resource_path = tmp_path / "stagehand-test"
    resource_path.write_bytes(b"binary")

    captured: dict[str, object] = {}

    monkeypatch.delenv("STAGEHAND_VERSION", raising=False)
    monkeypatch.setattr(sea_binary, "_resource_binary_path", lambda _filename: resource_path)

    def _fake_copy_to_cache(*, src: Path, filename: str, version: str) -> Path:
        captured["src"] = src
        captured["filename"] = filename
        captured["version"] = version
        return tmp_path / "cache" / filename

    monkeypatch.setattr(sea_binary, "_copy_to_cache", _fake_copy_to_cache)

    resolved = sea_binary.resolve_binary_path()

    assert resolved == tmp_path / "cache" / sea_binary.default_binary_filename()
    assert captured["src"] == resource_path
    assert captured["filename"] == sea_binary.default_binary_filename()
    assert captured["version"] == __version__


def test_parse_server_tag_rejects_prerelease_tags() -> None:
    assert download_binary._parse_server_tag("stagehand-server-v3/v3.20.0-dev") is None
    assert download_binary._parse_server_tag("stagehand-server-v3/v3.20.0+build.1") is None


def test_resolve_latest_server_tag_ignores_dev_releases(monkeypatch) -> None:
    releases = [
        {"tag_name": "stagehand-server-v3/v3.20.0-dev"},
        {"tag_name": "stagehand-server-v3/v3.19.1"},
        {"tag_name": "stagehand-server-v3/v3.19.0"},
    ]

    monkeypatch.setattr(download_binary, "_http_get_json", lambda _url: releases)

    assert download_binary.resolve_latest_server_tag() == "stagehand-server-v3/v3.19.1"
