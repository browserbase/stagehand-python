"""Unit tests for Valkey cache backend configuration.

Tests cover:
- SeaServerConfig dataclass accepts valkey fields
- _build_process_env propagates valkey config as environment variables
- Client constructors accept valkey params and pass them through
- copy()/with_options() preserves and overrides valkey config
- ValkeyCacheOptions TypedDict is importable
"""

from __future__ import annotations

from pathlib import Path

from stagehand import Stagehand, AsyncStagehand
from stagehand.types import ValkeyCacheOptions
from stagehand._custom.sea_server import SeaServerConfig, SeaServerManager


class TestSeaServerConfigValkey:
    def test_defaults_to_none(self) -> None:
        config = SeaServerConfig(
            host="127.0.0.1",
            port=9222,
            headless=True,
            ready_timeout_s=10.0,
            model_api_key=None,
            chrome_path=None,
            shutdown_on_close=True,
        )
        assert config.valkey_host is None
        assert config.valkey_port is None
        assert config.valkey_tls is None
        assert config.valkey_password is None
        assert config.valkey_username is None
        assert config.cache_ttl is None
        assert config.valkey_key_prefix is None

    def test_accepts_all_valkey_fields(self) -> None:
        config = SeaServerConfig(
            host="127.0.0.1",
            port=9222,
            headless=True,
            ready_timeout_s=10.0,
            model_api_key=None,
            chrome_path=None,
            shutdown_on_close=True,
            valkey_host="valkey.example.com",
            valkey_port=6380,
            valkey_tls=True,
            valkey_password="secret",
            valkey_username="admin",
            cache_ttl=3600,
            valkey_key_prefix="myapp",
        )
        assert config.valkey_host == "valkey.example.com"
        assert config.valkey_port == 6380
        assert config.valkey_tls is True
        assert config.valkey_password == "secret"
        assert config.valkey_username == "admin"
        assert config.cache_ttl == 3600
        assert config.valkey_key_prefix == "myapp"


class TestBuildProcessEnvValkey:
    def _make_manager(self, tmp_path: Path, **valkey_kwargs: object) -> SeaServerManager:
        binary = tmp_path / "fake-binary"
        binary.write_text("x")
        config = SeaServerConfig(
            host="127.0.0.1",
            port=9222,
            headless=True,
            ready_timeout_s=10.0,
            model_api_key="test-key",
            chrome_path=None,
            shutdown_on_close=True,
            **valkey_kwargs,  # type: ignore[arg-type]
        )
        return SeaServerManager(config=config, _local_stagehand_binary_path=binary)

    def test_no_valkey_env_when_not_configured(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path)
        env = mgr._build_process_env(port=9222)
        assert "VALKEY_HOST" not in env
        assert "VALKEY_PORT" not in env
        assert "VALKEY_TLS" not in env
        assert "VALKEY_PASSWORD" not in env
        assert "VALKEY_USERNAME" not in env
        assert "CACHE_TTL" not in env
        assert "VALKEY_KEY_PREFIX" not in env

    def test_valkey_host_sets_env(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path, valkey_host="valkey.local")
        env = mgr._build_process_env(port=9222)
        assert env["VALKEY_HOST"] == "valkey.local"

    def test_valkey_port_sets_env(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path, valkey_port=6380)
        env = mgr._build_process_env(port=9222)
        assert env["VALKEY_PORT"] == "6380"

    def test_valkey_tls_true(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path, valkey_tls=True)
        env = mgr._build_process_env(port=9222)
        assert env["VALKEY_TLS"] == "true"

    def test_valkey_tls_false(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path, valkey_tls=False)
        env = mgr._build_process_env(port=9222)
        assert env["VALKEY_TLS"] == "false"

    def test_valkey_credentials_set_env(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path, valkey_password="pw", valkey_username="user")
        env = mgr._build_process_env(port=9222)
        assert env["VALKEY_PASSWORD"] == "pw"
        assert env["VALKEY_USERNAME"] == "user"

    def test_cache_ttl_sets_env(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path, cache_ttl=7200)
        env = mgr._build_process_env(port=9222)
        assert env["CACHE_TTL"] == "7200"

    def test_valkey_key_prefix_sets_env(self, tmp_path: Path) -> None:
        mgr = self._make_manager(tmp_path, valkey_key_prefix="custom")
        env = mgr._build_process_env(port=9222)
        assert env["VALKEY_KEY_PREFIX"] == "custom"

    def test_all_valkey_env_vars_together(self, tmp_path: Path) -> None:
        mgr = self._make_manager(
            tmp_path,
            valkey_host="host",
            valkey_port=6381,
            valkey_tls=True,
            valkey_password="pass",
            valkey_username="usr",
            cache_ttl=300,
            valkey_key_prefix="pfx",
        )
        env = mgr._build_process_env(port=9222)
        assert env["VALKEY_HOST"] == "host"
        assert env["VALKEY_PORT"] == "6381"
        assert env["VALKEY_TLS"] == "true"
        assert env["VALKEY_PASSWORD"] == "pass"
        assert env["VALKEY_USERNAME"] == "usr"
        assert env["CACHE_TTL"] == "300"
        assert env["VALKEY_KEY_PREFIX"] == "pfx"


