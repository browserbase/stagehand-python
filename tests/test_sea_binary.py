from __future__ import annotations

import importlib.util
from pathlib import Path
from contextlib import contextmanager
from collections.abc import Iterator

import pytest

from stagehand._custom import sea_binary
from stagehand._version import __version__


def _load_download_binary_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "download_binary.py"
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

    def _fake_resource_binary_path(_filename: str, *, version: str) -> Path:
        captured["version"] = version
        return resource_path

    monkeypatch.setattr(sea_binary, "_resource_binary_path", _fake_resource_binary_path)

    resolved = sea_binary.resolve_binary_path()

    assert resolved == resource_path
    assert captured["version"] == __version__


def test_resolve_binary_path_caches_resource_before_context_exits(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class FakeResource:
        def joinpath(self, _name: str) -> FakeResource:
            return self

        def is_file(self) -> bool:
            return True

    extracted = tmp_path / "temporary-binary"

    @contextmanager
    def fake_as_file(_resource: object) -> Iterator[Path]:
        extracted.write_bytes(b"binary")
        try:
            yield extracted
        finally:
            extracted.unlink()

    def fake_files(_package: str) -> FakeResource:
        return FakeResource()

    monkeypatch.delenv("STAGEHAND_SEA_BINARY", raising=False)
    monkeypatch.setattr(sea_binary.importlib_resources, "files", fake_files)
    monkeypatch.setattr(sea_binary.importlib_resources, "as_file", fake_as_file)
    monkeypatch.setattr(sea_binary, "_cache_dir", lambda: tmp_path / "cache")
    monkeypatch.setattr(sea_binary, "default_binary_filename", lambda: "stagehand-test")

    resolved = sea_binary.resolve_binary_path(version="test")

    assert resolved == tmp_path / "cache" / "test" / "stagehand-test"
    assert resolved.read_bytes() == b"binary"
    assert not extracted.exists()


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
