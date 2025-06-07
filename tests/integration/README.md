# Stagehand Python Integration Tests

This directory contains comprehensive integration tests for the Stagehand Python SDK, designed to test the complete functionality of the library in both LOCAL and BROWSERBASE environments.

## 📁 Test Structure

### Core Integration Tests

- **`test_stagehand_integration.py`** - Main integration tests covering end-to-end workflows
- **`test_observe_integration.py`** - Tests for `page.observe()` functionality
- **`test_act_integration.py`** - Tests for `page.act()` functionality  
- **`test_extract_integration.py`** - Tests for `page.extract()` functionality

### Inspiration from Evals

These tests are inspired by the evaluation scripts in the `/evals` directory:

- **Observe tests** mirror `evals/observe/` functionality
- **Act tests** mirror `evals/act/` functionality
- **Extract tests** mirror `evals/extract/` functionality

## 🏷️ Test Markers

Tests are organized using pytest markers for flexible execution:

### Environment Markers
- `@pytest.mark.local` - Tests that run in LOCAL mode (using local browser)
- `@pytest.mark.browserbase` - Tests that run in BROWSERBASE mode (cloud browsers)

### Execution Type Markers
- `@pytest.mark.integration` - Integration tests (all tests in this directory)
- `@pytest.mark.e2e` - End-to-end tests covering complete workflows
- `@pytest.mark.slow` - Tests that take longer to execute
- `@pytest.mark.smoke` - Quick smoke tests for basic functionality

### Functionality Markers
- `@pytest.mark.observe` - Tests for observe functionality
- `@pytest.mark.act` - Tests for act functionality
- `@pytest.mark.extract` - Tests for extract functionality

## 🚀 Running Tests

### Local Execution

Use the provided helper script for easy test execution:

```bash
# Run basic local integration tests
./run_integration_tests.sh --local

# Run Browserbase tests (requires credentials)
./run_integration_tests.sh --browserbase

# Run all tests with coverage
./run_integration_tests.sh --all --coverage

# Run specific functionality tests
./run_integration_tests.sh --observe --local
./run_integration_tests.sh --act --local
./run_integration_tests.sh --extract --local

# Include slow tests
./run_integration_tests.sh --local --slow

# Run end-to-end tests
./run_integration_tests.sh --e2e --local
```

### Manual pytest Execution

```bash
# Run all local integration tests (excluding slow ones)
pytest tests/integration/ -m "local and not slow" -v

# Run Browserbase tests
pytest tests/integration/ -m "browserbase" -v

# Run specific test files
pytest tests/integration/test_observe_integration.py -v

# Run with coverage
pytest tests/integration/ -m "local" --cov=stagehand --cov-report=html
```

## 🔧 Environment Setup

### Local Mode Requirements

For LOCAL mode tests, you need:

1. **Python Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Playwright Browser**:
   ```bash
   playwright install chromium
   playwright install-deps chromium  # Linux only
   ```

3. **AI Model API Key**:
   ```bash
   export MODEL_API_KEY="your_openai_key"
   # OR
   export OPENAI_API_KEY="your_openai_key"
   ```

4. **Display Server** (Linux CI):
   ```bash
   # Install xvfb for headless browser testing
   sudo apt-get install -y xvfb
   
   # Run tests with virtual display
   xvfb-run -a pytest tests/integration/ -m "local"
   ```

### Browserbase Mode Requirements

For BROWSERBASE mode tests, you need:

```bash
export BROWSERBASE_API_KEY="your_browserbase_api_key"
export BROWSERBASE_PROJECT_ID="your_browserbase_project_id"
export MODEL_API_KEY="your_openai_key"
```

## 🤖 CI/CD Integration

### GitHub Actions Workflows

The tests are integrated into CI/CD with different triggers:

#### Always Run
- **Local Integration Tests** (`test-integration-local`)
  - Runs on every PR and push
  - Uses headless browsers with xvfb
  - Excludes slow tests by default
  - Markers: `local and not slow`

#### Label-Triggered Jobs
- **Slow Tests** (`test-integration-slow`)
  - Triggered by `test-slow` or `slow` labels
  - Includes performance and complex workflow tests
  - Markers: `slow and local`

