from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, TYPE_CHECKING

import pytest

from stagehand import StagehandPage
from stagehand.a11y import get_accessibility_tree

if TYPE_CHECKING:
    from stagehand.logging import StagehandLogger
else:
    StagehandLogger = Any

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def mock_stagehand_logger():
    with patch('stagehand.a11y.utils.StagehandLogger'):
        mock_logger = MagicMock()
        yield mock_logger


class TestGetAccessibilityTree:
    async def test_empty_tree_result(self, mock_stagehand_page: StagehandPage, mock_stagehand_logger: StagehandLogger):
        mock_stagehand_page.send_cdp = AsyncMock(return_value={"nodes": []})
        actual = await get_accessibility_tree(mock_stagehand_page, mock_stagehand_logger)
        assert actual["simplified"] == ""
        assert actual["tree"] == []
        assert actual["iframes"] == []
        assert actual["idToUrl"] == {}

    async def test_another(self, mock_stagehand_page: StagehandPage, mock_stagehand_logger: StagehandLogger):
        mock_stagehand_page.send_cdp = AsyncMock(return_value={"nodes": [
            {
                "backendNodeId": "",
                "role": "",
                "value": {},
            },

        ]})
        actual = await get_accessibility_tree(mock_stagehand_page, mock_stagehand_logger)
        assert actual["simplified"] == ""
        assert actual["tree"] == []
        assert actual["iframes"] == []
        assert actual["idToUrl"] == {}

class TestFindScrollableElementIds:
    async def test_something(self):
        raise NotImplementedError
