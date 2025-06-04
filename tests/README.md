# Stagehand Testing Strategy

This document outlines the comprehensive testing strategy for the Stagehand Python SDK, including test organization, execution instructions, and contribution guidelines.

## 📁 Test Organization

```
tests/
├── unit/                          # Unit tests for individual components
│   ├── core/                      # Core functionality (page, config, etc.)
│   ├── handlers/                  # Handler-specific tests (act, extract, observe)
│   ├── llm/                       # LLM integration tests
│   ├── agent/                     # Agent system tests
│   ├── schemas/                   # Schema validation tests
│   └── utils/                     # Utility function tests
├── integration/                   # Integration tests
│   ├── end_to_end/               # Full workflow tests
│   ├── browser/                  # Browser integration tests
│   └── api/                      # API integration tests
├── performance/                   # Performance and load tests
├── fixtures/                     # Test data and fixtures
│   ├── html_pages/               # Mock HTML pages for testing
│   ├── mock_responses/           # Mock API responses
│   └── test_schemas/             # Test schema definitions
├── mocks/                        # Mock implementations
│   ├── mock_llm.py               # Mock LLM client
│   ├── mock_browser.py           # Mock browser
│   └── mock_server.py            # Mock Stagehand server
├── conftest.py                   # Shared fixtures and configuration
└── README.md                     # This file
```

## 🧪 Test Categories

### Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Test individual components in isolation
- **Coverage**: 90%+ for core modules
- **Speed**: Fast (< 1s per test)
- **Dependencies**: Mocked

### Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Test component interactions
- **Coverage**: 70%+ for integration paths
- **Speed**: Medium (1-10s per test)
- **Dependencies**: Mock external services

### End-to-End Tests (`@pytest.mark.e2e`)
- **Purpose**: Test complete workflows
- **Coverage**: Critical user journeys
- **Speed**: Slow (10s+ per test)
- **Dependencies**: Full system stack

### Performance Tests (`@pytest.mark.performance`)
- **Purpose**: Test performance characteristics
- **Coverage**: Critical performance paths
- **Speed**: Variable
- **Dependencies**: Realistic loads

### Browser Tests (`@pytest.mark.browserbase`/`@pytest.mark.local`)
- **Purpose**: Test browser integrations
- **Coverage**: Browser-specific functionality
- **Speed**: Medium to slow
- **Dependencies**: Browser instances

## 🚀 Running Tests

### Prerequisites

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install additional test dependencies
pip install jsonschema

# Install Playwright browsers (for local tests)
playwright install chromium
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stagehand --cov-report=html

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "unit and not slow"     # Fast unit tests only
pytest -m "e2e"                   # End-to-end tests only
```

### Running Specific Test Suites

```bash
# Schema validation tests
pytest tests/unit/schemas/ -v

# Page functionality tests
pytest tests/unit/core/test_page.py -v

# Handler tests
pytest tests/unit/handlers/ -v

# Integration workflows
pytest tests/integration/end_to_end/ -v

# Performance tests
pytest tests/performance/ -v
```

### Environment-Specific Tests

```bash
# Local browser tests (requires Playwright)
pytest -m local

# Browserbase tests (requires credentials)
pytest -m browserbase

# Mock-only tests (no external dependencies)
pytest -m mock
```

### CI/CD Test Execution

The tests are automatically run in GitHub Actions with different configurations:

- **Unit Tests**: Run on Python 3.9, 3.10, 3.11, 3.12
- **Integration Tests**: Run on Python 3.11 with different categories
- **Browserbase Tests**: Run on schedule or with `[test-browserbase]` in commit message
- **Performance Tests**: Run on schedule or with `[test-performance]` in commit message

## 🎯 Test Coverage Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|-----------------|
| Core modules (client.py, page.py, schemas.py) | 90% | 95% |
| Handler modules | 85% | 90% |
| Configuration | 80% | 85% |
| Integration paths | 70% | 80% |
| Overall project | 75% | 85% |

## 🔧 Writing New Tests

### Test Naming Conventions

```python
# Test classes
class TestComponentName:
    """Test ComponentName functionality"""

# Test methods
def test_method_behavior_scenario(self):
    """Test that method exhibits expected behavior in specific scenario"""

# Async test methods
@pytest.mark.asyncio
async def test_async_method_behavior(self):
    """Test async method behavior"""
```

### Using Fixtures

```python
def test_with_mock_client(self, mock_stagehand_client):
    """Test using the mock Stagehand client fixture"""
    assert mock_stagehand_client.env == "LOCAL"

def test_with_sample_html(self, sample_html_content):
    """Test using sample HTML content fixture"""
    assert "<html>" in sample_html_content

@pytest.mark.asyncio
async def test_async_with_mock_page(self, mock_stagehand_page):
    """Test using mock StagehandPage fixture"""
    result = await mock_stagehand_page.act("click button")
    assert result is not None
```

### Mock Usage Patterns

```python
# Using MockLLMClient
mock_llm = MockLLMClient()
mock_llm.set_custom_response("act", {"success": True, "action": "click"})
result = await mock_llm.completion([{"role": "user", "content": "click button"}])

# Using MockBrowser
playwright, browser, context, page = create_mock_browser_stack()
setup_page_with_content(page, "<html><body>Test</body></html>")

