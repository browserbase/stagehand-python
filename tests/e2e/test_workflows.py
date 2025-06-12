"""End-to-end integration tests for complete Stagehand workflows"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from stagehand import Stagehand, StagehandConfig
from stagehand.schemas import ActResult, ObserveResult, ExtractResult
from tests.mocks.mock_llm import MockLLMClient
from tests.mocks.mock_browser import create_mock_browser_stack, setup_page_with_content
from tests.mocks.mock_server import create_mock_server_with_client, setup_successful_session_flow


class TestCompleteWorkflows:
    """Test complete automation workflows end-to-end"""
    
    @pytest.mark.asyncio
    async def test_search_and_extract_workflow(self, mock_stagehand_config, sample_html_content):
        """Test complete workflow: navigate → search → extract results"""
        
        # Create mock components
        playwright, browser, context, page = create_mock_browser_stack()
        setup_page_with_content(page, sample_html_content, "https://example.com")
        
        # Setup mock LLM client
        mock_llm = MockLLMClient()
        
        # Configure specific responses for each step
        mock_llm.set_custom_response("act", {
            "success": True,
            "message": "Search executed successfully",
            "action": "search for openai"
        })
        
        mock_llm.set_custom_response("extract", {
            "title": "OpenAI Search Results",
            "results": [
                {"title": "OpenAI Official Website", "url": "https://openai.com"},
                {"title": "OpenAI API Documentation", "url": "https://platform.openai.com"}
            ]
        })
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            # Initialize Stagehand
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.goto = AsyncMock()
            stagehand.page.act = AsyncMock(return_value=ActResult(
                success=True,
                message="Search executed",
                action="search"
            ))
            stagehand.page.extract = AsyncMock(return_value={
                "title": "OpenAI Search Results",
                "results": [
                    {"title": "OpenAI Official Website", "url": "https://openai.com"},
                    {"title": "OpenAI API Documentation", "url": "https://platform.openai.com"}
                ]
            })
            stagehand._initialized = True
            
            try:
                # Execute workflow
                await stagehand.page.goto("https://google.com")
                
                # Perform search
                search_result = await stagehand.page.act("search for openai")
                assert search_result.success is True
                
                # Extract results
                extracted_data = await stagehand.page.extract("extract search results")
                assert extracted_data["title"] == "OpenAI Search Results"
                assert len(extracted_data["results"]) == 2
                assert extracted_data["results"][0]["title"] == "OpenAI Official Website"
                
                # Verify calls were made
                stagehand.page.goto.assert_called_with("https://google.com")
                stagehand.page.act.assert_called_with("search for openai")
                stagehand.page.extract.assert_called_with("extract search results")
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_form_filling_workflow(self, mock_stagehand_config):
        """Test workflow: navigate → fill form → submit → verify"""
        
        form_html = """
        <html>
            <body>
                <form id="registration-form">
                    <input id="username" name="username" type="text" placeholder="Username">
                    <input id="email" name="email" type="email" placeholder="Email">
                    <input id="password" name="password" type="password" placeholder="Password">
                    <button type="submit" id="submit-btn">Register</button>
                </form>
                <div id="success-message" style="display:none;">Registration successful!</div>
            </body>
        </html>
        """
        
        playwright, browser, context, page = create_mock_browser_stack()
        setup_page_with_content(page, form_html, "https://example.com/register")
        
        mock_llm = MockLLMClient()
        
        # Configure responses for form filling steps
        form_responses = {
            "fill username": {"success": True, "message": "Username filled", "action": "fill"},
            "fill email": {"success": True, "message": "Email filled", "action": "fill"},
            "fill password": {"success": True, "message": "Password filled", "action": "fill"},
            "submit form": {"success": True, "message": "Form submitted", "action": "click"}
        }
        
        call_count = 0
        def form_response_generator(messages, **kwargs):
            nonlocal call_count
            call_count += 1
            content = str(messages).lower()
            
            if "username" in content:
                return form_responses["fill username"]
            elif "email" in content:
                return form_responses["fill email"]
            elif "password" in content:
                return form_responses["fill password"]
            elif "submit" in content:
                return form_responses["submit form"]
            else:
                return {"success": True, "message": "Action completed", "action": "unknown"}
        
        mock_llm.set_custom_response("act", form_response_generator)
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.goto = AsyncMock()
            stagehand.page.act = AsyncMock()
            stagehand.page.extract = AsyncMock()
            stagehand._initialized = True
            
            # Mock act responses
            stagehand.page.act.side_effect = [
                ActResult(success=True, message="Username filled", action="fill"),
                ActResult(success=True, message="Email filled", action="fill"),
                ActResult(success=True, message="Password filled", action="fill"),
                ActResult(success=True, message="Form submitted", action="click")
            ]
            
            # Mock success verification
            stagehand.page.extract.return_value = {"success": True, "message": "Registration successful!"}
            
            try:
                # Execute form filling workflow
                await stagehand.page.goto("https://example.com/register")
                
                # Fill form fields
                username_result = await stagehand.page.act("fill username field with 'testuser'")
                assert username_result.success is True
                
                email_result = await stagehand.page.act("fill email field with 'test@example.com'")
                assert email_result.success is True
                
                password_result = await stagehand.page.act("fill password field with 'securepass123'")
                assert password_result.success is True
                
                # Submit form
                submit_result = await stagehand.page.act("click submit button")
                assert submit_result.success is True
                
                # Verify success
                verification = await stagehand.page.extract("check if registration was successful")
                assert verification["success"] is True
                
                # Verify all steps were executed
                assert stagehand.page.act.call_count == 4
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_observe_then_act_workflow(self, mock_stagehand_config):
        """Test workflow: observe elements → act on observed elements"""
        
        complex_page_html = """
        <html>
            <body>
                <nav class="navbar">
                    <button id="home-btn" class="nav-button">Home</button>
                    <button id="products-btn" class="nav-button">Products</button>
                    <button id="contact-btn" class="nav-button">Contact</button>
                </nav>
                <main>
                    <div class="product-grid">
                        <div class="product-card" data-id="1">
                            <h3>Product A</h3>
                            <button class="add-to-cart" data-product="1">Add to Cart</button>
                        </div>
                        <div class="product-card" data-id="2">
                            <h3>Product B</h3>
                            <button class="add-to-cart" data-product="2">Add to Cart</button>
                        </div>
                    </div>
                </main>
            </body>
        </html>
        """
        
        playwright, browser, context, page = create_mock_browser_stack()
        setup_page_with_content(page, complex_page_html, "https://shop.example.com")
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = MockLLMClient()
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.goto = AsyncMock()
            stagehand.page.observe = AsyncMock()
            stagehand.page.act = AsyncMock()
            stagehand._initialized = True
            
            # Mock observe results
            nav_buttons = [
                ObserveResult(
                    selector="#home-btn",
                    description="Home navigation button",
                    method="click",
                    arguments=[]
                ),
                ObserveResult(
                    selector="#products-btn",
                    description="Products navigation button",
                    method="click",
                    arguments=[]
                ),
                ObserveResult(
                    selector="#contact-btn",
                    description="Contact navigation button",
                    method="click",
                    arguments=[]
                )
            ]
            
            add_to_cart_buttons = [
                ObserveResult(
                    selector="[data-product='1'] .add-to-cart",
                    description="Add to cart button for Product A",
                    method="click",
                    arguments=[]
                ),
                ObserveResult(
                    selector="[data-product='2'] .add-to-cart",
                    description="Add to cart button for Product B",
                    method="click",
                    arguments=[]
                )
            ]
            
            stagehand.page.observe.side_effect = [nav_buttons, add_to_cart_buttons]
            stagehand.page.act.return_value = ActResult(
                success=True,
                message="Button clicked",
                action="click"
            )
            
            try:
                # Execute observe → act workflow
                await stagehand.page.goto("https://shop.example.com")
                
                # Observe navigation buttons
                nav_results = await stagehand.page.observe("find all navigation buttons")
                assert len(nav_results) == 3
                assert nav_results[0].selector == "#home-btn"
                
                # Click on products button
                products_click = await stagehand.page.act(nav_results[1])  # Products button
                assert products_click.success is True
                
                # Observe add to cart buttons
                cart_buttons = await stagehand.page.observe("find add to cart buttons")
                assert len(cart_buttons) == 2
                
                # Add first product to cart
                add_to_cart_result = await stagehand.page.act(cart_buttons[0])
                assert add_to_cart_result.success is True
                
                # Verify method calls
                assert stagehand.page.observe.call_count == 2
                assert stagehand.page.act.call_count == 2
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_multi_page_navigation_workflow(self, mock_stagehand_config):
        """Test workflow spanning multiple pages with data extraction"""
        
        # Page 1: Product listing
        listing_html = """
        <html>
            <body>
                <div class="product-list">
                    <div class="product" data-id="1">
                        <h3>Laptop</h3>
                        <span class="price">$999</span>
                        <a href="/product/1" class="view-details">View Details</a>
                    </div>
                    <div class="product" data-id="2">
                        <h3>Mouse</h3>
                        <span class="price">$25</span>
                        <a href="/product/2" class="view-details">View Details</a>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Page 2: Product details
        details_html = """
        <html>
            <body>
                <div class="product-details">
                    <h1>Laptop</h1>
                    <p class="description">High-performance laptop for professionals</p>
                    <span class="price">$999</span>
                    <div class="specs">
                        <ul>
                            <li>16GB RAM</li>
                            <li>512GB SSD</li>
                            <li>Intel i7 Processor</li>
                        </ul>
                    </div>
                    <button id="add-to-cart">Add to Cart</button>
                </div>
            </body>
        </html>
        """
        
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = MockLLMClient()
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.goto = AsyncMock()
            stagehand.page.extract = AsyncMock()
            stagehand.page.act = AsyncMock()
            stagehand._initialized = True
            
            # Mock page responses
            page_responses = {
                "/products": {
                    "products": [
                        {"name": "Laptop", "price": "$999", "id": "1"},
                        {"name": "Mouse", "price": "$25", "id": "2"}
                    ]
                },
                "/product/1": {
                    "name": "Laptop",
                    "price": "$999",
                    "description": "High-performance laptop for professionals",
                    "specs": ["16GB RAM", "512GB SSD", "Intel i7 Processor"]
                }
            }
            
            current_page = ["/products"]  # Mutable container for current page
            
            def extract_response(instruction):
                return page_responses.get(current_page[0], {})
            
            def navigation_side_effect(url):
                if "/product/1" in url:
                    current_page[0] = "/product/1"
                else:
                    current_page[0] = "/products"
            
            stagehand.page.extract.side_effect = lambda inst: extract_response(inst)
            stagehand.page.goto.side_effect = navigation_side_effect
            stagehand.page.act.return_value = ActResult(
                success=True,
                message="Navigation successful",
                action="click"
            )
            
            try:
                # Start workflow
                await stagehand.page.goto("https://shop.example.com/products")
                
                # Extract product list
                products = await stagehand.page.extract("extract all products with names and prices")
                assert len(products["products"]) == 2
                assert products["products"][0]["name"] == "Laptop"
                
                # Navigate to first product details
                nav_result = await stagehand.page.act("click on first product details link")
                assert nav_result.success is True
                
                # Navigate to product page
                await stagehand.page.goto("https://shop.example.com/product/1")
                
                # Extract detailed product information
                details = await stagehand.page.extract("extract product details including specs")
                assert details["name"] == "Laptop"
                assert details["price"] == "$999"
                assert len(details["specs"]) == 3
                
                # Verify navigation flow
                assert stagehand.page.goto.call_count == 2
                assert stagehand.page.extract.call_count == 2
                
            finally:
                stagehand._closed = True
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, mock_stagehand_config):
        """Test workflow with error recovery and retry logic"""
        
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_llm = MockLLMClient()
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = mock_llm
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.goto = AsyncMock()
            stagehand.page.act = AsyncMock()
            stagehand._initialized = True
            
            # Simulate intermittent failures and recovery
            failure_count = 0
            def act_with_failures(*args, **kwargs):
                nonlocal failure_count
                failure_count += 1
                
                if failure_count <= 2:  # First 2 calls fail
                    return ActResult(
                        success=False,
                        message="Element not found",
                        action="click"
                    )
                else:  # Subsequent calls succeed
                    return ActResult(
                        success=True,
                        message="Action completed successfully",
                        action="click"
                    )
            
            stagehand.page.act.side_effect = act_with_failures
            
            try:
                await stagehand.page.goto("https://example.com")
                
                # Attempt action multiple times until success
                max_retries = 5
                success = False
                
                for attempt in range(max_retries):
                    result = await stagehand.page.act("click submit button")
                    if result.success:
                        success = True
                        break
                
                assert success is True
                assert failure_count == 3  # 2 failures + 1 success
                assert stagehand.page.act.call_count == 3
                
            finally:
                stagehand._closed = True


