# Stagehand Documentation

Welcome to the Stagehand documentation! This directory contains comprehensive guides for using Stagehand with local browser automation and custom LLM providers.

## Quick Start

- **[Main README](../README.md)** - Get started with Stagehand
- **[Installation and Basic Usage](../README.md#installation)** - Installation instructions and quickstart guide

## Configuration Guides

- **[LLM Client Configuration](llm_client_configuration.md)** - Complete guide to configuring LLM providers
  - OpenAI, Anthropic, Together AI, Groq configurations
  - Custom API endpoints
  - Environment variable setup
  - Configuration validation

## Migration

- **[Migration Guide](migration_guide.md)** - Complete migration from Browserbase to local configuration
  - Step-by-step migration instructions
  - Before/after configuration examples
  - Provider-specific configurations
  - Testing migration
  - Comprehensive FAQ section

### Migration Tools

- **[migration_utility.py](migration_utility.py)** - Automated migration analysis tool
  - Scan projects for Browserbase usage
  - Generate detailed migration reports
  - Provide specific migration suggestions
  - Show configuration examples

- **[validate_migration.py](validate_migration.py)** - Migration validation script
  - Verify environment setup
  - Test configuration creation
  - Validate runtime functionality
  - Check for leftover Browserbase files

- **[run_migration_check.ps1](run_migration_check.ps1)** - PowerShell helper script
  - Run analysis and validation together
  - Windows-friendly migration workflow
  - Comprehensive error reporting

#### Using Migration Tools

```bash
# Analyze your code for migration issues
python docs/migration_utility.py

# Analyze specific directory
python docs/migration_utility.py ./examples

# Show configuration migration example
python docs/migration_utility.py --config-example

# Validate your migration
python docs/validate_migration.py
```

**PowerShell (Windows):**
```powershell
# Run analysis and validation together
.\docs\run_migration_check.ps1 -Validate

# Analyze specific path
.\docs\run_migration_check.ps1 -Path .\examples

# Show help
.\docs\run_migration_check.ps1 -Help
```

## Troubleshooting

- **[Troubleshooting Guide](troubleshooting.md)** - Solutions for common issues
  - Configuration problems
  - Browser launch issues
  - LLM provider errors
  - Windows-specific solutions
  - Performance optimization

## Key Changes in Latest Version

### ✅ What's New
- **Local browser automation** - No external browser service required
- **Multiple LLM providers** - OpenAI, Anthropic, Together AI, Groq, and more
- **Custom API endpoints** - Use any OpenAI/Anthropic compatible API
- **Improved Windows support** - Better PowerShell compatibility
- **Enhanced configuration** - More flexible and powerful configuration options

### ❌ What's Removed
- **Browserbase dependency** - No longer requires Browserbase API
- **External browser sessions** - All browsers run locally
- **Complex environment setup** - Simplified configuration

### 🔄 What's Changed
- **Configuration format** - New `model_client_options` structure
- **Environment variables** - Use LLM provider keys instead of Browserbase keys
- **Browser options** - New `local_browser_launch_options` for browser configuration

## Examples

### Basic Configuration
```python
from stagehand import StagehandConfig, Stagehand

config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={
        "api_key": os.getenv("OPENAI_API_KEY")
    }
)
```

### Custom Provider Configuration
```python
config = StagehandConfig(
    model_name="claude-3-haiku-20240307",
    model_client_options={
        "api_base": "https://api.anthropic.com",
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    }
)
```

### Browser Customization
```python
config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={"api_key": os.getenv("OPENAI_API_KEY")},
    local_browser_launch_options={
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
        "user_data_dir": "./browser_data"
    }
)
```

## Getting Help

- **[GitHub Issues](https://github.com/browserbase/stagehand-python/issues)** - Report bugs or request features
- **[Slack Community](https://stagehand.dev/slack)** - Get help from the community
- **[Main Documentation](https://docs.stagehand.dev/)** - Official documentation site

## Contributing

See the main [Contributing Guide](https://docs.stagehand.dev/examples/contributing) for information on contributing to Stagehand.

---

For the most up-to-date information, always refer to the [official documentation](https://docs.stagehand.dev/).