# Using MockServer
server, client = create_mock_server_with_client()
server.set_response_override("act", {"success": True})
```

### Test Structure

```python
class TestFeatureName:
    """Test feature functionality"""
    
    def test_basic_functionality(self):
        """Test basic feature behavior"""
        # Arrange
        config = create_test_config()
        
        # Act
        result = perform_action(config)
        
        # Assert
        assert result.success is True
        assert "expected" in result.message
    
    @pytest.mark.asyncio
    async def test_async_functionality(self, mock_fixture):
        """Test async feature behavior"""
        # Arrange
        mock_fixture.setup_response("success")
        
        # Act
        result = await async_action()
        
        # Assert
        assert result is not None
        mock_fixture.verify_called()
    
    def test_error_handling(self):
        """Test error scenarios"""
        with pytest.raises(ExpectedError):
            action_that_should_fail()
```

## 🏷️ Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_functionality():
    """Unit test example"""
    pass

@pytest.mark.integration
@pytest.mark.asyncio
async def test_integration_workflow():
    """Integration test example"""
    pass

@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_complete_workflow():
    """End-to-end test example"""
    pass

@pytest.mark.browserbase
@pytest.mark.asyncio
async def test_browserbase_feature():
    """Browserbase-specific test"""
    pass

@pytest.mark.performance
def test_performance_characteristic():
    """Performance test example"""
    pass
```

## 🐛 Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with verbose output and no capture
pytest -v -s

# Run single test with full traceback
pytest tests/unit/core/test_page.py::TestStagehandPage::test_act_functionality -vvv

# Run with debugger on failure
pytest --pdb

# Run with coverage and keep temp files
pytest --cov=stagehand --cov-report=html --tb=long
```

### Using Test Fixtures for Debugging

```python
def test_debug_with_real_output(self, caplog):
    """Test with captured log output"""
    with caplog.at_level(logging.DEBUG):
        perform_action()
    
    assert "expected log message" in caplog.text

def test_debug_with_temp_files(self, tmp_path):
    """Test with temporary files for debugging"""
    test_file = tmp_path / "test_data.json"
    test_file.write_text('{"test": "data"}')
    
    result = process_file(test_file)
    assert result.success
```

## 📊 Test Reporting

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=stagehand --cov-report=html
open htmlcov/index.html

# Generate XML coverage report (for CI)
pytest --cov=stagehand --cov-report=xml

# Show missing lines in terminal
pytest --cov=stagehand --cov-report=term-missing
```

### Test Result Reports

```bash
# Generate JUnit XML report
pytest --junit-xml=junit.xml

# Generate detailed test report
pytest --tb=long --maxfail=5 -v
```

## 🤝 Contributing Tests

### Before Adding Tests

1. **Check existing coverage**: `pytest --cov=stagehand --cov-report=term-missing`
2. **Identify gaps**: Look for uncovered lines and missing scenarios
3. **Plan test structure**: Decide on unit vs integration vs e2e
4. **Write test first**: Follow TDD principles when possible

### Test Contribution Checklist

- [ ] Test follows naming conventions
- [ ] Test is properly categorized with markers
- [ ] Test uses appropriate fixtures
- [ ] Test includes docstring describing purpose
- [ ] Test covers error scenarios
- [ ] Test is deterministic (no random failures)
- [ ] Test runs in reasonable time
- [ ] Test follows AAA pattern (Arrange, Act, Assert)

### Code Review Guidelines

When reviewing test code:

- [ ] Tests actually test the intended behavior
- [ ] Tests are not overly coupled to implementation
- [ ] Mocks are used appropriately
- [ ] Tests cover edge cases and error conditions
- [ ] Tests are maintainable and readable
- [ ] Tests don't have side effects

## 🚨 Common Issues and Solutions

### Async Test Issues

```python
# ❌ Wrong: Missing asyncio marker
def test_async_function():
    result = await async_function()

# ✅ Correct: With asyncio marker
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
```

### Mock Configuration Issues

```python
# ❌ Wrong: Mock not configured properly
mock_client = MagicMock()
result = await mock_client.page.act("click")  # Returns MagicMock, not ActResult

# ✅ Correct: Mock properly configured
mock_client = MagicMock()
mock_client.page.act = AsyncMock(return_value=ActResult(success=True, message="OK", action="click"))
result = await mock_client.page.act("click")
```

### Fixture Scope Issues

```python
# ❌ Wrong: Session-scoped fixture that should be function-scoped
@pytest.fixture(scope="session")
def mock_client():
    return MagicMock()  # Same mock used across all tests

# ✅ Correct: Function-scoped fixture
@pytest.fixture
def mock_client():
    return MagicMock()  # Fresh mock for each test
```

## 📈 Performance Testing

### Memory Usage Tests

```python
@pytest.mark.performance
def test_memory_usage():
    """Test memory usage stays within bounds"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform memory-intensive operation
    perform_large_operation()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Assert memory increase is reasonable (< 100MB)
    assert memory_increase < 100 * 1024 * 1024
```

### Response Time Tests

```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_response_time():
    """Test operation completes within time limit"""
    import time
    
    start_time = time.time()
    await perform_operation()
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 5.0  # Should complete within 5 seconds
```

## 🔄 Continuous Improvement

### Regular Maintenance Tasks

1. **Weekly**: Review test coverage and identify gaps
2. **Monthly**: Update test data and fixtures
3. **Quarterly**: Review and refactor test structure
4. **Release**: Ensure all tests pass and coverage meets requirements

### Test Metrics to Track

- **Coverage percentage** by module
- **Test execution time** trends
- **Test failure rates** over time
- **Flaky test** identification and resolution

For questions or suggestions about the testing strategy, please open an issue or start a discussion in the repository. 