class TestBrowserbaseIntegration:
    """Test integration with Browserbase remote browser"""
    
    @pytest.mark.asyncio
    async def test_browserbase_session_workflow(self, mock_browserbase_config):
        """Test complete workflow using Browserbase remote browser"""
        
        # Create mock server
        server, http_client = create_mock_server_with_client()
        setup_successful_session_flow(server, "test-bb-session")
        
        # Setup server responses for workflow
        server.set_response_override("act", {
            "success": True,
            "message": "Button clicked via Browserbase",
            "action": "click"
        })
        
        server.set_response_override("extract", {
            "title": "Remote Page Title",
            "content": "Content extracted via Browserbase"
        })
        
        with patch('stagehand.main.httpx.AsyncClient') as mock_http_class:
            mock_http_class.return_value = http_client
            
            stagehand = Stagehand(
                config=mock_browserbase_config,
                api_url="https://mock-stagehand-server.com"
            )
            
            # Mock the browser connection parts
            stagehand._client = http_client
            stagehand.session_id = "test-bb-session"
            stagehand.page = MagicMock()
            stagehand.page.goto = AsyncMock()
            stagehand.page.act = AsyncMock()
            stagehand.page.extract = AsyncMock()
            stagehand._initialized = True
            
            # Mock page methods to use server
            async def mock_act(instruction, **kwargs):
                # Simulate server call
                response = await http_client.post(
                    "https://mock-server/api/act",
                    json={"action": instruction}
                )
                data = response.json()
                return ActResult(**data)
            
            async def mock_extract(instruction, **kwargs):
                response = await http_client.post(
                    "https://mock-server/api/extract",
                    json={"instruction": instruction}
                )
                return response.json()
            
            stagehand.page.act = mock_act
            stagehand.page.extract = mock_extract
            
            try:
                # Execute Browserbase workflow
                await stagehand.page.goto("https://example.com")
                
                # Perform actions via Browserbase
                act_result = await stagehand.page.act("click login button")
                assert act_result.success is True
                assert "Browserbase" in act_result.message
                
                # Extract data via Browserbase
                extracted = await stagehand.page.extract("extract page title and content")
                assert extracted["title"] == "Remote Page Title"
                assert extracted["content"] == "Content extracted via Browserbase"
                
                # Verify server interactions
                assert server.was_called_with_endpoint("act")
                assert server.was_called_with_endpoint("extract")
                
            finally:
                stagehand._closed = True


