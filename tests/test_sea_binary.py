from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

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
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    resource_path = tmp_path / "stagehand-test"
    resource_path.write_bytes(b"binary")

    captured: dict[str, object] = {}

    # This test is exercising the packaged-resource path, so clear the env override
    # that would otherwise bypass _resource_binary_path() entirely.
    monkeypatch.delenv("STAGEHAND_SEA_BINARY", raising=False)
    monkeypatch.delenv("STAGEHAND_VERSION", raising=False)

    def _fake_resource_binary_path(_filename: str) -> Path:
        return resource_path

    monkeypatch.setattr(sea_binary, "_resource_binary_path", _fake_resource_binary_path)

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


def test_normalize_server_tag_rejects_prerelease_input() -> None:
    try:
        download_binary.normalize_server_tag("v3.20.0-dev")
    except ValueError as exc:
        assert "stable tag" in str(exc)
    else:
        raise AssertionError("Expected prerelease version input to be rejected")


def test_resolve_latest_server_tag_ignores_dev_releases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    releases = [
        {"tag_name": "stagehand-server-v3/v3.20.0-dev"},
        {"tag_name": "stagehand-server-v3/v3.19.1"},
        {"tag_name": "stagehand-server-v3/v3.19.0"},
    ]

    def _fake_http_get_json(_url: str) -> list[dict[str, str]]:
        return releases

    monkeypatch.setattr(download_binary, "_http_get_json", _fake_http_get_json)

    assert download_binary.resolve_latest_server_tag() == "stagehand-server-v3/v3.19.1"
