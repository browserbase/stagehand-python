"""Test CUAHandler functionality for Computer Use Agent action execution"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from stagehand.handlers.cua_handler import CUAHandler
from stagehand.types.agent import TypeAction, AgentAction, ClickAction


class TestCUAHandlerInitialization:
    """Test CUAHandler initialization and setup"""

    def test_cua_handler_creation(self):
        """Test basic CUAHandler creation"""
        mock_stagehand = MagicMock()
        mock_page = MagicMock()
        mock_logger = MagicMock()

        handler = CUAHandler(
            stagehand=mock_stagehand,
            page=mock_page,
            logger=mock_logger,
        )

        assert handler.stagehand == mock_stagehand
        assert handler.page == mock_page
        assert handler.logger == mock_logger


class TestTypeActionClearBeforeTyping:
    """Test clear_before_typing functionality in type actions"""

    @pytest.fixture
    def cua_handler(self):
        """Create a CUAHandler with mocked dependencies"""
        mock_stagehand = MagicMock()
        mock_page = MagicMock()
        mock_page.mouse = MagicMock()
        mock_page.mouse.click = AsyncMock()
        mock_page.keyboard = MagicMock()
        mock_page.keyboard.type = AsyncMock()
        mock_page.keyboard.press = AsyncMock()
        mock_page.url = "https://example.com"
        mock_logger = MagicMock()

        handler = CUAHandler(
            stagehand=mock_stagehand,
            page=mock_page,
            logger=mock_logger,
        )
        # Mock internal methods
        handler._update_cursor_position = AsyncMock()
        handler.handle_page_navigation = AsyncMock()

        return handler

    @pytest.mark.asyncio
    async def test_type_without_clear_uses_single_click(self, cua_handler):
        """Test that typing without clear_before_typing uses single click"""
        type_action = TypeAction(
            type="type",
            text="hello world",
            x=100,
            y=200,
            clear_before_typing=False,
        )
        agent_action = AgentAction(
            action_type="type",
            action=type_action,
        )

        result = await cua_handler.perform_action(agent_action)

        assert result["success"] is True
        # Should have called single click (click_count defaults to 1)
        cua_handler.page.mouse.click.assert_called_once_with(100, 200)
        cua_handler.page.keyboard.type.assert_called_once_with("hello world")

    @pytest.mark.asyncio
    async def test_type_with_clear_uses_triple_click(self, cua_handler):
        """Test that typing with clear_before_typing=True uses triple click to select all"""
        type_action = TypeAction(
            type="type",
            text="new text",
            x=100,
            y=200,
            clear_before_typing=True,
        )
        agent_action = AgentAction(
            action_type="type",
            action=type_action,
        )

        result = await cua_handler.perform_action(agent_action)

        assert result["success"] is True
        # Should have called triple click to select all text
        cua_handler.page.mouse.click.assert_called_once_with(100, 200, click_count=3)
        cua_handler.page.keyboard.type.assert_called_once_with("new text")

    @pytest.mark.asyncio
    async def test_type_with_clear_no_coordinates_uses_keyboard_shortcuts(self, cua_handler):
        """Test that clear_before_typing without coordinates falls back to keyboard shortcuts"""
        type_action = TypeAction(
            type="type",
            text="new text",
            x=None,
            y=None,
            clear_before_typing=True,
        )
        agent_action = AgentAction(
            action_type="type",
            action=type_action,
        )

        result = await cua_handler.perform_action(agent_action)

        assert result["success"] is True
        # Should have called keyboard shortcuts for select all
        calls = cua_handler.page.keyboard.press.call_args_list
        key_calls = [call[0][0] for call in calls]
        assert "Meta+a" in key_calls or "Control+a" in key_calls
        assert "Backspace" in key_calls
        cua_handler.page.keyboard.type.assert_called_once_with("new text")

    @pytest.mark.asyncio
    async def test_type_default_clear_before_typing_is_false(self, cua_handler):
        """Test that clear_before_typing defaults to False"""
        type_action = TypeAction(
            type="type",
            text="hello",
            x=100,
            y=200,
            # clear_before_typing not specified, should default to False
        )
        agent_action = AgentAction(
            action_type="type",
            action=type_action,
        )

        result = await cua_handler.perform_action(agent_action)

        assert result["success"] is True
        # Should use single click (not triple click)
        cua_handler.page.mouse.click.assert_called_once_with(100, 200)

    @pytest.mark.asyncio
    async def test_type_with_press_enter_after(self, cua_handler):
        """Test that press_enter_after works with clear_before_typing"""
        type_action = TypeAction(
            type="type",
            text="search query",
            x=100,
            y=200,
            clear_before_typing=True,
            press_enter_after=True,
        )
        agent_action = AgentAction(
            action_type="type",
            action=type_action,
        )

        result = await cua_handler.perform_action(agent_action)

        assert result["success"] is True
        # Should have triple-clicked, typed, then pressed Enter
        cua_handler.page.mouse.click.assert_called_once_with(100, 200, click_count=3)
        cua_handler.page.keyboard.type.assert_called_once_with("search query")
        # Check that Enter was pressed
        enter_calls = [
            call for call in cua_handler.page.keyboard.press.call_args_list
            if call[0][0] == "Enter"
        ]
        assert len(enter_calls) == 1


class TestTypeActionModel:
    """Test TypeAction Pydantic model"""

    def test_type_action_has_clear_before_typing_field(self):
        """Test that TypeAction model has clear_before_typing field"""
        action = TypeAction(
            type="type",
            text="test",
            clear_before_typing=True,
        )
        assert action.clear_before_typing is True

    def test_type_action_clear_before_typing_defaults_to_false(self):
        """Test that clear_before_typing defaults to False"""
        action = TypeAction(
            type="type",
            text="test",
        )
        assert action.clear_before_typing is False

    def test_type_action_with_all_fields(self):
        """Test TypeAction with all fields populated"""
        action = TypeAction(
            type="type",
            text="hello@example.com",
            x=150,
            y=250,
            press_enter_after=True,
            clear_before_typing=True,
        )
        assert action.type == "type"
        assert action.text == "hello@example.com"
        assert action.x == 150
        assert action.y == 250
        assert action.press_enter_after is True
        assert action.clear_before_typing is True
