"""Test configuration management and validation for StagehandConfig"""

import os
import pytest
from unittest.mock import patch

from stagehand.config import StagehandConfig, default_config


class TestStagehandConfig:
    """Test StagehandConfig creation and validation"""
    
    def test_default_config_values(self):
        """Test that default config has expected values"""
        config = StagehandConfig()
        
        assert config.env is None  # Should be determined automatically
        assert config.verbose == 1  # Default verbosity
        assert config.dom_settle_timeout_ms == 30000  # Default timeout
        assert config.self_heal is True  # Default self-healing enabled
        assert config.wait_for_captcha_solves is True  # Default wait for captcha
        assert config.headless is True  # Default headless mode
        assert config.enable_caching is False  # Default caching disabled
    
    def test_config_with_custom_values(self):
        """Test creation with custom configuration values"""
        config = StagehandConfig(
            env="LOCAL",
            api_key="test-api-key",
            project_id="test-project",
            model_name="gpt-4o-mini",
            verbose=2,
            dom_settle_timeout_ms=5000,
            self_heal=False,
            headless=False,
            system_prompt="Custom system prompt"
        )
        
        assert config.env == "LOCAL"
        assert config.api_key == "test-api-key"
        assert config.project_id == "test-project"
        assert config.model_name == "gpt-4o-mini"
        assert config.verbose == 2
        assert config.dom_settle_timeout_ms == 5000
        assert config.self_heal is False
        assert config.headless is False
        assert config.system_prompt == "Custom system prompt"
    
    def test_browserbase_config(self):
        """Test configuration for Browserbase environment"""
        config = StagehandConfig(
            env="BROWSERBASE",
            api_key="bb-api-key",
            project_id="bb-project-id",
            browserbase_session_id="existing-session",
            browserbase_session_create_params={
                "browserSettings": {
                    "viewport": {"width": 1920, "height": 1080}
                }
            }
        )
        
        assert config.env == "BROWSERBASE"
        assert config.api_key == "bb-api-key"
        assert config.project_id == "bb-project-id"
        assert config.browserbase_session_id == "existing-session"
        assert config.browserbase_session_create_params is not None
        assert config.browserbase_session_create_params["browserSettings"]["viewport"]["width"] == 1920
    
    def test_local_browser_config(self):
        """Test configuration for local browser environment"""
        launch_options = {
            "headless": False,
            "args": ["--disable-web-security"],
            "executablePath": "/opt/chrome/chrome"
        }
        
        config = StagehandConfig(
            env="LOCAL",
            headless=False,
            local_browser_launch_options=launch_options
        )
        
        assert config.env == "LOCAL"
        assert config.headless is False
        assert config.local_browser_launch_options == launch_options
        assert config.local_browser_launch_options["executablePath"] == "/opt/chrome/chrome"
    
    def test_model_client_options(self):
        """Test model client configuration options"""
        model_options = {
            "apiKey": "test-api-key",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 30
        }
        
        config = StagehandConfig(
            model_name="gpt-4o",
            model_client_options=model_options
        )
        
        assert config.model_name == "gpt-4o"
        assert config.model_client_options == model_options
        assert config.model_client_options["temperature"] == 0.7
    
    def test_config_with_overrides(self):
        """Test the with_overrides method"""
        base_config = StagehandConfig(
            env="LOCAL",
            verbose=1,
            model_name="gpt-4o-mini"
        )
        
        # Create new config with overrides
        new_config = base_config.with_overrides(
            verbose=2,
            dom_settle_timeout_ms=10000,
            self_heal=False
        )
        
        # Original config should be unchanged
        assert base_config.verbose == 1
        assert base_config.model_name == "gpt-4o-mini"
        assert base_config.env == "LOCAL"
        
        # New config should have overrides applied
        assert new_config.verbose == 2
        assert new_config.dom_settle_timeout_ms == 10000
        assert new_config.self_heal is False
        # Non-overridden values should remain
        assert new_config.model_name == "gpt-4o-mini"
        assert new_config.env == "LOCAL"
    
    def test_config_overrides_with_none_values(self):
        """Test that None values in overrides are properly handled"""
        base_config = StagehandConfig(
            model_name="gpt-4o",
            verbose=2
        )
        
        # Override with None should clear the value
        new_config = base_config.with_overrides(
            model_name=None,
            verbose=1
        )
        
        assert new_config.model_name is None
        assert new_config.verbose == 1
    
    def test_config_with_nested_overrides(self):
        """Test overrides with nested dictionary values"""
        base_config = StagehandConfig(
            local_browser_launch_options={"headless": True},
            model_client_options={"temperature": 0.5}
        )
        
        new_config = base_config.with_overrides(
            local_browser_launch_options={"headless": False, "args": ["--no-sandbox"]},
            model_client_options={"temperature": 0.8, "max_tokens": 1000}
        )
        
        # Should completely replace nested dicts, not merge
        assert new_config.local_browser_launch_options == {"headless": False, "args": ["--no-sandbox"]}
        assert new_config.model_client_options == {"temperature": 0.8, "max_tokens": 1000}
        
        # Original should be unchanged
        assert base_config.local_browser_launch_options == {"headless": True}
        assert base_config.model_client_options == {"temperature": 0.5}
    
    def test_logger_configuration(self):
        """Test logger configuration"""
        def custom_logger(msg, level, category=None, auxiliary=None):
            pass
        
        config = StagehandConfig(
            logger=custom_logger,
            verbose=3
        )
        
        assert config.logger == custom_logger
        assert config.verbose == 3
    
    def test_timeout_configurations(self):
        """Test various timeout configurations"""
        config = StagehandConfig(
            dom_settle_timeout_ms=15000,
            act_timeout_ms=45000
        )
        
        assert config.dom_settle_timeout_ms == 15000
        assert config.act_timeout_ms == 45000
    
    def test_agent_configurations(self):
        """Test agent-related configurations"""
        config = StagehandConfig(
            enable_caching=True,
            system_prompt="You are a helpful automation assistant"
        )
        
        assert config.enable_caching is True
        assert config.system_prompt == "You are a helpful automation assistant"


