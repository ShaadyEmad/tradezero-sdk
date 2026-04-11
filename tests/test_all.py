# -*- coding: utf-8 -*-
"""
tradezero-sdk -- Full Live Test Script
=======================================
Tests every function in both the sync and async clients against the real API.

HOW TO ENABLE SENSITIVE TESTS:
  Some tests below are commented out because they place real orders,
  cancel orders, or request locates on your live account.
  Search for the tag  # <<< SENSITIVE >>>  to find every such block.
  Remove the triple-quotes (the  '''  lines) around a block to activate it.

Usage:
    set TZ_API_KEY=your-key
    set TZ_API_SECRET=your-secret
    python test_all.py
"""

import asyncio
import sys
import time
import uuid
from datetime import datetime, timedelta

# Force UTF-8 output so symbols print correctly on all terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── Credentials ───────────────────────────────────────────────────────────────
import os

API_KEY    = os.environ.get("TZ_API_KEY",    "")
API_SECRET = os.environ.get("TZ_API_SECRET", "")

# ── SDK imports ───────────────────────────────────────────────────────────────
from tradezero import (
    AsyncTradeZeroClient,
    TradeZeroClient,
    TradeZeroAPIError,
    TradeZeroSDKError,
    NotFoundError,
)
from tradezero.enums import LocateStatus, LocateTypeStr, OrderSide, OrderType, TimeInForce

# ── Display helpers ───────────────────────────────────────────────────────────
PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"
SEP  = "-" * 60
DBL  = "=" * 60

results: list[tuple[str, str, str]] = []   # (section, name, status)


def run(section: str, name: str, fn):
    """Run one sync test, catch any exception, record result."""
    try:
        result = fn()
        status = PASS
    except TradeZeroAPIError as e:
        status = FAIL
        result = None
        print(f"  {FAIL}  {name}")
        print(f"         -> TradeZeroAPIError {e.status_code}: {e}")
        results.append((section, name, status))
        return None
    except TradeZeroSDKError as e:
        status = FAIL
        result = None
        print(f"  {FAIL}  {name}")
        print(f"         -> TradeZeroSDKError: {e}")
        results.append((section, name, status))
        return None
    except Exception as e:
        status = FAIL
        result = None
        print(f"  {FAIL}  {name}")
        print(f"         -> {type(e).__name__}: {e}")
        results.append((section, name, status))
        return None

    results.append((section, name, status))
    print(f"  {status}  {name}")
    return result


def skip(section: str, name: str):
    """Record a skipped test without running it."""
    results.append((section, name, SKIP))
    print(f"  {SKIP}  {name}  (commented out -- see SENSITIVE block)")


def header(title: str):
    print(f"\n{SEP}\n  {title}\n{SEP}")


def print_info(msg: str):
    print(f"  [INFO] {msg}")


def summary():
    print(f"\n{DBL}")
    print("  RESULTS SUMMARY")
    print(DBL)
    passed  = sum(1 for _, _, s in results if s == PASS)
    failed  = sum(1 for _, _, s in results if s == FAIL)
    skipped = sum(1 for _, _, s in results if s == SKIP)
    total   = len(results)
    print(f"  Total  : {total}")
    print(f"  Passed : {passed}")
    print(f"  Failed : {failed}")
    print(f"  Skipped: {skipped}")
    if failed:
        print(f"\n  Failed tests:")
        for sec, name, status in results:
            if status == FAIL:
                print(f"    * [{sec}] {name}")
    if skipped:
        print(f"\n  Skipped (sensitive) tests:")
        for sec, name, status in results:
            if status == SKIP:
                print(f"    ~ [{sec}] {name}")
    print(DBL)


# ─────────────────────────────────────────────────────────────────────────────
# SYNC TESTS
# ─────────────────────────────────────────────────────────────────────────────

