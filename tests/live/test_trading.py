import asyncio
import os
import time
import uuid
from datetime import datetime, timedelta

import pytest

from tradezero import AsyncTradeZeroClient
from tradezero.enums import OrderSide, OrderType, TimeInForce


@pytest.mark.live
def test_sync_order_lifecycle(sync_client):
    """Test full order lifecycle: Create -> List -> Cancel."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account

    symbol = "SPY"
    qty = 1
    limit_price = 100.0
    client_order_id = str(uuid.uuid4())

    order = sync_client.trading.create_order(
        target, symbol, qty, OrderSide.BUY, OrderType.LIMIT, TimeInForce.DAY,
        limit_price=limit_price,
        client_order_id=client_order_id,
    )

    assert order.order_status is not None
    assert order.account_id is not None

    time.sleep(1)
    today_orders = sync_client.trading.list_orders(target)
    found = any(o.client_order_id == client_order_id for o in today_orders)
    assert found, f"Order {client_order_id} not found in today's orders list"

    sync_client.trading.cancel_order(target, client_order_id)


@pytest.mark.live
def test_sync_list_orders(sync_client):
    """Verify listing today's orders."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account
    orders = sync_client.trading.list_orders(target)
    assert isinstance(orders, list)


@pytest.mark.live
def test_sync_historical_orders(sync_client):
    """Verify listing historical orders."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    orders = sync_client.trading.list_historical_orders(target, start_date=start_date)
    assert isinstance(orders, list)


@pytest.mark.live
def test_sync_is_easy_to_borrow(sync_client):
    """Verify easy-to-borrow check returns a bool."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account
    result = sync_client.trading.is_easy_to_borrow(target, "AAPL")
    assert isinstance(result, bool)


@pytest.mark.live
def test_sync_get_routes(sync_client):
    """Verify routes retrieval returns a list."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account
    routes = sync_client.trading.get_routes(target)
    assert isinstance(routes, list)


@pytest.mark.live
def test_async_order_lifecycle():
    """Async version of order lifecycle."""
    client_order_id = str(uuid.uuid4())

    async def _run():
        async with AsyncTradeZeroClient(
            api_key=os.environ.get("TZ_API_KEY"),
            api_secret=os.environ.get("TZ_API_SECRET"),
        ) as client:
            accounts = await client.accounts.list_accounts()
            target = accounts[0].account
            order = await client.trading.create_order(
                target, "SPY", 1, OrderSide.BUY, OrderType.LIMIT, TimeInForce.DAY,
                limit_price=50.0,
                client_order_id=client_order_id,
            )
            assert order.order_status is not None
            assert order.account_id is not None
            await client.trading.cancel_order(target, client_order_id)

    asyncio.run(_run())