class TestDefaultConfig:
    """Test the default configuration instance"""
    
    def test_default_config_instance(self):
        """Test that default_config is properly instantiated"""
        assert isinstance(default_config, StagehandConfig)
        assert default_config.verbose == 1
        assert default_config.self_heal is True
        assert default_config.headless is True
    
    def test_default_config_immutability(self):
        """Test that default_config modifications don't affect new instances"""
        # Get original values
        original_verbose = default_config.verbose
        original_model = default_config.model_name
        
        # Create new config from default
        new_config = default_config.with_overrides(verbose=3, model_name="custom-model")
        
        # Default config should be unchanged
        assert default_config.verbose == original_verbose
        assert default_config.model_name == original_model
        
        # New config should have overrides
        assert new_config.verbose == 3
        assert new_config.model_name == "custom-model"


class TestConfigEnvironmentIntegration:
    """Test configuration integration with environment variables"""
    
    @patch.dict(os.environ, {
        "BROWSERBASE_API_KEY": "env-api-key",
        "BROWSERBASE_PROJECT_ID": "env-project-id",
        "MODEL_API_KEY": "env-model-key"
    })
    def test_environment_variable_priority(self):
        """Test that explicit config values take precedence over environment variables"""
        # Note: StagehandConfig itself doesn't read env vars directly,
        # but the client does. This tests the expected behavior.
        config = StagehandConfig(
            api_key="explicit-api-key",
            project_id="explicit-project-id"
        )
        
        # Explicit values should be preserved
        assert config.api_key == "explicit-api-key"
        assert config.project_id == "explicit-project-id"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_without_environment_variables(self):
        """Test configuration when environment variables are not set"""
        config = StagehandConfig(
            api_key="config-api-key",
            project_id="config-project-id"
        )
        
        assert config.api_key == "config-api-key"
        assert config.project_id == "config-project-id"