class TestClientValkeyParams:
    def test_sync_client_accepts_valkey_params(self) -> None:
        client = Stagehand(
            base_url="http://localhost:4010",
            browserbase_api_key="test",
            model_api_key="test",
            valkey_host="valkey.local",
            valkey_port=6380,
            valkey_tls=True,
            valkey_password="pw",
            valkey_username="user",
            cache_ttl=3600,
            valkey_key_prefix="myapp",
        )
        assert client._valkey_host == "valkey.local"
        assert client._valkey_port == 6380
        assert client._valkey_tls is True
        assert client._valkey_password == "pw"
        assert client._valkey_username == "user"
        assert client._cache_ttl == 3600
        assert client._valkey_key_prefix == "myapp"
        client.close()

    def test_async_client_accepts_valkey_params(self) -> None:
        client = AsyncStagehand(
            base_url="http://localhost:4010",
            browserbase_api_key="test",
            model_api_key="test",
            valkey_host="valkey.local",
            valkey_port=6380,
        )
        assert client._valkey_host == "valkey.local"
        assert client._valkey_port == 6380

    def test_sync_client_defaults_none(self) -> None:
        client = Stagehand(
            base_url="http://localhost:4010",
            browserbase_api_key="test",
            model_api_key="test",
        )
        assert client._valkey_host is None
        assert client._valkey_port is None
        assert client._valkey_tls is None
        assert client._valkey_password is None
        assert client._valkey_username is None
        assert client._cache_ttl is None
        assert client._valkey_key_prefix is None
        client.close()

    def test_with_options_preserves_valkey(self) -> None:
        client = Stagehand(
            base_url="http://localhost:4010",
            browserbase_api_key="test",
            model_api_key="test",
            valkey_host="original.host",
            cache_ttl=1800,
        )
        copied = client.with_options(max_retries=5)
        assert copied._valkey_host == "original.host"
        assert copied._cache_ttl == 1800
        client.close()
        copied.close()

    def test_with_options_overrides_valkey(self) -> None:
        client = Stagehand(
            base_url="http://localhost:4010",
            browserbase_api_key="test",
            model_api_key="test",
            valkey_host="original.host",
            cache_ttl=1800,
        )
        copied = client.with_options(valkey_host="new.host", cache_ttl=900)
        assert copied._valkey_host == "new.host"
        assert copied._cache_ttl == 900
        client.close()
        copied.close()


class TestValkeyCacheOptionsType:
    def test_importable(self) -> None:
        # ValkeyCacheOptions should be importable from stagehand.types
        assert ValkeyCacheOptions is not None

    def test_is_typed_dict(self) -> None:
        # Verify it behaves as a TypedDict (has __annotations__)
        assert "host" in ValkeyCacheOptions.__annotations__
        assert "port" in ValkeyCacheOptions.__annotations__
        assert "use_tls" in ValkeyCacheOptions.__annotations__
        assert "password" in ValkeyCacheOptions.__annotations__
        assert "username" in ValkeyCacheOptions.__annotations__
        assert "cache_ttl" in ValkeyCacheOptions.__annotations__
        assert "key_prefix" in ValkeyCacheOptions.__annotations__


class TestSessionStartValkeyCache:
    """Verify valkey_cache is a first-class parameter in sessions.start()."""

    def test_start_accepts_valkey_cache_param(self) -> None:
        """sessions.start() should accept valkey_cache without needing extra_body."""
        import inspect

        from stagehand.resources.sessions import SessionsResource, AsyncSessionsResource

        sync_sig = inspect.signature(SessionsResource.start)
        assert "valkey_cache" in sync_sig.parameters

        async_sig = inspect.signature(AsyncSessionsResource.start)
        assert "valkey_cache" in async_sig.parameters
