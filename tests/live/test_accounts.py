import os

import pytest

from tradezero import AsyncTradeZeroClient


@pytest.mark.live
def test_sync_list_accounts(sync_client):
    """Verify syncing account list retrieval works."""
    accounts = sync_client.accounts.list_accounts()
    assert isinstance(accounts, list)
    assert len(accounts) > 0, "No accounts found for these credentials!"

    acct = accounts[0]
    assert acct.account is not None
    assert acct.account_status is not None


@pytest.mark.live
def test_sync_get_account_details(sync_client):
    """Verify detailed account retrieval returns an Account with financial fields."""
    accounts = sync_client.accounts.list_accounts()
    details = sync_client.accounts.get_account_details(accounts[0].account)

    assert details.account is not None
    assert details.buying_power >= 0
    assert details.equity >= 0


@pytest.mark.live
def test_sync_get_account_pnl(sync_client):
    """Verify P&L data retrieval."""
    accounts = sync_client.accounts.list_accounts()
    pnl = sync_client.accounts.get_account_pnl(accounts[0].account)

    assert pnl.total_unrealized is not None
    assert pnl.available_cash is not None
    assert pnl.day_pnl is not None


@pytest.mark.live
def test_async_list_accounts():
    """Verify async account list retrieval works."""
    import asyncio

    async def _run():
        async with AsyncTradeZeroClient(
            api_key=os.environ.get("TZ_API_KEY"),
            api_secret=os.environ.get("TZ_API_SECRET"),
        ) as client:
            return await client.accounts.list_accounts()

    accounts = asyncio.run(_run())
    assert isinstance(accounts, list)
    assert len(accounts) > 0


@pytest.mark.live
def test_async_get_account_details():
    """Verify async detailed account retrieval."""
    import asyncio

    async def _run():
        async with AsyncTradeZeroClient(
            api_key=os.environ.get("TZ_API_KEY"),
            api_secret=os.environ.get("TZ_API_SECRET"),
        ) as client:
            accounts = await client.accounts.list_accounts()
            return await client.accounts.get_account_details(accounts[0].account)

    details = asyncio.run(_run())
    assert details.account is not None
    assert details.equity >= 0
