import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ActResult, ExtractResult, ObserveResult


# Set up pytest-asyncio as the default
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test session.
    This helps with running async tests.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_stagehand_config():
    """Provide a mock StagehandConfig for testing"""
    return StagehandConfig(
        env="LOCAL",
        model_name="gpt-4o-mini",
        verbose=1,  # Quiet for tests
        api_key="test-api-key",
        project_id="test-project-id",
        dom_settle_timeout_ms=1000,
        self_heal=True,
        wait_for_captcha_solves=False,
        system_prompt="Test system prompt",
        use_api=False,
        experimental=False,
    )


@pytest.fixture
def mock_browserbase_config():
    """Provide a mock StagehandConfig for Browserbase testing"""
    return StagehandConfig(
        env="BROWSERBASE",
        model_name="gpt-4o",
        api_key="test-browserbase-api-key",
        project_id="test-browserbase-project-id",
        verbose=0,
        use_api=True,
        experimental=False,
    )


@pytest.fixture
def mock_playwright_page():
    """Provide a mock Playwright page"""
    page = MagicMock()
    page.evaluate = AsyncMock(return_value=True)
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.add_init_script = AsyncMock()
    page.keyboard = MagicMock()
    page.keyboard.press = AsyncMock()
    page.context = MagicMock()
    page.context.new_cdp_session = AsyncMock()
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Test Page")
    page.content = AsyncMock(return_value="<html><body>Test content</body></html>")
    return page


@pytest.fixture
def mock_stagehand_page(mock_playwright_page):
    """Provide a mock StagehandPage"""
    from stagehand.page import StagehandPage
    
    # Create a mock stagehand client
    mock_client = MagicMock()
    mock_client.use_api = False
    mock_client.env = "LOCAL"
    mock_client.logger = MagicMock()
    mock_client.logger.debug = MagicMock()
    mock_client.logger.warning = MagicMock()
    mock_client.logger.error = MagicMock()
    mock_client._get_lock_for_session = MagicMock(return_value=AsyncMock())
    mock_client._execute = AsyncMock()
    mock_client.update_metrics = MagicMock()
    
    stagehand_page = StagehandPage(mock_playwright_page, mock_client)
    
    # Mock CDP calls for accessibility tree
    async def mock_send_cdp(method, params=None):
        if method == "Accessibility.getFullAXTree":
            return {
                "nodes": [
                    {
                        "nodeId": "1",
                        "role": {"value": "button"},
                        "name": {"value": "Click me"},
                        "backendDOMNodeId": 1,
                        "childIds": [],
                        "properties": []
                    },
                    {
                        "nodeId": "2", 
                        "role": {"value": "textbox"},
                        "name": {"value": "Search input"},
                        "backendDOMNodeId": 2,
                        "childIds": [],
                        "properties": []
                    }
                ]
            }
        elif method == "DOM.resolveNode":
            # Create a mapping of element IDs to appropriate object IDs
            backend_node_id = params.get("backendNodeId", 1)
            return {
                "object": {
                    "objectId": f"test-object-id-{backend_node_id}"
                }
            }
        elif method == "Runtime.callFunctionOn":
            # Map object IDs to appropriate selectors based on the element ID
            object_id = params.get("objectId", "")
            
            # Extract backend_node_id from object_id
            if "test-object-id-" in object_id:
                backend_node_id = object_id.replace("test-object-id-", "")
                
                # Map specific element IDs to expected selectors for tests
                selector_mapping = {
                    "100": "//a[@id='home-link']",
                    "101": "//a[@id='about-link']", 
                    "102": "//a[@id='contact-link']",
                    "200": "//button[@id='visible-button']",
                    "300": "//input[@id='form-input']",
                    "400": "//div[@id='target-element']",
                    "501": "//button[@id='btn1']",
                    "600": "//button[@id='interactive-btn']",
                    "700": "//div[@id='positioned-element']",
                    "800": "//div[@id='highlighted-element']",
                    "900": "//div[@id='custom-model-element']",
                    "1000": "//input[@id='complex-element']",
                }
                
                xpath = selector_mapping.get(backend_node_id, "//div[@id='test']")
            else:
                xpath = "//div[@id='test']"
                
            return {
                "result": {
                    "value": xpath
                }
            }
        return {}
    
    stagehand_page.send_cdp = AsyncMock(side_effect=mock_send_cdp)
    
    # Mock get_cdp_client to return a mock CDP session
    mock_cdp_client = AsyncMock()
    
    # Set up the mock CDP client to handle Runtime.callFunctionOn properly
    async def mock_cdp_send(method, params=None):
        if method == "Runtime.callFunctionOn":
            # Map object IDs to appropriate selectors based on the element ID
            object_id = params.get("objectId", "")
            
            # Extract backend_node_id from object_id
            if "test-object-id-" in object_id:
                backend_node_id = object_id.replace("test-object-id-", "")
                
                # Map specific element IDs to expected selectors for tests
                selector_mapping = {
                    "100": "//a[@id='home-link']",
                    "101": "//a[@id='about-link']", 
                    "102": "//a[@id='contact-link']",
                    "200": "//button[@id='visible-button']",
                    "300": "//input[@id='form-input']",
                    "400": "//div[@id='target-element']",
                    "501": "//button[@id='btn1']",
                    "600": "//button[@id='interactive-btn']",
                    "700": "//div[@id='positioned-element']",
                    "800": "//div[@id='highlighted-element']",
                    "900": "//div[@id='custom-model-element']",
                    "1000": "//input[@id='complex-element']",
                }
                
                xpath = selector_mapping.get(backend_node_id, "//div[@id='test']")
            else:
                xpath = "//div[@id='test']"
                
            return {
                "result": {
                    "value": xpath
                }
            }
        return {"result": {"value": "//div[@id='test']"}}
    
    mock_cdp_client.send = AsyncMock(side_effect=mock_cdp_send)
    stagehand_page.get_cdp_client = AsyncMock(return_value=mock_cdp_client)
    
    # Mock ensure_injection and evaluate methods
    stagehand_page.ensure_injection = AsyncMock()
    stagehand_page.evaluate = AsyncMock(return_value=[])
    
    # Mock enable/disable CDP domain methods
    stagehand_page.enable_cdp_domain = AsyncMock()
    stagehand_page.disable_cdp_domain = AsyncMock()
    
    # Mock _wait_for_settled_dom to avoid asyncio.sleep issues
    stagehand_page._wait_for_settled_dom = AsyncMock()
    
    return stagehand_page


