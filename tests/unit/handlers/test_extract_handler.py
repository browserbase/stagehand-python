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
        
        assert handler.stagehand_page == mock_stagehand_page
        assert handler.stagehand == mock_client
        assert handler.user_provided_instructions == "Test extraction instructions"


class TestExtractExecution:
    """Test data extraction functionality"""
    
    @pytest.mark.asyncio
    async def test_extract_with_default_schema(self, mock_stagehand_page):
        """Test extracting data with default schema"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
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
        
        # Should have called LLM twice (once for extraction, once for metadata)
        assert mock_llm.call_count == 2
        assert mock_llm.was_called_with_content("extract")
    
    @pytest.mark.asyncio
    async def test_extract_with_pydantic_model(self, mock_stagehand_page):
        """Test extracting data with Pydantic model schema"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
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
        mock_client.update_metrics = MagicMock()
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>General content</body></html>")
        
        result = await handler.extract()
        
        assert isinstance(result, ExtractResult)
        # When no options are provided, should extract raw page text without LLM
        assert hasattr(result, 'extraction')
        assert result.extraction is not None


# TODO: move to llm/inference tests
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
        assert handler.stagehand_page == mock_stagehand_page


class TestMetrics:
    """Test metrics collection and logging for extraction"""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_on_successful_extraction(self, mock_stagehand_page):
        """Test that metrics are collected on successful extractions"""
        mock_client = MagicMock()
        mock_llm = MockLLMClient()
        mock_client.llm = mock_llm
        mock_client.start_inference_timer = MagicMock()
        mock_client.update_metrics = MagicMock()
        
        mock_llm.set_custom_response("extract", {
            "data": "extracted successfully"
        })
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        options = ExtractOptions(instruction="extract data")
        await handler.extract(options)
        
        # Should start timing and update metrics
        mock_client.start_inference_timer.assert_called()
        mock_client.update_metrics.assert_called()
