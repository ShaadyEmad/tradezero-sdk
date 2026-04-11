"""Basic asynchronous usage example for tradezero-sdk.

Set your credentials as environment variables before running:

    export TZ_API_KEY="your-api-key"
    export TZ_API_SECRET="your-api-secret"
    python examples/basic_async.py
"""

import asyncio

from tradezero import AsyncTradeZeroClient, AuthenticationError, TradeZeroAPIError


async def main() -> None:
    # Credentials are read from TZ_API_KEY and TZ_API_SECRET env vars automatically
    async with AsyncTradeZeroClient() as client:
        # 1. List all accounts
        accounts = await client.accounts.list_accounts()
        if not accounts:
            print("No accounts found.")
            return

        account_id = accounts[0].account
        print(f"Account:    {account_id}")
        print(f"Equity:     {accounts[0].equity:,.2f}")

        # 2. Day P&L summary
        pnl = await client.accounts.get_account_pnl(account_id)
        print(f"\nDay P&L:    {pnl.day_pnl:+,.2f}")
        print(f"Realized:   {pnl.day_realized:+,.2f}")
        print(f"Unrealized: {pnl.day_unrealized:+,.2f}")

        # 3. Open positions with computed unrealized P&L
        positions = await client.positions.get_positions(account_id)
        if positions:
            print(f"\nOpen positions ({len(positions)}):")
            for pos in positions:
                sign = "+" if pos.unrealized_pnl >= 0 else ""
                print(
                    f"  {pos.symbol:10s} {pos.side:5s}  "
                    f"{pos.shares:>6} shares  "
                    f"unrealized: {sign}{pos.unrealized_pnl:,.2f}"
                )
        else:
            print("\nNo open positions.")

        # 4. Check short-sell borrow availability (read-only, no order placed)
        symbol = "AAPL"
        etb = await client.trading.is_easy_to_borrow(account_id, symbol)
        print(f"\n{symbol} easy to borrow: {etb}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AuthenticationError:
        print("Authentication failed. Check TZ_API_KEY and TZ_API_SECRET.")
    except TradeZeroAPIError as exc:
        print(f"API error {exc.status_code}: {exc}")