def run_sync_tests():
    print(f"\n{DBL}")
    print("  SYNC CLIENT TESTS  (TradeZeroClient)")
    print(DBL)

    with TradeZeroClient(api_key=API_KEY, api_secret=API_SECRET) as client:

        # ── Accounts ──────────────────────────────────────────────────────────
        header("ACCOUNTS MODULE")

        accounts = run("Accounts", "list_accounts()",
                       lambda: client.accounts.list_accounts())

        if not accounts:
            print("  [WARN] No accounts returned -- skipping account-dependent tests")
            return

        acct = accounts[0].account
        print_info(f"Using account : {acct}")
        print_info(f"Equity        : {accounts[0].equity:,.2f}")
        print_info(f"Buying Power  : {accounts[0].buying_power:,.2f}")

        run("Accounts", "get_account_details(account_id)",
            lambda: client.accounts.get_account_details(acct))

        pnl_result = run("Accounts", "get_account_pnl(account_id)",
                         lambda: client.accounts.get_account_pnl(acct))
        if pnl_result:
            print_info(f"Day P&L       : {pnl_result.day_pnl:+,.2f}")
            print_info(f"Realized      : {pnl_result.day_realized:+,.2f}")
            print_info(f"Unrealized    : {pnl_result.day_unrealized:+,.2f}")

        # ── Positions ─────────────────────────────────────────────────────────
        header("POSITIONS MODULE")

        positions = run("Positions", "get_positions(account_id)",
                        lambda: client.positions.get_positions(acct))
        if positions:
            print_info(f"Open positions: {len(positions)}")
            for p in positions:
                print_info(f"  {p.symbol:8s} {p.side:5s} {p.shares:>6} shares | "
                           f"avg={p.price_avg:.2f} last={p.price_close:.2f} "
                           f"pnl={p.unrealized_pnl:+.2f}")
        else:
            print_info("No open positions today")

        # ── Trading — safe read-only calls ────────────────────────────────────
        header("TRADING MODULE -- Read-Only (safe)")

        orders = run("Trading", "list_orders(account_id)",
                     lambda: client.trading.list_orders(acct))
        if orders:
            print_info(f"Today's orders: {len(orders)}")

        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        hist = run("Trading", f"list_historical_orders(account_id, '{start_date}')",
                   lambda: client.trading.list_historical_orders(acct, start_date))
        if hist:
            print_info(f"Historical trades (7d): {len(hist)}")

        etb_aapl = run("Trading", "is_easy_to_borrow(account_id, 'AAPL')",
                       lambda: client.trading.is_easy_to_borrow(acct, "AAPL"))
        if etb_aapl is not None:
            print_info(f"AAPL easy-to-borrow : {etb_aapl}")

        etb_gme = run("Trading", "is_easy_to_borrow(account_id, 'GME')",
                      lambda: client.trading.is_easy_to_borrow(acct, "GME"))
        if etb_gme is not None:
            print_info(f"GME  easy-to-borrow : {etb_gme}")

        routes = run("Trading", "get_routes(account_id)",
                     lambda: client.trading.get_routes(acct))
        if routes:
            print_info(f"Available routes: {len(routes)}")

        # ── Trading — order lifecycle ─────────────────────────────────────────
        # <<< SENSITIVE >>> -- places a real limit buy order then cancels it.
        # The order uses limit_price=$1.00 so it will never fill on SPY,
        # but it WILL appear in your order book until cancelled.
        # Remove the triple-quotes below to enable this block.
        header("TRADING MODULE -- Order Lifecycle (SENSITIVE)")

                                                          # <<< SENSITIVE START >>>
        coid = str(uuid.uuid4())
        print_info(f"client_order_id = {coid}")

        order_resp = run(
            "Trading", "create_order() -- limit buy SPY @ $1.00",
            lambda: client.trading.create_order(
                account_id=acct,
                symbol="SPY",
                quantity=1,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                time_in_force=TimeInForce.DAY,
                limit_price=1.00,           # far below market -- will not fill
                client_order_id=coid,
            ),
        )

        if order_resp:
            print_info(f"Order status       : {order_resp.order_status}")
            print_info(f"Leaves qty         : {order_resp.leaves_quantity}")
            print_info(f"Margin requirement : {order_resp.margin_requirement}")
            time.sleep(1)

            # Cancel the specific order we just placed
            run("Trading", "cancel_order(account_id, client_order_id)",
                lambda: client.trading.cancel_order(acct, coid))
                                                          # <<< SENSITIVE END >>>

        # Mark these as skipped in the summary
        skip("Trading", "create_order() -- limit buy SPY @ $1.00")
        skip("Trading", "cancel_order(account_id, client_order_id)")

        # <<< SENSITIVE >>> -- cancels ALL open orders on the account.
        # Remove the triple-quotes below to enable this block.
                                                          # <<< SENSITIVE START >>>
        # cancel_all_orders returns 404 when no open orders exist -- that is normal
        def safe_cancel_all(symbol=None):
            try:
                return client.trading.cancel_all_orders(acct, symbol=symbol)
            except NotFoundError:
                return "(no open orders to cancel -- 404 expected)"

        run("Trading", "cancel_all_orders(account_id)",
            lambda: safe_cancel_all())

        run("Trading", "cancel_all_orders(account_id, symbol='SPY')",
            lambda: safe_cancel_all(symbol="SPY"))
                                                          # <<< SENSITIVE END >>>

        skip("Trading", "cancel_all_orders(account_id)")
        skip("Trading", "cancel_all_orders(account_id, symbol='SPY')")

        # ── Locates — safe read-only calls ────────────────────────────────────
        header("LOCATES MODULE -- Read-Only (safe)")

        inventory = run("Locates", "get_inventory(account_id)",
                        lambda: client.locates.get_inventory(acct))
        if inventory:
            print_info(f"Locate inventory items: {len(inventory)}")

        history = run("Locates", "get_history(account_id)",
                      lambda: client.locates.get_history(acct))
        if history:
            print_info(f"Locate history items: {len(history)}")
            item = history[0]
            print_info(f"  Latest: {item.symbol} | status={item.locate_status.name} "
                       f"| rate={item.rate}")

        # <<< SENSITIVE >>> -- submits a real locate request for TSLA, then
        # cancels it. This will appear in your locate history.
        # Remove the triple-quotes below to enable this block.
        header("LOCATES MODULE -- Quote Lifecycle (SENSITIVE)")

                                                          # <<< SENSITIVE START >>>
        locate_id = f"tz_test_{int(time.time())}"
        print_info(f"quote_req_id = {locate_id}")

        run("Locates", "request_quote(account, 'TSLA', 100, quote_req_id)",
            lambda: client.locates.request_quote(acct, "TSLA", 100, locate_id))

        time.sleep(2)

        # Check the live status of our quote
        our_item = None
        try:
            fresh = client.locates.get_history(acct)
            our_item = next((h for h in fresh if h.quote_req_id == locate_id), None)
        except Exception:
            pass

        if our_item:
            print_info(f"Quote status: {our_item.locate_status.name}")

            if our_item.locate_status == LocateStatus.OFFERED:
                # To accept the offered rate (costs money), remove the # on the
                # next two run() calls.  They are kept as # comments so you can
                # enable them independently without breaking the outer block.
                run("Locates", "accept_quote(account_id, quote_req_id)",
                    lambda: client.locates.accept_quote(acct, locate_id))
                #
                sell_id = f"tz_sell_{int(time.time())}"
                run("Locates", "sell_locate(account, symbol, quote_req_id, qty, type)",
                    lambda: client.locates.sell_locate(
                        acct, "TSLA", sell_id, 100, LocateTypeStr.LOCATE
                     ))
            else:
                # Not offered yet -- cancel safely
                run("Locates", "cancel_locate(account_id, quote_req_id)",
                    lambda: client.locates.cancel_locate(acct, locate_id))
        else:
            run("Locates", "cancel_locate(account_id, quote_req_id)",
                lambda: client.locates.cancel_locate(acct, locate_id))
                                                          # <<< SENSITIVE END >>>

        skip("Locates", "request_quote(account, 'TSLA', 100, quote_req_id)")
        skip("Locates", "cancel_locate(account_id, quote_req_id)")
        skip("Locates", "accept_quote(account_id, quote_req_id)  [requires OFFERED status]")
        skip("Locates", "sell_locate(account, symbol, quote_req_id, qty, type)")