@pytest.fixture
def mock_stagehand_client(mock_stagehand_config):
    """Provide a mock Stagehand client for testing"""
    with patch('stagehand.main.async_playwright'), \
         patch('stagehand.main.LLMClient'), \
         patch('stagehand.main.StagehandLogger'):
        
        client = Stagehand(config=mock_stagehand_config)
        client._initialized = True  # Skip init for testing
        client._closed = False
        
        # Mock the essential components
        client.llm = MagicMock()
        client.llm.completion = AsyncMock()
        client.page = MagicMock()
        client.agent = MagicMock()
        client._client = MagicMock()
        client._execute = AsyncMock()
        client._get_lock_for_session = MagicMock(return_value=AsyncMock())
        
        return client


@pytest.fixture
def sample_html_content():
    """Provide sample HTML for testing"""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <header>
                <nav>
                    <button id="home-btn">Home</button>
                    <button id="about-btn">About</button>
                </nav>
            </header>
            <main>
                <h1>Welcome to Test Page</h1>
                <form id="search-form">
                    <input id="search-input" type="text" placeholder="Search...">
                    <button type="submit" id="search-submit">Search</button>
                </form>
                <div class="content">
                    <article class="post">
                        <h2>Sample Post Title</h2>
                        <p class="description">This is a sample post description for testing extraction.</p>
                        <span class="author">John Doe</span>
                        <span class="date">2024-01-15</span>
                    </article>
                    <article class="post">
                        <h2>Another Post</h2>
                        <p class="description">Another sample post for testing purposes.</p>
                        <span class="author">Jane Smith</span>
                        <span class="date">2024-01-16</span>
                    </article>
                </div>
            </main>
            <footer>
                <p>&copy; 2024 Test Company</p>
            </footer>
        </body>
    </html>
    """


@pytest.fixture
def sample_extraction_schemas():
    """Provide sample schemas for extraction testing"""
    return {
        "simple_text": {
            "type": "object",
            "properties": {
                "text": {"type": "string"}
            },
            "required": ["text"]
        },
        "post_data": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "author": {"type": "string"},
                "date": {"type": "string"}
            },
            "required": ["title", "description"]
        },
        "posts_list": {
            "type": "object",
            "properties": {
                "posts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "author": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["posts"]
        }
    }


@pytest.fixture
def mock_llm_responses():
    """Provide mock LLM responses for different scenarios"""
    return {
        "act_click_button": {
            "success": True,
            "message": "Successfully clicked the button",
            "action": "click on the button"
        },
        "act_fill_input": {
            "success": True,
            "message": "Successfully filled the input field",
            "action": "fill input with text"
        },
        "observe_button": [
            {
                "selector": "#search-submit",
                "description": "Search submit button",
                "backend_node_id": 123,
                "method": "click",
                "arguments": []
            }
        ],
        "observe_multiple": [
            {
                "selector": "#home-btn",
                "description": "Home navigation button",
                "backend_node_id": 124,
                "method": "click",
                "arguments": []
            },
            {
                "selector": "#about-btn", 
                "description": "About navigation button",
                "backend_node_id": 125,
                "method": "click",
                "arguments": []
            }
        ],
        "extract_title": {
            "title": "Sample Post Title"
        },
        "extract_posts": {
            "posts": [
                {
                    "title": "Sample Post Title",
                    "description": "This is a sample post description for testing extraction.",
                    "author": "John Doe"
                },
                {
                    "title": "Another Post",
                    "description": "Another sample post for testing purposes.",
                    "author": "Jane Smith"
                }
            ]
        }
    }


@pytest.fixture
def mock_dom_scripts():
    """Provide mock DOM scripts for testing injection"""
    return """
    window.getScrollableElementXpaths = function() {
        return ['//body', '//div[@class="content"]'];
    };
    
    window.getElementInfo = function(selector) {
        return {
            selector: selector,
            visible: true,
            bounds: { x: 0, y: 0, width: 100, height: 50 }
        };
    };
    """


@pytest.fixture
def temp_user_data_dir(tmp_path):
    """Provide a temporary user data directory for browser testing"""
    user_data_dir = tmp_path / "test_browser_data"
    user_data_dir.mkdir()
    return str(user_data_dir)


@pytest.fixture
def mock_browser_context():
    """Provide a mock browser context"""
    context = MagicMock()
    context.new_page = AsyncMock()
    context.close = AsyncMock()
    context.new_cdp_session = AsyncMock()
    return context


@pytest.fixture
def mock_browser():
    """Provide a mock browser"""
    browser = MagicMock()
    browser.new_context = AsyncMock()
    browser.close = AsyncMock()
    browser.contexts = []
    return browser


@pytest.fixture
def mock_playwright():
    """Provide a mock Playwright instance"""
    playwright = MagicMock()
    playwright.chromium = MagicMock()
    playwright.chromium.launch = AsyncMock()
    playwright.chromium.connect_over_cdp = AsyncMock()
    return playwright


@pytest.fixture
def environment_variables():
    """Provide mock environment variables for testing"""
    return {
        "BROWSERBASE_API_KEY": "test-browserbase-key",
        "BROWSERBASE_PROJECT_ID": "test-project-id",
        "MODEL_API_KEY": "test-model-key",
        "STAGEHAND_API_URL": "http://localhost:3000"
    }


@pytest.fixture
def mock_http_client():
    """Provide a mock HTTP client for API testing"""
    import httpx
    
    client = MagicMock(spec=httpx.AsyncClient)
    client.post = AsyncMock()
    client.get = AsyncMock() 
    client.close = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock()
    return client


class MockLLMResponse:
    """Mock LLM response object"""
    
    def __init__(self, content: str, data: Any = None, usage: Dict[str, int] = None):
        self.content = content
        self.data = data
        self.usage = MagicMock()
        self.usage.prompt_tokens = usage.get("prompt_tokens", 100) if usage else 100
        self.usage.completion_tokens = usage.get("completion_tokens", 50) if usage else 50
        self.usage.total_tokens = self.usage.prompt_tokens + self.usage.completion_tokens
        
        # Add choices for compatibility
        choice = MagicMock()
        choice.message = MagicMock()
        choice.message.content = content
        self.choices = [choice]


@pytest.fixture
def mock_llm_client():
    """Provide a mock LLM client"""
    from unittest.mock import MagicMock, AsyncMock
    
    client = MagicMock()
    client.completion = AsyncMock()
    client.api_key = "test-api-key"
    client.default_model = "gpt-4o-mini"
    
    return client


# Test data generators
class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def create_complex_dom():
        """Create complex DOM structure for testing"""
        return """
        <div class="app">
            <header class="navbar">
                <div class="nav-brand">
                    <img src="logo.png" alt="Logo">
                    <span>Test App</span>
                </div>
                <nav class="nav-menu">
                    <a href="/home" class="nav-link active">Home</a>
                    <a href="/products" class="nav-link">Products</a>
                    <a href="/contact" class="nav-link">Contact</a>
                </nav>
            </header>
            <main class="content">
                <section class="hero">
                    <h1>Welcome to Our Store</h1>
                    <p>Find the best products at great prices</p>
                    <button class="cta-button">Shop Now</button>
                </section>
                <section class="products-grid">
                    <div class="product-card" data-id="1">
                        <img src="product1.jpg" alt="Product 1">
                        <h3>Product 1</h3>
                        <p class="price">$99.99</p>
                        <button class="add-to-cart">Add to Cart</button>
                    </div>
                    <div class="product-card" data-id="2">
                        <img src="product2.jpg" alt="Product 2">
                        <h3>Product 2</h3>
                        <p class="price">$149.99</p>
                        <button class="add-to-cart">Add to Cart</button>
                    </div>
                </section>
            </main>
        </div>
        """
    
    @staticmethod
    def create_form_elements():
        """Create form elements for testing"""
        return """
        <form id="registration-form">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="country">Country</label>
                <select id="country" name="country">
                    <option value="us">United States</option>
                    <option value="ca">Canada</option>
                    <option value="uk">United Kingdom</option>
                </select>
            </div>
            <div class="form-group">
                <input type="checkbox" id="terms" name="terms" required>
                <label for="terms">I agree to the terms and conditions</label>
            </div>
            <button type="submit">Register</button>
        </form>
        """


# Custom assertion helpers
class AssertionHelpers:
    """Custom assertion helpers for Stagehand testing"""
    
    @staticmethod
    def assert_valid_selector(selector: str):
        """Assert selector is valid CSS/XPath"""
        import re
        
        # Basic CSS selector validation
        css_pattern = r'^[#.]?[\w\-\[\]="\':\s,>+~*()]+$'
        xpath_pattern = r'^\/\/.*$'
        
        assert (re.match(css_pattern, selector) or 
                re.match(xpath_pattern, selector)), f"Invalid selector: {selector}"
    
    @staticmethod
    def assert_schema_compliance(data: dict, schema: dict):
        """Assert data matches expected schema"""
        import jsonschema
        
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            pytest.fail(f"Data does not match schema: {e.message}")
    
    @staticmethod
    def assert_act_result_valid(result: ActResult):
        """Assert ActResult is valid"""
        assert isinstance(result, ActResult)
        assert isinstance(result.success, bool)
        assert isinstance(result.message, str)
        assert isinstance(result.action, str)
    
    @staticmethod
    def assert_observe_results_valid(results: list[ObserveResult]):
        """Assert ObserveResult list is valid"""
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, ObserveResult)
            assert isinstance(result.selector, str)
            assert isinstance(result.description, str)


@pytest.fixture
def assertion_helpers():
    """Provide assertion helpers"""
    return AssertionHelpers()


@pytest.fixture
def test_data_generator():
    """Provide test data generator"""
    return TestDataGenerator()
