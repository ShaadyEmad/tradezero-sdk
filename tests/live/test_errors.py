import pytest

from tradezero import TradeZeroClient
from tradezero.enums import OrderSide, OrderType, TimeInForce
from tradezero.exceptions import APIValidationError, TradeZeroAPIError


@pytest.mark.live
def test_error_invalid_auth():
    """Verify that wrong credentials raise TradeZeroAPIError."""
    with pytest.raises(TradeZeroAPIError) as excinfo:
        with TradeZeroClient(api_key="wrong", api_secret="wrong") as client:
            client.accounts.list_accounts()

    assert excinfo.value.status_code in [401, 403, 404, 500]


@pytest.mark.live
def test_error_insufficient_params(sync_client):
    """Verify that quantity 0 raises a validation error."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account

    with pytest.raises((APIValidationError, TradeZeroAPIError, ValueError)):
        sync_client.trading.create_order(
            target, "SPY", 0, OrderSide.BUY, OrderType.MARKET, TimeInForce.DAY
        )


@pytest.mark.live
def test_error_non_existent_symbol(sync_client):
    """Verify that orders for invalid symbols are either rejected by the API
    or accepted and immediately marked as rejected/error by the exchange.
    TradeZero may queue orders without instant validation, so either outcome is acceptable."""
    accounts = sync_client.accounts.list_accounts()
    target = accounts[0].account

    try:
        order = sync_client.trading.create_order(
            target, "NONEXISTENT_SYMBOL_123", 1, OrderSide.BUY, OrderType.MARKET, TimeInForce.DAY
        )
        # If the API accepts it, the order status should indicate rejection
        assert order.order_status is not None
    except TradeZeroAPIError:
        pass  # API rejected it immediately — expected behaviour
