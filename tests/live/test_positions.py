import asyncio
import os

import pytest

from tradezero import AsyncTradeZeroClient


@pytest.mark.live
def test_sync_get_positions(sync_client):
    """Verify position retrieval and model integrity."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account

    positions = sync_client.positions.get_positions(target)
    assert isinstance(positions, list)

    if len(positions) > 0:
        pos = positions[0]
        assert pos.symbol is not None
        assert isinstance(pos.shares, int)
        assert isinstance(pos.unrealized_pnl, float)


@pytest.mark.live
def test_async_get_positions():
    """Verify async position retrieval."""
    async def _run():
        async with AsyncTradeZeroClient(
            api_key=os.environ.get("TZ_API_KEY"),
            api_secret=os.environ.get("TZ_API_SECRET"),
        ) as client:
            accounts = await client.accounts.list_accounts()
            return await client.positions.get_positions(accounts[0].account)

    positions = asyncio.run(_run())
    assert isinstance(positions, list)
