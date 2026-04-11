"""Fixtures for live integration tests.

Requires environment variables:
    export TZ_API_KEY="your-api-key"
    export TZ_API_SECRET="your-api-secret"

Run with:
    pytest tests/live/ -m live -v
"""

import os

import pytest

from tradezero import AsyncTradeZeroClient, TradeZeroClient

_API_KEY = os.environ.get("TZ_API_KEY")
_API_SECRET = os.environ.get("TZ_API_SECRET")

_skip_if_no_credentials = pytest.mark.skipif(
    not (_API_KEY and _API_SECRET),
    reason="Live tests require TZ_API_KEY and TZ_API_SECRET environment variables",
)


@pytest.fixture(scope="module")
@_skip_if_no_credentials
def sync_client():
    with TradeZeroClient(api_key=_API_KEY, api_secret=_API_SECRET) as client:
        yield client


@pytest.fixture(scope="function")
@_skip_if_no_credentials
async def async_client():
    async with AsyncTradeZeroClient(api_key=_API_KEY, api_secret=_API_SECRET) as client:
        yield client