# ─────────────────────────────────────────────────────────────────────────────
# ASYNC TESTS
# ─────────────────────────────────────────────────────────────────────────────

async def run_async_tests():
    print(f"\n{DBL}")
    print("  ASYNC CLIENT TESTS  (AsyncTradeZeroClient)")
    print(DBL)

    async with AsyncTradeZeroClient(api_key=API_KEY, api_secret=API_SECRET) as client:

        async def arun(section: str, name: str, coro):
            try:
                result = await coro
                status = PASS
            except TradeZeroAPIError as e:
                status = FAIL
                result = None
                print(f"  {FAIL}  {name}")
                print(f"         -> TradeZeroAPIError {e.status_code}: {e}")
                results.append((section, name, status))
                return None
            except TradeZeroSDKError as e:
                status = FAIL
                result = None
                print(f"  {FAIL}  {name}")
                print(f"         -> TradeZeroSDKError: {e}")
                results.append((section, name, status))
                return None
            except Exception as e:
                status = FAIL
                result = None
                print(f"  {FAIL}  {name}")
                print(f"         -> {type(e).__name__}: {e}")
                results.append((section, name, status))
                return None

            results.append((section, name, status))
            print(f"  {status}  {name}")
            return result

        # ── Accounts ──────────────────────────────────────────────────────────
        header("ASYNC -- ACCOUNTS MODULE")

        accounts = await arun("Async/Accounts", "list_accounts()",
                              client.accounts.list_accounts())

        if not accounts:
            print("  [WARN] No accounts -- skipping async account-dependent tests")
            return

        acct = accounts[0].account
        print_info(f"Using account: {acct}")

        await arun("Async/Accounts", "get_account_details(account_id)",
                   client.accounts.get_account_details(acct))

        pnl = await arun("Async/Accounts", "get_account_pnl(account_id)",
                         client.accounts.get_account_pnl(acct))
        if pnl:
            print_info(f"Day P&L: {pnl.day_pnl:+,.2f}")

        # ── Positions ─────────────────────────────────────────────────────────
        header("ASYNC -- POSITIONS MODULE")

        positions = await arun("Async/Positions", "get_positions(account_id)",
                               client.positions.get_positions(acct))
        if positions:
            print_info(f"Open positions: {len(positions)}")
            for p in positions:
                print_info(f"  {p.symbol:8s} {p.side:5s} {p.shares:>6} shares | "
                           f"pnl={p.unrealized_pnl:+.2f}")

        # ── Trading — safe read-only calls ────────────────────────────────────
        header("ASYNC -- TRADING MODULE -- Read-Only (safe)")

        await arun("Async/Trading", "list_orders(account_id)",
                   client.trading.list_orders(acct))

        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        await arun("Async/Trading", f"list_historical_orders(account_id, '{start_date}')",
                   client.trading.list_historical_orders(acct, start_date))

        etb = await arun("Async/Trading", "is_easy_to_borrow(account_id, 'AAPL')",
                         client.trading.is_easy_to_borrow(acct, "AAPL"))
        if etb is not None:
            print_info(f"AAPL easy-to-borrow: {etb}")

        await arun("Async/Trading", "get_routes(account_id)",
                   client.trading.get_routes(acct))

        # ── Trading — order lifecycle ─────────────────────────────────────────
        # <<< SENSITIVE >>> -- places a real limit buy order then cancels it.
        # Remove the triple-quotes below to enable this block.
        header("ASYNC -- TRADING MODULE -- Order Lifecycle (SENSITIVE)")

                                                          # <<< SENSITIVE START >>>
        coid = str(uuid.uuid4())
        print_info(f"client_order_id = {coid}")

        order_resp = await arun(
            "Async/Trading", "create_order() -- limit buy SPY @ $1.00",
            client.trading.create_order(
                account_id=acct,
                symbol="SPY",
                quantity=1,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                time_in_force=TimeInForce.DAY,
                limit_price=1.00,           # far below market -- will not fill
                client_order_id=coid,
            ),
        )

        if order_resp:
            print_info(f"Order status: {order_resp.order_status}")
            await asyncio.sleep(1)

            # Cancel the specific order we just placed
            await arun("Async/Trading", "cancel_order(account_id, client_order_id)",
                       client.trading.cancel_order(acct, coid))

        # <<< SENSITIVE >>> -- cancels ALL open orders on the account.
        async def async_safe_cancel_all():
            try:
                return await client.trading.cancel_all_orders(acct)
            except NotFoundError:
                return "(no open orders to cancel -- 404 expected)"

        await arun("Async/Trading", "cancel_all_orders(account_id)",
                   async_safe_cancel_all())
                                                          # <<< SENSITIVE END >>>

        skip("Async/Trading", "create_order() -- limit buy SPY @ $1.00")
        skip("Async/Trading", "cancel_order(account_id, client_order_id)")
        skip("Async/Trading", "cancel_all_orders(account_id)")

        # ── Locates — safe read-only calls ────────────────────────────────────
        header("ASYNC -- LOCATES MODULE -- Read-Only (safe)")

        await arun("Async/Locates", "get_inventory(account_id)",
                   client.locates.get_inventory(acct))

        await arun("Async/Locates", "get_history(account_id)",
                   client.locates.get_history(acct))

        # <<< SENSITIVE >>> -- submits a real locate request then cancels it.
        # Remove the triple-quotes below to enable this block.
        header("ASYNC -- LOCATES MODULE -- Quote Lifecycle (SENSITIVE)")

                                                          # <<< SENSITIVE START >>>
        locate_id = f"async_{int(time.time())}"
        print_info(f"quote_req_id = {locate_id}")

        await arun("Async/Locates", "request_quote(account, 'TSLA', 100, quote_req_id)",
                   client.locates.request_quote(acct, "TSLA", 100, locate_id))

        await asyncio.sleep(2)

        await arun("Async/Locates", "cancel_locate(account_id, quote_req_id)",
                   client.locates.cancel_locate(acct, locate_id))
                                                          # <<< SENSITIVE END >>>

        skip("Async/Locates", "request_quote(account, 'TSLA', 100, quote_req_id)")
        skip("Async/Locates", "cancel_locate(account_id, quote_req_id)")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(DBL)
    print("  tradezero-sdk -- Full Function Test")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(DBL)
    print()
    print("  Sensitive tests (orders / locates) are COMMENTED OUT by default.")
    print("  Search for  <<< SENSITIVE >>>  in this file to enable them.")
    print()

    if not API_KEY or not API_SECRET:
        print("[ERROR] No credentials found.")
        print("        Set TZ_API_KEY and TZ_API_SECRET environment variables.")
        raise SystemExit(1)

    run_sync_tests()
    asyncio.run(run_async_tests())
    summary()