class TestConfigValidation:
    """Test configuration validation and error handling"""
    
    def test_invalid_env_value(self):
        """Test that invalid environment values are handled gracefully"""
        # StagehandConfig allows any env value, validation happens in client
        config = StagehandConfig(env="INVALID_ENV")
        assert config.env == "INVALID_ENV"
    
    def test_invalid_verbose_level(self):
        """Test with invalid verbose levels"""
        # Should accept any integer
        config = StagehandConfig(verbose=-1)
        assert config.verbose == -1
        
        config = StagehandConfig(verbose=100)
        assert config.verbose == 100
    
    def test_zero_timeout_values(self):
        """Test with zero timeout values"""
        config = StagehandConfig(
            dom_settle_timeout_ms=0,
            act_timeout_ms=0
        )
        
        assert config.dom_settle_timeout_ms == 0
        assert config.act_timeout_ms == 0
    
    def test_negative_timeout_values(self):
        """Test with negative timeout values"""
        config = StagehandConfig(
            dom_settle_timeout_ms=-1000,
            act_timeout_ms=-5000
        )
        
        # Should accept negative values (validation happens elsewhere)
        assert config.dom_settle_timeout_ms == -1000
        assert config.act_timeout_ms == -5000


class TestConfigSerialization:
    """Test configuration serialization and representation"""
    
    def test_config_dict_conversion(self):
        """Test converting config to dictionary"""
        config = StagehandConfig(
            env="LOCAL",
            api_key="test-key",
            verbose=2,
            headless=False
        )
        
        # Should be able to convert to dict for inspection
        config_dict = vars(config)
        assert config_dict["env"] == "LOCAL"
        assert config_dict["api_key"] == "test-key"
        assert config_dict["verbose"] == 2
        assert config_dict["headless"] is False
    
    def test_config_string_representation(self):
        """Test string representation of config"""
        config = StagehandConfig(
            env="BROWSERBASE",
            api_key="test-key",
            verbose=1
        )
        
        config_str = str(config)
        assert "StagehandConfig" in config_str
        # Should not expose sensitive information like API keys in string representation
        # (This depends on how __str__ is implemented)


class TestConfigEdgeCases:
    """Test edge cases and unusual configurations"""
    
    def test_empty_config(self):
        """Test creating config with no parameters"""
        config = StagehandConfig()
        
        # Should create valid config with defaults
        assert config.verbose == 1  # Default value
        assert config.env is None   # No default
        assert config.api_key is None
    
    def test_config_with_empty_strings(self):
        """Test config with empty string values"""
        config = StagehandConfig(
            api_key="",
            project_id="",
            model_name=""
        )
        
        assert config.api_key == ""
        assert config.project_id == ""
        assert config.model_name == ""
    
    def test_config_with_complex_options(self):
        """Test config with complex nested options"""
        complex_options = {
            "browserSettings": {
                "viewport": {"width": 1920, "height": 1080},
                "userAgent": "custom-user-agent",
                "extraHeaders": {"Authorization": "Bearer token"}
            },
            "proxy": {
                "server": "proxy.example.com:8080",
                "username": "user",
                "password": "pass"
            }
        }
        
        config = StagehandConfig(
            browserbase_session_create_params=complex_options
        )
        
        assert config.browserbase_session_create_params == complex_options
        assert config.browserbase_session_create_params["browserSettings"]["viewport"]["width"] == 1920
        assert config.browserbase_session_create_params["proxy"]["server"] == "proxy.example.com:8080"
    
    def test_config_with_callable_logger(self):
        """Test config with different types of logger functions"""
        call_count = 0
        
        def counting_logger(msg, level, category=None, auxiliary=None):
            nonlocal call_count
            call_count += 1
        
        config = StagehandConfig(logger=counting_logger)
        assert config.logger == counting_logger
        
        # Test that logger is callable
        assert callable(config.logger)
        
        # Test calling the logger
        config.logger("test message", 1)
        assert call_count == 1 