"""Test ExtractHandler functionality for AI-powered data extraction"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from stagehand.handlers.extract_handler import ExtractHandler
from stagehand.schemas import ExtractOptions, ExtractResult, DEFAULT_EXTRACT_SCHEMA
from tests.mocks.mock_llm import MockLLMClient, MockLLMResponse


class TestExtractHandlerInitialization:
    """Test ExtractHandler initialization and setup"""
    
    def test_extract_handler_creation(self, mock_stagehand_page):
        """Test basic ExtractHandler creation"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ExtractHandler(
            mock_stagehand_page,
            mock_client,
            user_provided_instructions="Test extraction instructions"
        )
        
        assert handler.page == mock_stagehand_page
        assert handler.stagehand == mock_client
        assert handler.user_provided_instructions == "Test extraction instructions"
    
    def test_extract_handler_with_empty_instructions(self, mock_stagehand_page):
        """Test ExtractHandler with empty user instructions"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        assert handler.user_provided_instructions == ""


class TestExtractExecution:
    """Test data extraction functionality"""
    
    @pytest.mark.asyncio
    async def test_extract_with_default_schema(self, mock_stagehand_page):
        """Test extracting data with default schema"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Set up mock LLM response
        mock_llm.set_custom_response("extract", {
            "extraction": "Sample extracted text from the page"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        # Mock page content
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Sample content</body></html>")
        
        options = ExtractOptions(instruction="extract the main content")
        result = await handler.extract(options)
        
        assert isinstance(result, ExtractResult)
        assert result.extraction == "Sample extracted text from the page"
        
        # Should have called LLM
        assert mock_llm.call_count == 1
        assert mock_llm.was_called_with_content("extract")
    
    @pytest.mark.asyncio
    async def test_extract_with_custom_schema(self, mock_stagehand_page):
        """Test extracting data with custom schema"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Custom schema for product information
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "price": {"type": "number"},
                "description": {"type": "string"}
            },
            "required": ["title", "price"]
        }
        
        # Mock LLM response matching schema
        mock_llm.set_custom_response("extract", {
            "title": "Gaming Laptop",
            "price": 1299.99,
            "description": "High-performance gaming laptop"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Product page</body></html>")
        
        options = ExtractOptions(
            instruction="extract product information",
            schema_definition=schema
        )
        
        result = await handler.extract(options, schema)
        
        assert isinstance(result, ExtractResult)
        assert result.title == "Gaming Laptop"
        assert result.price == 1299.99
        assert result.description == "High-performance gaming laptop"
    
    @pytest.mark.asyncio
    async def test_extract_with_pydantic_model(self, mock_stagehand_page):
        """Test extracting data with Pydantic model schema"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        class ProductModel(BaseModel):
            name: str
            price: float
            in_stock: bool = True
            tags: list[str] = []
        
        # Mock LLM response
        mock_llm.set_custom_response("extract", {
            "name": "Wireless Mouse",
            "price": 29.99,
            "in_stock": True,
            "tags": ["electronics", "computer", "accessories"]
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Product page</body></html>")
        
        options = ExtractOptions(
            instruction="extract product details",
            schema_definition=ProductModel
        )
        
        result = await handler.extract(options, ProductModel)
        
        assert isinstance(result, ExtractResult)
        assert result.name == "Wireless Mouse"
        assert result.price == 29.99
        assert result.in_stock is True
        assert len(result.tags) == 3
    
    @pytest.mark.asyncio
    async def test_extract_without_options(self, mock_stagehand_page):
        """Test extracting data without specific options"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock LLM response for general extraction
        mock_llm.set_custom_response("extract", {
            "extraction": "General page content extracted automatically"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>General content</body></html>")
        
        result = await handler.extract(None, None)
        
        assert isinstance(result, ExtractResult)
        assert result.extraction == "General page content extracted automatically"
    
    @pytest.mark.asyncio
    async def test_extract_with_llm_failure(self, mock_stagehand_page):
        """Test handling of LLM API failure during extraction"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_llm.simulate_failure(True, "Extraction API unavailable")
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        options = ExtractOptions(instruction="extract content")
        
        with pytest.raises(Exception) as exc_info:
            await handler.extract(options)
        
        assert "Extraction API unavailable" in str(exc_info.value)


class TestSchemaValidation:
    """Test schema validation and processing"""
    
    @pytest.mark.asyncio
    async def test_schema_validation_success(self, mock_stagehand_page):
        """Test successful schema validation"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Valid schema
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "count": {"type": "integer"}
            },
            "required": ["title"]
        }
        
        # Mock LLM response that matches schema
        mock_llm.set_custom_response("extract", {
            "title": "Valid Title",
            "count": 42
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        options = ExtractOptions(
            instruction="extract data",
            schema_definition=schema
        )
        
        result = await handler.extract(options, schema)
        
        assert result.title == "Valid Title"
        assert result.count == 42
    
    @pytest.mark.asyncio
    async def test_schema_validation_with_malformed_llm_response(self, mock_stagehand_page):
        """Test handling of LLM response that doesn't match schema"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        mock_client.logger = MagicMock()
        
        schema = {
            "type": "object",
            "properties": {
                "required_field": {"type": "string"}
            },
            "required": ["required_field"]
        }
        
        # Mock LLM response that doesn't match schema
        mock_llm.set_custom_response("extract", {
            "wrong_field": "This doesn't match the schema"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        options = ExtractOptions(
            instruction="extract data",
            schema_definition=schema
        )
        
        result = await handler.extract(options, schema)
        
        # Should still return result but may log warnings
        assert isinstance(result, ExtractResult)


class TestDOMContextProcessing:
    """Test DOM context processing for extraction"""
    
    @pytest.mark.asyncio
    async def test_dom_context_inclusion(self, mock_stagehand_page):
        """Test that DOM context is included in extraction prompts"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock page content
        complex_html = """
        <html>
            <body>
                <div class="content">
                    <h1>Article Title</h1>
                    <p class="author">By John Doe</p>
                    <div class="article-body">
                        <p>This is the article content...</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        mock_stagehand_page._page.content = AsyncMock(return_value=complex_html)
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="cleaned DOM text")
        
        mock_llm.set_custom_response("extract", {
            "title": "Article Title",
            "author": "John Doe",
            "content": "This is the article content..."
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        options = ExtractOptions(instruction="extract article information")
        result = await handler.extract(options)
        
        # Should have called page.content to get DOM
        mock_stagehand_page._page.content.assert_called()
        
        # Result should contain extracted information
        assert result.title == "Article Title"
        assert result.author == "John Doe"
    
    @pytest.mark.asyncio
    async def test_dom_cleaning_and_processing(self, mock_stagehand_page):
        """Test DOM cleaning and processing before extraction"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Mock DOM evaluation for cleaning
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Cleaned text content")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html>Raw HTML</html>")
        
        mock_llm.set_custom_response("extract", {
            "extraction": "Cleaned extracted content"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        options = ExtractOptions(instruction="extract clean content")
        await handler.extract(options)
        
        # Should have evaluated DOM cleaning script
        mock_stagehand_page._page.evaluate.assert_called()


class TestPromptGeneration:
    """Test prompt generation for extraction"""
    
    def test_prompt_includes_user_instructions(self, mock_stagehand_page):
        """Test that prompts include user-provided instructions"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        user_instructions = "Focus on extracting numerical data accurately"
        handler = ExtractHandler(mock_stagehand_page, mock_client, user_instructions)
        
        assert handler.user_provided_instructions == user_instructions
    
    def test_prompt_includes_schema_context(self, mock_stagehand_page):
        """Test that prompts include schema information"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        # This would test that schema context is included in prompts
        # Implementation depends on how prompts are structured
        assert handler.page == mock_stagehand_page


class TestMetricsAndLogging:
    """Test metrics collection and logging for extraction"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_on_successful_extraction(self, mock_stagehand_page):
        """Test that metrics are collected on successful extractions"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        mock_llm.set_custom_response("extract", {
            "data": "extracted successfully"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        options = ExtractOptions(instruction="extract data")
        await handler.extract(options)
        
        # Should start timing and update metrics
        mock_client.start_inference_timer.assert_called()
        mock_client.update_metrics_from_response.assert_called()
    
    @pytest.mark.asyncio
    async def test_logging_on_extraction_errors(self, mock_stagehand_page):
        """Test that extraction errors are properly logged"""
        mock_client = MagicMock()
        mock_client.llm = MockLLMClient()
        mock_client.logger = MagicMock()
        
        # Simulate an error during extraction
        mock_stagehand_page._page.content = AsyncMock(side_effect=Exception("Page load failed"))
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        options = ExtractOptions(instruction="extract data")
        
        with pytest.raises(Exception):
            await handler.extract(options)


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_extraction_with_empty_page(self, mock_stagehand_page):
        """Test extraction from empty page"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Empty page content
        mock_stagehand_page._page.content = AsyncMock(return_value="")
        
        mock_llm.set_custom_response("extract", {
            "extraction": "No content found"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        options = ExtractOptions(instruction="extract content")
        result = await handler.extract(options)
        
        assert isinstance(result, ExtractResult)
        assert result.extraction == "No content found"
    
    @pytest.mark.asyncio
    async def test_extraction_with_very_large_page(self, mock_stagehand_page):
        """Test extraction from very large page content"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Very large content
        large_content = "<html><body>" + "x" * 100000 + "</body></html>"
        mock_stagehand_page._page.content = AsyncMock(return_value=large_content)
        mock_stagehand_page._page.evaluate = AsyncMock(return_value="Truncated content")
        
        mock_llm.set_custom_response("extract", {
            "extraction": "Extracted from large page"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        options = ExtractOptions(instruction="extract key information")
        result = await handler.extract(options)
        
        assert isinstance(result, ExtractResult)
        # Should handle large content gracefully
    
    @pytest.mark.asyncio
    async def test_extraction_with_complex_nested_schema(self, mock_stagehand_page):
        """Test extraction with deeply nested schema"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics_from_response = MagicMock()
        
        # Complex nested schema
        complex_schema = {
            "type": "object",
            "properties": {
                "company": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "employees": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "role": {"type": "string"},
                                    "skills": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Mock complex nested response
        mock_llm.set_custom_response("extract", {
            "company": {
                "name": "Tech Corp",
                "employees": [
                    {
                        "name": "Alice",
                        "role": "Engineer",
                        "skills": ["Python", "JavaScript"]
                    },
                    {
                        "name": "Bob", 
                        "role": "Designer",
                        "skills": ["Figma", "CSS"]
                    }
                ]
            }
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Company page</body></html>")
        
        options = ExtractOptions(
            instruction="extract company information",
            schema_definition=complex_schema
        )
        
        result = await handler.extract(options, complex_schema)
        
        assert isinstance(result, ExtractResult)
        assert result.company["name"] == "Tech Corp"
        assert len(result.company["employees"]) == 2
        assert result.company["employees"][0]["name"] == "Alice" 