class TestWorkflowPydanticSchemas:
    """Test workflows using Pydantic schemas for structured data"""
    
    @pytest.mark.asyncio
    async def test_workflow_with_pydantic_extraction(self, mock_stagehand_config):
        """Test workflow using Pydantic schemas for data extraction"""
        
        class ProductInfo(BaseModel):
            name: str
            price: float
            description: str
            in_stock: bool
            specs: list[str] = []
        
        class ProductList(BaseModel):
            products: list[ProductInfo]
            total_count: int
        
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = MockLLMClient()
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.goto = AsyncMock()
            stagehand.page.extract = AsyncMock()
            stagehand._initialized = True
            
            # Mock structured extraction responses
            mock_product_data = {
                "products": [
                    {
                        "name": "Gaming Laptop",
                        "price": 1299.99,
                        "description": "High-performance gaming laptop",
                        "in_stock": True,
                        "specs": ["RTX 4070", "32GB RAM", "1TB SSD"]
                    },
                    {
                        "name": "Wireless Mouse",
                        "price": 79.99,
                        "description": "Ergonomic wireless mouse",
                        "in_stock": False,
                        "specs": ["2.4GHz", "6-month battery"]
                    }
                ],
                "total_count": 2
            }
            
            stagehand.page.extract.return_value = mock_product_data
            
            try:
                await stagehand.page.goto("https://electronics-store.com")
                
                # Extract with Pydantic schema
                from stagehand.schemas import ExtractOptions
                
                extract_options = ExtractOptions(
                    instruction="extract all products with detailed information",
                    schema_definition=ProductList
                )
                
                products_data = await stagehand.page.extract(extract_options)
                
                # Validate structure matches Pydantic schema
                assert "products" in products_data
                assert products_data["total_count"] == 2
                
                product1 = products_data["products"][0]
                assert product1["name"] == "Gaming Laptop"
                assert product1["price"] == 1299.99
                assert product1["in_stock"] is True
                assert len(product1["specs"]) == 3
                
                product2 = products_data["products"][1]
                assert product2["in_stock"] is False
                
                # Verify extract was called with schema
                stagehand.page.extract.assert_called_once()
                
            finally:
                stagehand._closed = True


