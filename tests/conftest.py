"""Shared pytest fixtures."""

import pytest
import respx
import httpx

BASE = "https://webapi.tradezero.com/v1/api"


@pytest.fixture()
def mock_router():
    """Activate a ``respx`` mock router for the default base URL."""
    with respx.mock(base_url=BASE, assert_all_called=False) as router:
        yield router
