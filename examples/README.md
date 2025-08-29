# Stagehand Examples

This directory contains examples demonstrating how to use Stagehand with local browser automation and custom LLM endpoints.

## Prerequisites

Before running the examples, make sure you have:

1. **Python 3.8+** installed
2. **Chrome/Chromium browser** installed (Playwright will use this)
3. **LLM Provider API Key** - at least one of:
   - OpenAI API key (`OPENAI_API_KEY`)
   - Anthropic API key (`ANTHROPIC_API_KEY`)
   - Groq API key (`GROQ_API_KEY`)
   - Together AI API key (`TOGETHER_API_KEY`)

## Environment Setup

### Option 1: Using .env file (Recommended)

Create a `.env` file in the project root:

```bash
# OpenAI (recommended for getting started)
OPENAI_API_KEY=your-openai-api-key-here

# Or use other providers
# ANTHROPIC_API_KEY=your-anthropic-api-key-here
# GROQ_API_KEY=your-groq-api-key-here
# TOGETHER_API_KEY=your-together-api-key-here
```

### Option 2: Environment Variables

#### On Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
python examples/quickstart.py
```

#### On Linux/macOS:
```bash
export OPENAI_API_KEY="your-api-key-here"
python examples/quickstart.py
```

## Available Examples

### 1. `quickstart.py` - Basic Getting Started
The simplest example showing:
- Local browser automation
- Custom LLM endpoint configuration
- Structured data extraction with Pydantic
- Basic browser actions (act, extract, observe)

```bash
python examples/quickstart.py
```

### 2. `example.py` - Comprehensive Demo
A more detailed example with:
- Rich console output and logging
- Multiple browser actions
- Error handling
- Step-by-step automation workflow

```bash
python examples/example.py
```

### 3. `agent_example.py` - AI Agent Usage
Demonstrates the agent functionality:
- Agent-based automation
- Multi-step task execution
- Agent result handling

```bash
python examples/agent_example.py
```

### 4. `custom_llm_endpoints.py` - LLM Provider Configurations
Shows how to configure different LLM providers:
- OpenAI configuration
- Anthropic Claude configuration
- Together AI configuration
- Groq configuration
- Local OpenAI-compatible servers
- Error handling and validation

```bash
python examples/custom_llm_endpoints.py
```

### 5. `windows_powershell_example.py` - Windows Compatibility
Specifically designed for Windows PowerShell users:
- Windows-specific features
- PowerShell integration examples
- Multiple provider support with automatic selection
- Comprehensive error handling

```bash
python examples/windows_powershell_example.py
```

### 6. `quickstart_jupyter_notebook.ipynb` - Jupyter Notebook
Interactive notebook example:
- Step-by-step tutorial
- Local browser configuration
- Multiple provider examples
- Rich documentation and explanations

Open in Jupyter Lab/Notebook:
```bash
jupyter lab examples/quickstart_jupyter_notebook.ipynb
```

## Configuration Examples

### OpenAI Configuration
```python
config = StagehandConfig(
    model_name="gpt-4o-mini",
    model_client_options={
        "api_base": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "timeout": 30
    },
    local_browser_launch_options={
        "headless": False,
        "viewport": {"width": 1280, "height": 720}
    }
)
```

### Anthropic Configuration
```python
config = StagehandConfig(
    model_name="claude-3-haiku-20240307",
    model_client_options={
        "api_base": "https://api.anthropic.com",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "timeout": 60
    },
    local_browser_launch_options={"headless": False}
)
```

### Together AI Configuration
```python
config = StagehandConfig(
    model_name="together/llama-2-7b-chat",
    model_client_options={
        "api_base": "https://api.together.xyz/v1",
        "api_key": os.getenv("TOGETHER_API_KEY"),
        "timeout": 45
    },
    local_browser_launch_options={"headless": False}
)
```

## Browser Configuration Options

### Headless Mode
```python
local_browser_launch_options={
    "headless": True,  # Run without visible browser window
    "viewport": {"width": 1920, "height": 1080}
}
```

### Custom Browser Path
```python
local_browser_launch_options={
    "executable_path": "/path/to/chrome",  # Custom browser executable
    "headless": False
}
```

### Additional Browser Arguments
```python
local_browser_launch_options={
    "args": [
        "--disable-web-security",
        "--disable-features=VizDisplayCompositor",
        "--no-sandbox"
    ],
    "headless": False
}
```

## Windows PowerShell Tips

### Setting Environment Variables
```powershell
# Set for current session
$env:OPENAI_API_KEY="your-api-key"

# Set permanently for user
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-api-key", "User")
```

### Running Scripts
```powershell
# Run example
python examples/quickstart.py

# Run with specific provider
$env:PREFERRED_PROVIDER="anthropic"; python examples/windows_powershell_example.py

# Chain commands (use semicolon instead of &&)
python examples/quickstart.py; python examples/example.py
```

### Using PowerShell Scripts
```powershell
# Format code
./format.ps1

# Run tests
./run_tests.ps1

# Run tests and open coverage report
./run_tests.ps1 -Open
```

## Troubleshooting

### Common Issues

1. **"No LLM provider API keys found"**
   - Make sure you've set at least one API key environment variable
   - Check that the variable name is correct (e.g., `OPENAI_API_KEY`)

2. **"Browser not found"**
   - Install Chrome or Chromium browser
   - Run `playwright install chromium` to install Playwright's browser

3. **"Module not found"**
   - Make sure Stagehand is installed: `pip install stagehand`
   - Or install in development mode: `pip install -e .`

4. **Windows PowerShell encoding issues**
   - The examples handle UTF-8 encoding automatically
   - If you see strange characters, try running in Windows Terminal

### Getting Help

- Check the main README.md for installation instructions
- Review the requirements.md and design.md in `.kiro/specs/browserbase-removal/`
- Look at the test files for more usage examples
- Open an issue on GitHub if you encounter problems

## Migration from Browserbase

If you were previously using Browserbase configuration, here's how to migrate:

### Old Configuration (Browserbase)
```python
config = StagehandConfig(
    env="BROWSERBASE",
    api_key="browserbase-key",
    project_id="browserbase-project",
    model_name="gpt-4o"
)
```

### New Configuration (Local)
```python
config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    local_browser_launch_options={
        "headless": False
    }
)
```

The key changes:
- Remove `env`, `api_key`, `project_id` fields
- Add `model_client_options` with LLM provider configuration
- Add `local_browser_launch_options` for browser settings
- All browser operations now use local Playwright instances