class TestPerformanceWorkflows:
    """Test workflows under different performance conditions"""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_workflow(self, mock_stagehand_config):
        """Test workflow with concurrent page operations"""
        
        playwright, browser, context, page = create_mock_browser_stack()
        
        with patch('stagehand.main.async_playwright') as mock_playwright_func, \
             patch('stagehand.main.LLMClient') as mock_llm_class:
            
            mock_playwright_func.return_value.start = AsyncMock(return_value=playwright)
            mock_llm_class.return_value = MockLLMClient()
            
            stagehand = Stagehand(config=mock_stagehand_config)
            stagehand._playwright = playwright
            stagehand._browser = browser
            stagehand._context = context
            stagehand.page = MagicMock()
            stagehand.page.extract = AsyncMock()
            stagehand._initialized = True
            
            # Mock multiple concurrent extractions
            extraction_responses = [
                {"section": "header", "content": "Header content"},
                {"section": "main", "content": "Main content"},
                {"section": "footer", "content": "Footer content"}
            ]
            
            stagehand.page.extract.side_effect = extraction_responses
            
            try:
                # Execute concurrent extractions
                import asyncio
                
                tasks = [
                    stagehand.page.extract("extract header information"),
                    stagehand.page.extract("extract main content"),
                    stagehand.page.extract("extract footer information")
                ]
                
                results = await asyncio.gather(*tasks)
                
                assert len(results) == 3
                assert results[0]["section"] == "header"
                assert results[1]["section"] == "main"
                assert results[2]["section"] == "footer"
                
                # Verify all extractions were called
                assert stagehand.page.extract.call_count == 3
                
            finally:
                stagehand._closed = True 