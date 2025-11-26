from typing import Any
from unittest.mock import MagicMock, patch
import json

import pytest

from stagehand import StagehandPage
from stagehand.a11y import get_accessibility_tree
from stagehand.logging import StagehandLogger

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def mock_stagehand_logger():
    with patch('stagehand.a11y.utils.StagehandLogger'):
        mock_logger = MagicMock()
        yield mock_logger


@pytest.fixture
def load_ax_tree(pytestconfig):
    def loader(name: str) -> dict[str, Any]:
        fixture = pytestconfig.rootpath / "tests/fixtures/ax_trees" / name
        return json.loads(fixture.read_text())
    return loader



@pytest.fixture
def mock_send_cdp(mock_stagehand_page):
    def mock_send_cdp_factory(*, ax_tree, backend_nodes=None, tag_names=None):
        backend_nodes = backend_nodes or {}
        tag_names = tag_names or {}

        async def mocked_send_cdp(method, params=None):
            params = params or {}
            if method == "Accessibility.getFullAXTree":
                return ax_tree
            elif method == "DOM.resolveNode":
                # Create a mapping of element IDs to appropriate object IDs
                backend_node_id = params.get("backendNodeId", 1)
                return backend_nodes.get(backend_node_id, {})
            elif method == "Runtime.callFunctionOn":
                object_id = params.get("objectId")
                functionDeclaration = params.get("functionDeclaration")
                if functionDeclaration != 'function() { return this.tagName ? this.tagName.toLowerCase() : ""; }':
                    raise NotImplementedError
                return tag_names.get(object_id, {})
            else:
                return {}

        mock_stagehand_page.send_cdp.side_effect = mocked_send_cdp
        return mocked_send_cdp

    return mock_send_cdp_factory


class TestGetAccessibilityTree:
    async def test_empty_tree_result(self, mock_stagehand_page: StagehandPage, mock_stagehand_logger: StagehandLogger, mock_send_cdp):
        mock_send_cdp(ax_tree={"nodes": []})
        actual = await get_accessibility_tree(mock_stagehand_page, mock_stagehand_logger)
        assert actual["simplified"] == ""
        assert actual["tree"] == []
        assert actual["iframes"] == []
        assert actual["idToUrl"] == {}

    async def test_select_tag_included_in_simplified(self, mock_stagehand_page: StagehandPage, mock_stagehand_logger: StagehandLogger, mock_send_cdp, load_ax_tree):
        mock_send_cdp(
            ax_tree=load_ax_tree("select.json"),
            backend_nodes={12: {"object": {"objectId": "1234"}}},
            tag_names={"1234": {"result": {"value": "select"}}},
        )
        actual = await get_accessibility_tree(mock_stagehand_page, mock_stagehand_logger)

        assert (
"""[2] RootWebArea
  [9] generic
    [10] heading: Select Menus
    [11] LabelText
      [29] StaticText: Choose a pet:
    [12] select: Choose a pet: value=Hamster
      [15] MenuListPopup
        [19] option: Dog
        [22] option: Cat
        [25] option: Hamster (selected=true)
"""
        ) == actual["simplified"]
        assert [] == actual["iframes"]
        assert {"2": "https://example.com/select.html"} == actual["idToUrl"]

    async def test_input_type_radio(self, mock_stagehand_page: StagehandPage, mock_stagehand_logger: StagehandLogger, mock_send_cdp, load_ax_tree):
        mock_send_cdp(
            ax_tree=load_ax_tree("input-radio.json"),
            backend_nodes={12: {"object": {"objectId": "1234"}}},
            tag_names={"1234": {"result": {"value": "select"}}},
        )
        actual = await get_accessibility_tree(mock_stagehand_page, mock_stagehand_logger)

        assert (
"""[2] RootWebArea
  [8] generic
    [9] heading: Radio Menus
    [10] group: Select a maintenance drone:
      [11] Legend
        [22] StaticText: Select a maintenance drone:
      [13] radio: Huey (checked=true)
      [16] radio: Dewey
      [19] radio: Louie
"""
        ) == actual["simplified"]
        assert [] == actual["iframes"]
        assert {"2": "https://example.com/input-radio.html"} == actual["idToUrl"]

    async def test_input_type_range(self, mock_stagehand_page: StagehandPage, mock_stagehand_logger: StagehandLogger, mock_send_cdp, load_ax_tree):
        mock_send_cdp(
            ax_tree=load_ax_tree("input-range.json"),
            backend_nodes={12: {"object": {"objectId": "1234"}}},
            tag_names={"1234": {"result": {"value": "select"}}},
        )
        actual = await get_accessibility_tree(mock_stagehand_page, mock_stagehand_logger)

        assert (
"""[2] RootWebArea
  [8] generic
    [9] heading: Range Input
    [10] generic
      [11] slider: Volume value=5 (valuemin=0, valuemax=11)
      [15] LabelText
        [17] StaticText: Volume
"""
        ) == actual["simplified"]
        assert [] == actual["iframes"]
        assert {"2": "https://example.com/input-range.html"} == actual["idToUrl"]

    async def test_list_links(self, mock_stagehand_page: StagehandPage, mock_stagehand_logger:StagehandLogger, mock_send_cdp, load_ax_tree):
        mock_send_cdp(
            ax_tree=load_ax_tree("list_links.json"),
            backend_nodes={},
            tag_names={},
        )
        actual = await get_accessibility_tree(mock_stagehand_page, mock_stagehand_logger)

        assert (
"""[2] RootWebArea
  [8] generic
    [9] heading: List Links
    [10] list
      [11] listitem
        [20] ListMarker: •
        [12] link: Google
      [13] listitem
        [22] ListMarker: •
        [14] link: DuckDuckGo
      [15] listitem
        [24] ListMarker: •
        [16] link: Bing
      [17] listitem
        [26] ListMarker: •
        [18] link: Brave
"""
        ) == actual["simplified"]
        assert [] == actual["iframes"]
        assert {
            '12': 'https://www.google.com/',
            '14': 'https://duckduckgo.com/',
            '16': 'https://www.bing.com/',
            '18': 'https://search.brave.com/',
            '2': 'https://example.com/list_links.html'
        } == actual["idToUrl"]
