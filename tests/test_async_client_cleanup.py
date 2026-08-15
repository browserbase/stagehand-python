from __future__ import annotations

import asyncio
import warnings

import pytest

from stagehand._base_client import AsyncHttpxClientWrapper


def test_unclosed_async_http_client_warns_without_running_loop() -> None:
    client = AsyncHttpxClientWrapper()

    with pytest.warns(ResourceWarning, match="Unclosed async HTTP client"):
        client.__del__()

    asyncio.run(client.aclose())


def test_closed_async_http_client_does_not_warn() -> None:
    client = AsyncHttpxClientWrapper()
    asyncio.run(client.aclose())

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        client.__del__()

    assert caught == []
