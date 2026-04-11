import asyncio
import os
import time

import pytest

from tradezero import AsyncTradeZeroClient


@pytest.mark.live
def test_sync_locate_inventory(sync_client):
    """Verify locate inventory retrieval."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account

    inventory = sync_client.locates.get_inventory(target)
    assert isinstance(inventory, list)
    if len(inventory) > 0:
        item = inventory[0]
        assert item.available >= 0


@pytest.mark.live
def test_sync_locate_history(sync_client):
    """Verify locate history retrieval."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account

    history = sync_client.locates.get_history(target)
    assert isinstance(history, list)


@pytest.mark.live
def test_sync_locate_quote_lifecycle(sync_client):
    """Test requesting and canceling a locate quote."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account

    symbol = "TSLA"
    qreq_id = f"test_qreq_{int(time.time())}"

    try:
        resp = sync_client.locates.request_quote(target, symbol, 100, qreq_id)
        assert isinstance(resp, dict)

        sync_client.locates.cancel_locate(target, qreq_id)
    except Exception as e:
        pytest.fail(f"Locate lifecycle failed: {e}")


@pytest.mark.live
def test_async_locate_list():
    """Verify async locates retrieval."""
    async def _run():
        async with AsyncTradeZeroClient(
            api_key=os.environ.get("TZ_API_KEY"),
            api_secret=os.environ.get("TZ_API_SECRET"),
        ) as client:
            accounts = await client.accounts.list_accounts()
            return await client.locates.get_inventory(accounts[0].account)

    inv = asyncio.run(_run())
    assert isinstance(inv, list)
