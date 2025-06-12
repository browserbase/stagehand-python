"""Test ExtractHandler functionality for AI-powered data extraction"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from stagehand.handlers.extract_handler import ExtractHandler
from stagehand.types import ExtractOptions, ExtractResult
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
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        
        # Mock page content
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Sample content</body></html>")
        
        # Mock get_accessibility_tree
        with patch('stagehand.handlers.extract_handler.get_accessibility_tree') as mock_get_tree:
            mock_get_tree.return_value = {
                "simplified": "Sample accessibility tree content",
                "idToUrl": {}
            }
            
            # Mock extract_inference
            with patch('stagehand.handlers.extract_handler.extract_inference') as mock_extract_inference:
                mock_extract_inference.return_value = {
                    "data": {"extraction": "Sample extracted text from the page"},
                    "metadata": {"completed": True},
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "inference_time_ms": 1000
                }
                
                # Also need to mock _wait_for_settled_dom
                mock_stagehand_page._wait_for_settled_dom = AsyncMock()
                
                options = ExtractOptions(instruction="extract the main content")
                result = await handler.extract(options)
                
                assert isinstance(result, ExtractResult)
                # The handler should now properly populate the result with extracted data
                assert result.data is not None
                assert result.data == {"extraction": "Sample extracted text from the page"}
                
                # Verify the mocks were called
                mock_get_tree.assert_called_once()
                mock_extract_inference.assert_called_once()
    
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
        
        handler = ExtractHandler(mock_stagehand_page, mock_client, "")
        mock_stagehand_page._page.content = AsyncMock(return_value="<html><body>Product page</body></html>")
        
        # Mock get_accessibility_tree
        with patch('stagehand.handlers.extract_handler.get_accessibility_tree') as mock_get_tree:
            mock_get_tree.return_value = {
                "simplified": "Product page accessibility tree content",
                "idToUrl": {}
            }
            
            # Mock extract_inference
            with patch('stagehand.handlers.extract_handler.extract_inference') as mock_extract_inference:
                mock_extract_inference.return_value = {
                    "data": {
                        "name": "Wireless Mouse",
                        "price": 29.99,
                        "in_stock": True,
                        "tags": ["electronics", "computer", "accessories"]
                    },
                    "metadata": {"completed": True},
                    "prompt_tokens": 150,
                    "completion_tokens": 80,
                    "inference_time_ms": 1200
                }
                
                # Also need to mock _wait_for_settled_dom
                mock_stagehand_page._wait_for_settled_dom = AsyncMock()
                
                options = ExtractOptions(
                    instruction="extract product details",
                    schema_definition=ProductModel
                )
                
                result = await handler.extract(options, ProductModel)
                
                assert isinstance(result, ExtractResult)
                # The handler should now properly populate the result with a validated Pydantic model
                assert result.data is not None
                assert isinstance(result.data, ProductModel)
                assert result.data.name == "Wireless Mouse"
                assert result.data.price == 29.99
                assert result.data.in_stock is True
                assert result.data.tags == ["electronics", "computer", "accessories"]
                
                # Verify the mocks were called
                mock_get_tree.assert_called_once()
                mock_extract_inference.assert_called_once()