- **Browserbase Tests** (`test-browserbase`)
  - Triggered by `test-browserbase` or `browserbase` labels
  - Requires Browserbase secrets in repository
  - Markers: `browserbase`

- **End-to-End Tests** (`test-e2e`)
  - Triggered by `test-e2e` or `e2e` labels
  - Complete user journey simulations
  - Markers: `e2e`

### Adding PR Labels

To run specific test types in CI, add these labels to your PR:

- `test-slow` - Run slow integration tests
- `test-browserbase` - Run Browserbase cloud tests
- `test-e2e` - Run end-to-end tests
- `test-all` - Run complete test suite

## 📊 Test Categories

### Basic Navigation and Interaction
- Page navigation
- Element observation
- Form filling
- Button clicking
- Search workflows

### Data Extraction
- Simple text extraction
- Schema-based extraction
- Multi-element extraction
- Error handling for extraction

### Complex Workflows
- Multi-page navigation
- Search and result interaction
- Form submission workflows
- Error recovery scenarios

### Performance Testing
- Response time measurement
- Multiple operation timing
- Resource usage validation

### Accessibility Testing
- Screen reader compatibility
- Keyboard navigation
- ARIA attribute testing

## 🔍 Debugging Failed Tests

### Local Debugging

1. **Run with verbose output**:
   ```bash
   ./run_integration_tests.sh --local --verbose
   ```

2. **Run single test**:
   ```bash
   pytest tests/integration/test_observe_integration.py::TestObserveIntegration::test_observe_form_elements_local -v -s
   ```

3. **Use non-headless mode** (modify test config):
   ```python
   # In test fixtures, change:
   headless=False  # For visual debugging
   ```

### Browserbase Debugging

1. **Check session URLs**:
   - Tests provide `session_url` in results
   - Visit the URL to see browser session recording

2. **Enable verbose logging**:
   ```python
   # In test config:
   verbose=3  # Maximum detail
   ```

## 🧪 Writing New Integration Tests

### Test Structure Template

```python
@pytest.mark.asyncio
@pytest.mark.local  # or @pytest.mark.browserbase
async def test_new_functionality_local(self, local_stagehand):
    """Test description"""
    stagehand = local_stagehand
    
    # Navigate to test page
    await stagehand.page.goto("https://example.com")
    
    # Perform actions
    await stagehand.page.act("Click the button")
    
    # Observe results
    results = await stagehand.page.observe("Find result elements")
    
    # Extract data if needed
    data = await stagehand.page.extract("Extract page data")
    
    # Assertions
    assert results is not None
    assert len(results) > 0
```

### Best Practices

1. **Use appropriate markers** for test categorization
2. **Test both LOCAL and BROWSERBASE** modes when possible
3. **Include error handling tests** for robustness
4. **Use realistic test scenarios** that mirror actual usage
5. **Keep tests independent** - no dependencies between tests
6. **Clean up resources** using fixtures with proper teardown
7. **Add performance assertions** for time-sensitive operations

### Adding Tests to CI

1. Mark tests with appropriate pytest markers
2. Ensure tests work in headless mode
3. Use reliable test websites (avoid flaky external sites)
4. Add to appropriate CI job based on markers
5. Test locally before submitting PR

## 📚 Related Documentation

- [Main README](../../README.md) - Project overview
- [Evals README](../../evals/README.md) - Evaluation scripts
- [Unit Tests](../unit/README.md) - Unit test documentation
- [Examples](../../examples/) - Usage examples

## 🔧 Troubleshooting

### Common Issues

1. **Playwright not installed**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Display server issues (Linux)**:
   ```bash
   sudo apt-get install xvfb
   export DISPLAY=:99
   xvfb-run -a your_test_command
   ```

3. **API key issues**:
   - Verify environment variables are set
   - Check API key validity
   - Ensure sufficient API credits

4. **Network timeouts**:
   - Increase timeout values in test config
   - Check internet connectivity
   - Consider using local test pages

5. **Browser crashes**:
   - Update Playwright browsers
   - Check system resources
   - Use headless mode for stability

### Getting Help

- Check the [main repository issues](https://github.com/browserbase/stagehand-python/issues)
- Review similar tests in `/evals` directory
- Look at `/examples` for usage patterns
- Check CI logs for detailed error information 