# TradeZero Developer API — Complete Reference

> **Base URL:** `https://webapi.tradezero.com`  
> **API Version:** v1  
> **Documentation:** https://developer.tradezero.com

---

## Table of Contents

1. [Authentication](#authentication)
2. [Accounts](#accounts)
   - [Retrieve Account Details](#1-retrieve-account-details)
   - [List User Accounts](#2-list-user-accounts)
   - [Retrieve Account Values and P&L](#3-retrieve-account-values-and-pnl)
3. [Locates](#locates)
   - [Accept a Locate Quote](#4-accept-a-locate-quote)
   - [Cancel a Locate Quote](#5-cancel-a-locate-quote)
   - [Request a Locate Quote](#6-request-a-locate-quote)
   - [Sell a Locate for Credit](#7-sell-a-locate-for-credit)
   - [Get Locates History](#8-get-locates-history)
   - [Get Locates Inventory](#9-get-locates-inventory)
4. [Orders](#orders)
   - [Cancel All Orders](#10-cancel-all-orders)
   - [Is Symbol Easy to Borrow](#11-is-symbol-easy-to-borrow)
   - [Create Order](#12-create-order)
   - [Retrieve an Order from Today](#13-retrieve-an-order-from-today)
   - [Retrieve Today's Orders](#14-retrieve-todays-orders)
   - [Retrieve Historical Orders (Paginated)](#15-retrieve-historical-orders-paginated)
   - [Retrieve Historical Orders](#16-retrieve-historical-orders)
   - [Cancel Order](#17-cancel-order)
   - [Retrieve Trading Routes](#18-retrieve-trading-routes)
5. [Positions](#positions)
   - [Retrieve Positions](#19-retrieve-positions)
6. [WebSocket API](#websocket-api)
7. [Reference Tables](#reference-tables)
8. [Best Practices](#best-practices)
9. [Common Workflows](#common-workflows)

---

## Authentication

TradeZero uses API Key authentication. Every request must include both headers:

| Header | Description |
|---|---|
| `TZ-API-KEY-ID` | Your API Key ID |
| `TZ-API-SECRET-KEY` | Your API Secret Key |

### Getting Your Credentials

1. Have an active TradeZero account
2. Activate API trading through the [TradeZero Portal](https://portal.tradezero.com/)
3. Generate your API key and secret in the Portal
4. Store them securely — if you lose your secret, you must generate a new one

> ⚠️ **Never expose your API credentials in client-side code or public repositories.**

### Authentication Headers

Include the following headers in all API requests:
- `TZ-API-KEY-ID`: Your API Key ID
- `TZ-API-SECRET-KEY`: Your API Secret Key
- `Accept: application/json`

---

## Accounts

### 1. Retrieve Account Details

Retrieve comprehensive information about a specific trading account.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/account/:accountId` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | The account ID (e.g., `TZ12345678`) |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `account` | string | Account identifier |
| `accountStatus` | string | Current account status |
| `availableCash` | number | Available cash balance |
| `buyingPower` | number | Available buying power for new positions |
| `equity` | number | Total account equity (cash + position value) |
| `leverage` | number | Current leverage ratio |
| `optContractsTraded` | number | Number of option contracts traded |
| `optLevel` | number | Options trading level |
| `optionCashTotalBalance` | number | Total cash balance for options |
| `optionTradingLevel` | number | Options trading level classification |
| `overnightBp` | number | Overnight buying power |
| `realized` | number | Realized profit/loss for the day |
| `sharesTraded` | number | Number of shares traded |
| `sodEquity` | number | Start of day equity |
| `totalCommissions` | number | Total commissions paid |
| `totalLocateCosts` | number | Total locate costs incurred |
| `usedLeverage` | number | Currently used leverage amount |

#### Response Example (200 OK)

```json
{
  "account": "TZ12345678",
  "accountStatus": "Active",
  "availableCash": 50000.00,
  "buyingPower": 250000.00,
  "equity": 75000.00,
  "leverage": 4.0,
  "optContractsTraded": 0,
  "optLevel": 2,
  "optionCashTotalBalance": 0,
  "optionTradingLevel": 2,
  "overnightBp": 250000.00,
  "realized": 500.00,
  "sharesTraded": 1500,
  "sodEquity": 74500.00,
  "totalCommissions": 25.50,
  "totalLocateCosts": 10.00,
  "usedLeverage": 15000.00
}
```

---

### 2. List User Accounts

Retrieve all trading accounts associated with your API credentials.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts` |
| **Auth** | Required |

#### Request

No body or query parameters required.

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `accounts` | array | Array of account objects |
| `account` | string | Unique identifier for the trading account |
| `accountStatus` | string | Account status: `"Active"`, `"Restricted"` |
| `accountType` | string | Account type: `"Paper"`, `"Cash"`, `"Margin"`, `"PDT"` |
| `availableCash` | number | Available cash balance |
| `buyingPower` | number | Available buying power for new positions |
| `equity` | number | Total account equity |
| `leverage` | number | Current leverage ratio |
| `maintenanceDeficit` | number | Maintenance requirement deficit (if any) |
| `marginDeficit` | number | Margin requirement deficit (if any) |
| `marginRatio` | number | Current margin ratio percentage |
| `optContractsTraded` | number | Number of option contracts traded |
| `optLevel` | number | Options trading level |
| `optionCashTotalBalance` | number | Total cash balance for options |
| `optionTradingLevel` | number | Options trading level classification |
| `overnightBp` | number | Overnight buying power |
| `realized` | number | Realized profit/loss |
| `sharesTraded` | number | Number of shares traded |
| `sodEquity` | number | Start of day equity |
| `totalCommissions` | number | Total commissions paid |
| `totalLocateCosts` | number | Total locate costs incurred |
| `usedLeverage` | number | Currently used leverage amount |

#### Response Example (200 OK)

```json
{
  "accounts": [
    {
      "account": "TZ12345678",
      "accountStatus": "Active",
      "accountType": "Paper",
      "availableCash": 995037.56,
      "buyingPower": 995037.56,
      "equity": 1000000,
      "leverage": 1,
      "maintenanceDeficit": 0,
      "marginDeficit": 0,
      "marginRatio": 100,
      "optContractsTraded": 0,
      "optLevel": 0,
      "optionCashTotalBalance": 0,
      "optionTradingLevel": 0,
      "overnightBp": 1000000,
      "realized": 0,
      "sharesTraded": 0,
      "sodEquity": 1000000,
      "totalCommissions": 0,
      "totalLocateCosts": 0,
      "usedLeverage": 0
    }
  ]
}
```

#### Error Response (500)

```json
{ "error": "Internal Server Error" }
```

---

### 3. Retrieve Account Values and P&L

Retrieve detailed cash values, profit/loss calculations, and settlement information.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/pnl` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | The account ID |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `accountValue` | number | Total account value |
| `allowedLeverage` | number | Maximum allowed leverage |
| `availableCash` | number | Available cash balance |
| `dayPnl` | number | Day's profit/loss |
| `dayRealized` | number | Day's realized P&L |
| `dayUnrealized` | number | Day's unrealized P&L |
| `equityRatio` | number | Current equity ratio |
| `exposure` | number | Current market exposure |
| `optionCashUsed` | number | Cash used for options positions |
| `pnl` | array | Array of position-level P&L details |
| `sharesTraded` | number | Number of shares traded |
| `totalUnrealized` | number | Total unrealized P&L across all positions |
| `usedLeverage` | number | Currently used leverage amount |

##### P&L Array Fields

| Field | Type | Description |
|---|---|---|
| `dayPctPnLMove` | number | Day's percentage P&L move |
| `dayRealizedPnl` | number | Day's realized P&L for position |
| `dayUnrealizedPnL` | number | Day's unrealized P&L for position |
| `exposure` | number | Position market exposure |
| `pctPnLMove` | number | Total percentage P&L move |
| `positionId` | string | Unique position identifier |
| `realizedPnl` | number | Total realized P&L for position |
| `symbol` | string | Trading symbol |
| `unrealizedPnL` | number | Total unrealized P&L for position |

#### Response Example (200 OK)

```json
{
  "accountValue": 75850.00,
  "allowedLeverage": 4,
  "availableCash": 50000.00,
  "dayPnl": 850.00,
  "dayRealized": 1200.00,
  "dayUnrealized": -350.00,
  "equityRatio": 0.95,
  "exposure": 25000.00,
  "optionCashUsed": 0,
  "pnl": [
    {
      "dayPctPnLMove": 2.5,
      "dayRealizedPnl": 500.00,
      "dayUnrealizedPnL": 350.00,
      "exposure": 15000.00,
      "pctPnLMove": 3.2,
      "positionId": "POS123456",
      "realizedPnl": 1200.00,
      "symbol": "AAPL",
      "unrealizedPnL": 350.00
    },
    {
      "dayPctPnLMove": -1.5,
      "dayRealizedPnl": 700.00,
      "dayUnrealizedPnL": -700.00,
      "exposure": 10000.00,
      "pctPnLMove": -2.1,
      "positionId": "POS789012",
      "realizedPnl": 800.00,
      "symbol": "TSLA",
      "unrealizedPnL": -700.00
    }
  ],
  "sharesTraded": 250,
  "totalUnrealized": -350.00,
  "usedLeverage": 0.33
}
```

---

## Orders

### 12. Create Order

Place a new order for equities, ETFs, or options.

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/v1/api/accounts/:accountId/order` |
| **Auth** | Required |
| **Content-Type** | `application/json` |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | The account ID to place the order on |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Valid symbol of the security to trade (≤ 30 characters, alphanumeric, dots, hyphens, underscores only) |
| `orderQuantity` | integer | Yes | Number of shares to trade (≥ 1 and ≤ 1,000,000) |
| `side` | string | Yes | Buy or Sell. Possible values: `Buy`, `Sell` |
| `orderType` | string | Yes | Type of order. Possible values: `Limit`, `Market`, `Stop`, `StopLimit` |
| `securityType` | string | Yes | Type of security. Possible values: `Stock`, `Option` |
| `timeInForce` | string | Yes | Time in force for order. Possible values: `Day`, `GoodTillCancel`, `AtTheOpening`, `ImmediateOrCancel`, `FillOrKill`, `GoodTillCrossing`, `Day_Plus`, `GTC_Plus` |
| `limitPrice` | number | No | Limit price for limit orders (≤ 9999.99). Required for `Limit` and `StopLimit` orders |
| `stopPrice` | number | No | Stop price for stop orders (≤ 9999.99). Required for `Stop` and `StopLimit` orders |
| `clientOrderId` | string | No | User's unique order ID for this account (≤ 375 characters) |
| `route` | string | No | The route to send the order to. Must be a valid route for the account and security type |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `accountId` | string | Account identifier |
| `canceledQuantity` | integer | Quantity canceled |
| `clientOrderId` | string | User's unique order ID |
| `executed` | integer | Quantity executed |
| `lastPrice` | number | Last execution price |
| `lastQuantity` | integer | Last quantity executed |
| `lastUpdated` | string | Last update timestamp (ISO 8601) |
| `leavesQuantity` | integer | Remaining open quantity |
| `legCount` | integer | Number of legs (for multi-leg orders) |
| `limitPrice` | number | Limit price (if applicable) |
| `maintenanceRequirement` | number | Maintenance requirement for the order |
| `marginRequirement` | number | Margin requirement for the order |
| `maxDisplayQuantity` | integer | Max display quantity (iceberg orders) |
| `openClose` | string | Order type (Open or Close for options) |
| `orderQuantity` | integer | Total order quantity |
| `orderStatus` | string | Current order status |
| `orderType` | string | Order type |
| `pegDifference` | number | Offset for pegged orders |
| `pegOffsetType` | string | Offset type (Price or Percentage) |
| `priceAvg` | number | Average execution price |
| `priceStop` | number | Stop price (if applicable) |
| `route` | string | Routing destination |
| `securityType` | string | Security type (Stock or Option) |
| `side` | string | Buy or Sell |
| `startTime` | string | Order submission time (ISO 8601) |
| `strikePrice` | number | Strike price (options only) |
| `symbol` | string | Trading symbol |
| `text` | string | Error messages or notes |
| `timeInForce` | string | Time in force value |
| `tradedSymbol` | string | Traded symbol (OCC format for options) |

#### Response Example (200 OK)

```json
{
  "accountId": "string",
  "canceledQuantity": 0,
  "clientOrderId": "string",
  "executed": 0,
  "lastPrice": 0,
  "lastQuantity": 0,
  "lastUpdated": "string",
  "leavesQuantity": 0,
  "legCount": 0,
  "limitPrice": 0,
  "maintenanceRequirement": 0,
  "marginRequirement": 0,
  "maxDisplayQuantity": 0,
  "openClose": "string",
  "orderQuantity": 0,
  "orderStatus": "string",
  "orderType": "string",
  "pegDifference": 0,
  "pegOffsetType": "string",
  "priceAvg": 0,
  "priceStop": 0,
  "route": "string",
  "securityType": "string",
  "side": "string",
  "startTime": "2024-07-29T15:51:28.071Z",
  "strikePrice": 0,
  "symbol": "string",
  "text": "string",
  "timeInForce": "string",
  "tradedSymbol": "string"
}
```

---

### 14. Retrieve Today's Orders

Retrieve all orders submitted today for the specified account.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/orders` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | The account ID |

#### Response Fields

Returns an array of order objects with the following fields:

| Field | Type | Description |
|---|---|---|
| `accountId` | string | Account identifier |
| `canceledQuantity` | integer | Quantity canceled |
| `clientOrderId` | string | User's unique order ID |
| `executed` | integer | Quantity executed |
| `lastPrice` | number | Last execution price |
| `lastQuantity` | integer | Last quantity executed |
| `lastUpdated` | string | Last update timestamp (ISO 8601) |
| `leavesQuantity` | integer | Remaining open quantity |
| `legCount` | integer | Number of legs (for multi-leg orders) |
| `limitPrice` | number | Limit price (if applicable) |
| `maintenanceRequirement` | number | Maintenance requirement for the order |
| `marginRequirement` | number | Margin requirement for the order |
| `maxDisplayQuantity` | integer | Max display quantity (iceberg orders) |
| `openClose` | string | Order type (Open or Close for options) |
| `orderQuantity` | integer | Total order quantity |
| `orderStatus` | string | Current order status |
| `orderType` | string | Order type |
| `pegDifference` | number | Offset for pegged orders |
| `pegOffsetType` | string | Offset type (Price or Percentage) |
| `priceAvg` | number | Average execution price |
| `priceStop` | number | Stop price (if applicable) |
| `route` | string | Routing destination |
| `securityType` | string | Security type (Stock or Option) |
| `side` | string | Buy or Sell |
| `startTime` | string | Order submission time (ISO 8601) |
| `strikePrice` | number | Strike price (options only) |
| `symbol` | string | Trading symbol |
| `text` | string | Error messages or notes |
| `timeInForce` | string | Time in force value |
| `tradedSymbol` | string | Traded symbol (OCC format for options) |

#### Response Example (200 OK)

```json
[
  {
    "accountId": "string",
    "canceledQuantity": 0,
    "clientOrderId": "string",
    "executed": 0,
    "lastPrice": 0,
    "lastQuantity": 0,
    "lastUpdated": "string",
    "leavesQuantity": 0,
    "legCount": 0,
    "limitPrice": 0,
    "maintenanceRequirement": 0,
    "marginRequirement": 0,
    "maxDisplayQuantity": 0,
    "openClose": "string",
    "orderQuantity": 0,
    "orderStatus": "string",
    "orderType": "string",
    "pegDifference": 0,
    "pegOffsetType": "string",
    "priceAvg": 0,
    "priceStop": 0,
    "route": "string",
    "securityType": "string",
    "side": "string",
    "startTime": "2024-07-29T15:51:28.071Z",
    "strikePrice": 0,
    "symbol": "string",
    "text": "string",
    "timeInForce": "string",
    "tradedSymbol": "string"
  }
]
```

---

### 13. Retrieve an Order from Today

Retrieve a specific order from today by its client order ID.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/order/:orderId` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | The account ID |
| `orderId` | string | Yes | The client order ID |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `accountId` | string | Account identifier |
| `canceledQuantity` | integer | Quantity canceled |
| `clientOrderId` | string | User's unique order ID |
| `executed` | integer | Quantity executed |
| `lastPrice` | number | Last execution price |
| `lastQuantity` | integer | Last quantity executed |
| `lastUpdated` | string | Last update timestamp (ISO 8601) |
| `leavesQuantity` | integer | Remaining open quantity |
| `legCount` | integer | Number of legs (for multi-leg orders) |
| `limitPrice` | number | Limit price (if applicable) |
| `maintenanceRequirement` | number | Maintenance requirement for the order |
| `marginRequirement` | number | Margin requirement for the order |
| `maxDisplayQuantity` | integer | Max display quantity (iceberg orders) |
| `openClose` | string | Order type (Open or Close for options) |
| `orderQuantity` | integer | Total order quantity |
| `orderStatus` | string | Current order status |
| `orderType` | string | Order type |
| `pegDifference` | number | Offset for pegged orders |
| `pegOffsetType` | string | Offset type (Price or Percentage) |
| `priceAvg` | number | Average execution price |
| `priceStop` | number | Stop price (if applicable) |
| `route` | string | Routing destination |
| `securityType` | string | Security type (Stock or Option) |
| `side` | string | Buy or Sell |
| `startTime` | string | Order submission time (ISO 8601) |
| `strikePrice` | number | Strike price (options only) |
| `symbol` | string | Trading symbol |
| `text` | string | Error messages or notes |
| `timeInForce` | string | Time in force value |
| `tradedSymbol` | string | Traded symbol (OCC format for options) |

#### Response Example (200 OK)

```json
{
  "accountId": "string",
  "canceledQuantity": 0,
  "clientOrderId": "string",
  "executed": 0,
  "lastPrice": 0,
  "lastQuantity": 0,
  "lastUpdated": "string",
  "leavesQuantity": 0,
  "legCount": 0,
  "limitPrice": 0,
  "maintenanceRequirement": 0,
  "marginRequirement": 0,
  "maxDisplayQuantity": 0,
  "openClose": "string",
  "orderQuantity": 0,
  "orderStatus": "string",
  "orderType": "string",
  "pegDifference": 0,
  "pegOffsetType": "string",
  "priceAvg": 0,
  "priceStop": 0,
  "route": "string",
  "securityType": "string",
  "side": "string",
  "startTime": "2024-07-29T15:51:28.071Z",
  "strikePrice": 0,
  "symbol": "string",
  "text": "string",
  "timeInForce": "string",
  "tradedSymbol": "string"
}
```

---

### 16. Retrieve Historical Orders

Retrieve all historical orders for a specified start date.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/orders/start-date/:startDate` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Account identifier |
| `startDate` | string | Yes | Start date for order history retrieval in YYYY-MM-DD format |

#### Response Fields

Returns an array of trading history objects with the following fields:

| Field | Type | Description |
|---|---|---|
| `accountId` | string | Account identifier |
| `canceled` | boolean | Whether the order was canceled |
| `commission` | number | Commission charged for the trade |
| `currency` | string | Currency of the trade |
| `entryDate` | string | Date the order was entered (ISO 8601) |
| `execTime` | string | Time the order was executed |
| `grossProceeds` | number | Gross proceeds from the trade |
| `mLegId` | integer | Multi-leg identifier |
| `netProceeds` | number | Net proceeds after commissions and fees |
| `notes` | string | Additional notes about the trade |
| `price` | number | Execution price |
| `qty` | integer | Quantity executed |
| `securityType` | string | Type of security (Stock, Option, etc.) |
| `settleDate` | string | Settlement date (ISO 8601) |
| `side` | string | Buy or Sell |
| `spreadType` | integer | Spread type identifier |
| `symbol` | string | Trading symbol |
| `totalFees` | number | Total fees charged |
| `tradeDate` | string | Date of the trade (ISO 8601) |
| `tradeId` | integer | Unique trade identifier |

#### Response Example (200 OK)

```json
[
  {
    "accountId": "string",
    "canceled": true,
    "commission": 0,
    "currency": "string",
    "entryDate": "2024-07-29T15:51:28.071Z",
    "execTime": "string",
    "grossProceeds": 0,
    "mLegId": 0,
    "netProceeds": 0,
    "notes": "string",
    "price": 0,
    "qty": 0,
    "securityType": "string",
    "settleDate": "2024-07-29T15:51:28.071Z",
    "side": "string",
    "spreadType": 0,
    "symbol": "string",
    "totalFees": 0,
    "tradeDate": "2024-07-29T15:51:28.071Z",
    "tradeId": 0
  }
]
```

---

### 15. Retrieve Historical Orders (Paginated)

Retrieve historical orders with pagination support for a specified date range.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/orders-with-pagination/start-date/:startDate` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Account identifier |
| `startDate` | string | Yes | Start date for order history retrieval in YYYY-MM-DD format |

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | No | Symbol identifier to filter by |
| `numberOfDays` | integer | No | Number of days to return orders for (up to 365 days maximum). Defaults to 30 days if not provided |
| `offset` | integer | No | Number of orders to skip before starting to return results. Used for pagination. Defaults to 0 if not provided |
| `limit` | integer | No | Maximum number of orders to return (max 100). Defaults to 100 if not provided |

#### Response Fields

The response contains pagination metadata and an array of trading history records.

**Pagination Object:**

| Field | Type | Description |
|---|---|---|
| `currentLimit` | integer | Current limit applied to the request |
| `currentOffset` | integer | Current offset applied to the request |
| `totalRecords` | integer | Total number of records available |

**Trading History Object:**

| Field | Type | Description |
|---|---|---|
| `accountId` | string | Account identifier |
| `canceled` | boolean | Whether the order was canceled |
| `commission` | number | Commission charged for the trade |
| `currency` | string | Currency of the trade |
| `entryDate` | string | Date the order was entered (ISO 8601) |
| `execTime` | string | Time the order was executed |
| `grossProceeds` | number | Gross proceeds from the trade |
| `mLegId` | integer | Multi-leg identifier |
| `netProceeds` | number | Net proceeds after commissions and fees |
| `notes` | string | Additional notes about the trade |
| `price` | number | Execution price |
| `qty` | integer | Quantity executed |
| `securityType` | string | Type of security (Stock, Option, etc.) |
| `settleDate` | string | Settlement date (ISO 8601) |
| `side` | string | Buy or Sell |
| `spreadType` | integer | Spread type identifier |
| `symbol` | string | Trading symbol |
| `totalFees` | number | Total fees charged |
| `tradeDate` | string | Date of the trade (ISO 8601) |
| `tradeId` | integer | Unique trade identifier |

#### Response Example (200 OK)

```json
{
  "pagination": {
    "currentLimit": 0,
    "currentOffset": 0,
    "totalRecords": 0
  },
  "tradingHistory": [
    {
      "accountId": "string",
      "canceled": true,
      "commission": 0,
      "currency": "string",
      "entryDate": "2024-07-29T15:51:28.071Z",
      "execTime": "string",
      "grossProceeds": 0,
      "mLegId": 0,
      "netProceeds": 0,
      "notes": "string",
      "price": 0,
      "qty": 0,
      "securityType": "string",
      "settleDate": "2024-07-29T15:51:28.071Z",
      "side": "string",
      "spreadType": 0,
      "symbol": "string",
      "totalFees": 0,
      "tradeDate": "2024-07-29T15:51:28.071Z",
      "tradeId": 0
    }
  ]
}
```

---

### 17. Cancel Order

Cancel a specific open or partially filled order by its client order ID.

| | |
|---|---|
| **Method** | `DELETE` |
| **URL** | `/v1/api/accounts/:accountId/orders/:clientOrderId` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Account identifier |
| `clientOrderId` | string | Yes | Client order ID to cancel |

#### Response Fields (200 OK)

| Field | Type | Description |
|---|---|---|
| `accountId` | string | The user's account to send the order from |
| `canceledQuantity` | number | Shares of the order that was canceled |
| `clientOrderId` | string | The order ID assigned or specified by user |
| `executed` | number | Shares of the order that was executed |
| `lastPrice` | number | The last price the order was executed at |
| `lastQuantity` | number | The last quantity of the order that was executed |
| `lastUpdated` | string | The last time the order was updated |
| `leavesQuantity` | number | The remaining quantity of the order |
| `legCount` | integer | The number of legs in a multi-leg order |
| `legs` | object[] | Array of legs for multi-leg orders |
| `limitPrice` | number | The limit price of the order |
| `maintenanceRequirement` | number | The maintenance requirement for the order |
| `marginRequirement` | number | The margin requirement for the order |
| `maxDisplayQuantity` | number | Optional maximum quantity to display |
| `openClose` | string | Options - indicates opening or closing position |
| `orderQuantity` | number | The quantity of the order |
| `orderStatus` | string | Current status of the order (e.g., Pending, Filled, Canceled) |
| `orderType` | string | The type of order (limit, market, stop) |
| `pegDifference` | number | The offset amount for pegged orders |
| `pegOffsetType` | string | The type of offset for pegged orders (Price or Percentage) |
| `priceAvg` | number | The average execution price for the order |
| `priceStop` | number | The stop price for stop or stop-limit orders |
| `route` | string | The routing destination for the order (e.g., SMART, SIM, TEST) |
| `securityType` | string | The type of security (stock, option) |
| `side` | string | The side of the order (buy, sell) |
| `startTime` | string | The time when the order was created/submitted (ISO 8601) |
| `strikePrice` | number | The strike price for options contracts |
| `symbol` | string | The security symbol for the order |
| `text` | string | Optional text for the order, typically contains error messages |
| `timeInForce` | string | The time in force for the order (Day, GoodTillCancel, etc.) |
| `tradedSymbol` | string | The traded symbol in OCC format for options orders |

**Legs Array Object (for multi-leg orders):**

| Field | Type | Description |
|---|---|---|
| `avgPx` | number | Average execution price for the leg |
| `cxlQty` | number | Canceled quantity for the leg |
| `index` | integer | Index of the leg in the multi-leg order |
| `lastPx` | number | Last execution price for the leg |
| `lastQty` | number | Last executed quantity for the leg |
| `lvsQty` | number | Remaining quantity for the leg |
| `qty` | number | Total quantity for the leg |
| `side` | string | Side of the leg (Buy or Sell) |
| `symbol` | string | Symbol for the leg (OCC format for options) |

#### Response Example (200 OK)

```json
{
  "accountId": "string",
  "canceledQuantity": 0,
  "clientOrderId": "string",
  "executed": 0,
  "lastPrice": 0,
  "lastQuantity": 0,
  "lastUpdated": "string",
  "leavesQuantity": 0,
  "legCount": 0,
  "legs": [
    {
      "avgPx": 0,
      "cxlQty": 0,
      "index": 0,
      "lastPx": 0,
      "lastQty": 0,
      "lvsQty": 0,
      "qty": 0,
      "side": "string",
      "symbol": "string"
    }
  ],
  "limitPrice": 0,
  "maintenanceRequirement": 0,
  "marginRequirement": 0,
  "maxDisplayQuantity": 0,
  "openClose": "string",
  "orderQuantity": 0,
  "orderStatus": "string",
  "orderType": "string",
  "pegDifference": 0,
  "pegOffsetType": "string",
  "priceAvg": 0,
  "priceStop": 0,
  "route": "string",
  "securityType": "string",
  "side": "string",
  "startTime": "2024-07-29T15:51:28.071Z",
  "strikePrice": 0,
  "symbol": "string",
  "text": "string",
  "timeInForce": "string",
  "tradedSymbol": "string"
}
```

#### Error Response (400 - Bad Request)

```json
{
  "detail": "We do not allow the cancellation of orders placed through one of our UIs in the API.",
  "error": true,
  "message": "CancelOrderWithResponse",
  "statusCode": "BadRequest"
}
```

#### Error Response (500 - Internal Server Error)

Internal Server Error occurred during order cancellation.

---

### 10. Cancel All Orders

Cancel all open orders, optionally filtered by symbol.

| | |
|---|---|
| **Method** | `DELETE` |
| **URL** | `/v1/api/accounts/orders` |
| **Auth** | Required |
| **Content-Type** | `multipart/form-data` |

> ⚠️ **Use with caution.** This cancels all open orders. Details for each canceled order are not returned.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | No | Optional symbol to restrict cancellation to |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `account` | string | Yes | Account ID |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `message` | string | Confirmation message |

#### Response Example (200 OK)

```json
{
  "message": "string"
}
```

---

### 11. Is Symbol Easy to Borrow

Check if a stock symbol is easy to borrow for short selling (no locate required).

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/is-easy-to-borrow/symbol/:symbol` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | The account ID |
| `symbol` | string | Yes | The ticker symbol to check (e.g., `AAPL`) |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `isEasyToBorrow` | boolean | Whether the symbol is easy to borrow for short selling |

#### Response Example (200 OK)

```json
{
  "isEasyToBorrow": true
}
```

---

### 18. Retrieve Trading Routes

Retrieve the available routing destinations for order submission.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/routes` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Account identifier |

#### Response Fields

Returns an array of route objects with the following fields:

| Field | Type | Description |
|---|---|---|
| `orderTypes` | string[] | List of supported order types. Possible values: `Market`, `Limit`, `Stop`, `StopLimit`, `RangeOrder`, `MarketOnOpen`, `LimitOnOpen`, `TrailStop`, `MarketOnClose`, `LimitOnClose`, `Pegged` |
| `routeName` | string | Name of the trading route |
| `securityTypes` | string[] | List of supported security types. Possible values: `Stock`, `Option`, `MLEG` |
| `timesInForce` | string[] | List of supported time in force values. Possible values: `Day`, `GoodTillCancel`, `AtTheOpening`, `ImmediateOrCancel`, `FillOrKill`, `GoodTillCrossing`, `Day_Plus`, `GTC_Plus` |
| `useDisplayQty` | boolean | Whether this route supports display quantity (iceberg orders) |

#### Response Example (200 OK)

```json
{
  "routes": [
    {
      "orderTypes": [
        "Market",
        "Limit",
        "Stop",
        "StopLimit",
        "RangeOrder"
      ],
      "routeName": "PAPER",
      "securityTypes": [
        "Stock",
        "Option"
      ],
      "timesInForce": [
        "Day",
        "GoodTillCancel",
        "GoodTillCrossing"
      ],
      "useDisplayQty": false
    },
    {
      "orderTypes": [
        "Market",
        "Limit",
        "Stop",
        "StopLimit",
        "RangeOrder"
      ],
      "routeName": "PAPERM",
      "securityTypes": [
        "MLEG"
      ],
      "timesInForce": [
        "Day"
      ],
      "useDisplayQty": false
    }
  ]
}
```

---

## Positions

### 19. Retrieve Positions

Retrieve all open positions for the account.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/positions` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | The account ID |

#### Response Fields

Returns an array of position objects with the following fields:

| Field | Type | Description |
|---|---|---|
| `accountId` | string | The user's account |
| `createdDate` | string | The time when the position was created (ISO 8601) |
| `dayOvernight` | string | Indicates whether the position is a day trade or overnight position |
| `positionId` | string | The unique identifier for the position |
| `priceAvg` | number | The average execution price for the position |
| `priceClose` | number | The closing price for the position |
| `priceOpen` | number | The opening price for the position |
| `priceStrike` | number | The strike price for options contracts |
| `putCall` | string | Type of option (Put or Call) |
| `rootSymbol` | string | The underlying symbol for options positions |
| `securityType` | string | The type of security (stock, option) |
| `shares` | number | The total number of shares in the position |
| `side` | string | The side of the position (Long, Short) |
| `symbol` | string | The security symbol for the position |
| `tradedSymbol` | string | The traded symbol in OCC format for options positions |
| `updatedDate` | string | The last time the position was updated (ISO 8601) |

> **Note:** P&L fields are not included in the response. Calculate them as:
> - **Unrealized P&L** = (`priceClose` - `priceAvg`) × `shares`
> - **Market Value** = `priceClose` × `shares`
> - **Cost Basis** = `priceAvg` × `shares`

#### Response Example (200 OK)

```json
[
  {
    "accountId": "string",
    "createdDate": "2024-07-29T15:51:28.071Z",
    "dayOvernight": "string",
    "positionId": "string",
    "priceAvg": 0,
    "priceClose": 0,
    "priceOpen": 0,
    "priceStrike": 0,
    "putCall": "string",
    "rootSymbol": "string",
    "securityType": "string",
    "shares": 0,
    "side": "string",
    "symbol": "string",
    "tradedSymbol": "string",
    "updatedDate": "2024-07-29T15:51:28.071Z"
  }
]
```

---

## Locates

The Locates API manages short-sale locate services. Short selling requires borrowing shares; the "locate" process confirms shares are available to borrow.

> **Important (December 2025 Update):** The original `GET /v1/api/accounts/{accountId}/locates` endpoint has been replaced with two new endpoints: `locates/inventory` and `locates/history`.

### Typical Locate Workflow

```
1. POST /locates/quote       → Request a locate
2. GET  /locates/history     → Poll until locateStatus = 65 (Offered)
3. POST /locates/accept      → Accept the offered quote
4. GET  /locates/inventory   → Verify locate is in inventory
5. POST /locates/sell        → (Optional) Sell the locate for credit
6. DELETE /locates/cancel/…  → (Optional) Cancel before fill
```

---

### 6. Request a Locate Quote

Request a locate for a specific symbol and quantity.

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/v1/api/accounts/locates/quote` |
| **Auth** | Required |
| **Content-Type** | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `account` | string | Yes | Trading account ID |
| `symbol` | string | Yes | Stock symbol to locate |
| `quantity` | integer | Yes | Number of shares to locate |
| `quoteReqID` | string | Yes | Unique quote request ID (you generate this) |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `locateQuoteSent` | string | Confirmation message indicating the locate quote was sent |

#### Response Example (200 OK)

```json
{
  "locateQuoteSent": "string"
}
```

---

### 4. Accept a Locate Quote

Accept an offered locate quote (status = 65).

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/v1/api/accounts/locates/accept` |
| **Auth** | Required |
| **Content-Type** | `application/json` |

> **Note:** Accept is NOT available for `locateType = 2` (Intraday Only) locates.

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Trading account ID |
| `quoteReqID` | string | Yes | Quote request ID from the history endpoint |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `locateAcceptSent` | string | Confirmation message indicating the locate was accepted |

#### Response Example (200 OK)

```json
{
  "locateAcceptSent": "string"
}
```

---

### 5. Cancel a Locate Quote

Cancel an offered or sold locate that has not yet been filled.

| | |
|---|---|
| **Method** | `DELETE` |
| **URL** | `/v1/api/accounts/locates/cancel/accounts/:accountId/quoteReqID/:quoteReqID` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Trading account ID |
| `quoteReqID` | string | Yes | Quote request ID to cancel |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `locateCancelSent` | string | Confirmation message indicating the locate cancellation was sent |

#### Response Example (200 OK)

```json
{
  "locateCancelSent": "string"
}
```

---

### 7. Sell a Locate for Credit

Sell (credit) a locate from your inventory to another party.

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/v1/api/accounts/locates/sell` |
| **Auth** | Required |
| **Content-Type** | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `account` | string | Yes | Trading account ID |
| `symbol` | string | Yes | Stock symbol from inventory |
| `quoteReqID` | string | Yes | New unique quote request ID (freshly generated) |
| `quantity` | integer | Yes | Shares to sell |
| `locateType` | string | Yes | Type of locate being sold. Possible values: `Unknown`, `Locate`, `IntraDay`, `PreBorrow`, `SingleUse` |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `locateSellbackSent` | string | Confirmation message indicating the locate sellback was sent |

#### Response Example (200 OK)

```json
{
  "locateSellbackSent": "string"
}
```

---

### 8. Get Locates History

Retrieve all locate requests (open, closed, expired) for the current trading day.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/locates/history` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Trading account ID |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `accountId` | string | Account identifier |
| `symbol` | string | Ticker symbol |
| `locateShares` | number | Shares requested |
| `filledShares` | number | Shares filled |
| `locateStatus` | number | Status code (see table below) |
| `locateType` | number | Type code (see table below) |
| `locatePrice` | number | Quoted price per share |
| `quoteReqId` | string | Quote request identifier |
| `preBorrow` | boolean | Whether this is a pre-borrow |
| `locateError` | number | `1` = error with request, `0` = no error |
| `text` | string | Additional info or error message |
| `createdDate` | string | Creation timestamp (ISO 8601) |
| `updatedDate` | string | Last update timestamp (ISO 8601) |

#### Response Example (200 OK)

```json
{
  "locateHistory": [
    {
      "accountId": "string",
      "createdDate": "string",
      "filledShares": 0,
      "locateError": 0,
      "locatePrice": 0,
      "locateShares": 0,
      "locateStatus": 0,
      "locateType": 0,
      "preBorrow": true,
      "quoteReqId": "string",
      "symbol": "string",
      "text": "string",
      "updatedDate": "string"
    }
  ]
}
```

---

### 9. Get Locates Inventory

Retrieve active locate inventory for the current trading day.

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/v1/api/accounts/:accountId/locates/inventory` |
| **Auth** | Required |

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `accountId` | string | Yes | Trading account ID |

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `accountId` | string | Account identifier |
| `symbol` | string | Ticker symbol |
| `available` | number | Shares available to use for shorting |
| `sold` | number | Shares already sold/credited |
| `toBeSold` | number | Shares queued to be sold |
| `unavailable` | number | Shares currently unavailable |
| `locateType` | number | Type code (see reference table) |

#### Response Example (200 OK)

```json
{
  "locateInventory": [
    {
      "accountId": "string",
      "available": 0,
      "locateType": 0,
      "sold": 0,
      "symbol": "string",
      "toBeSold": 0,
      "unavailable": 0
    }
  ]
}
```

---

## WebSocket API

TradeZero provides real-time streaming via WebSocket.

**Base URL:** `wss://webapi.tradezero.com`

### Authentication

On connection, send:
```json
{
  "key": "YOUR_TZ-API-KEY-ID",
  "secret": "YOUR_TZ-API-SECRET-KEY"
}
```

**System messages** (`"@system": true`) indicate connection status:

```json
{ "@system": true, "ts": 1770237123968, "status": "PENDING_AUTH", "message": "Send authenticate message" }
{ "@system": true, "ts": 1770237123968, "status": "CONNECTED" }
{ "@system": true, "ts": 1770236412039, "status": "FAILED_AUTH", "message": "Authentication parameters not properly provided" }
```

### Available Streams

| Endpoint | Description |
|---|---|
| `wss://webapi.tradezero.com/stream/pnl` | Real-time P&L and position-level updates |
| `wss://webapi.tradezero.com/stream/portfolio` | Real-time order status and position updates |

---

## Reference Tables

### Order Status Values

| Status | Description |
|---|---|
| `new` | Accepted, not yet filled |
| `partially_filled` | Some quantity executed, remainder active |
| `filled` | Fully executed |
| `canceled` | Canceled by user or system |
| `rejected` | Rejected (validation error or insufficient buying power) |
| `pending_cancel` | Cancellation submitted, not yet confirmed |

### Time in Force Values

| Value | Description |
|---|---|
| `day` | Order expires at end of trading day |
| `gtc` | Good Till Canceled — remains active until filled or canceled |
| `ioc` | Immediate or Cancel — fill immediately or cancel remaining |
| `fok` | Fill or Kill — fill entire quantity immediately or cancel |

### Order Types

| Type | Description |
|---|---|
| `market` | Execute immediately at best available price |
| `limit` | Execute at specified price or better |
| `stop` | Trigger a market order when stop price is reached |
| `stop_limit` | Trigger a limit order when stop price is reached |

### Locate Status Codes

| Code | Status | Description |
|---|---|---|
| 48 | New | Locate request is new |
| 50 | Filled | Locate has been filled |
| 52 | Canceled | Locate request was canceled |
| 54 | Pending | Locate request is pending |
| 56 | Rejected | Locate request was rejected |
| 65 | Offered | Quote is offered and available for acceptance |
| 67 | Expired | Quote has expired |
| 81 | Quoting | Locate is being quoted |

### Locate Type Codes

| Code | Type | String Value (for requests) | Description |
|---|---|---|---|
| 0 | Unknown | `"Unknown"` | Unknown locate type |
| 1 | Locate | `"Locate"` | Standard locate |
| 2 | Intraday Only | `"IntraDay"` | Intraday only (cannot accept) |
| 3 | Pre-Borrow | `"PreBorrow"` | Pre-borrowed shares |
| 4 | Single Use | `"SingleUse"` | Single use locate |

---

## Best Practices

### Authentication & Security

- Never expose API keys in client-side code or public repositories
- Store credentials in environment variables or a secrets manager
- If your API secret is lost, generate a new one from the TradeZero Portal
- Log all account data access for audit purposes

### Polling Frequencies

| Data Type | Recommended Frequency |
|---|---|
| Account balances | Every 5–10 seconds during active trading |
| P&L data | Every 1–2 seconds for real-time monitoring |
| Positions | Every 1–5 seconds during active trading |
| Locate status | Every 2–5 seconds (while waiting for offers) |
| Account list | Cache and refresh hourly or on user action |

> **Tip:** Consider the WebSocket API for real-time position and order updates to reduce REST polling load.

### Order Management

- Always provide a `clientOrderId` when creating orders for easy tracking and cancellation
- Check order status after submission — don't assume immediate fill
- Handle partial fills: monitor `filledQuantity` vs `quantity`
- Cancel open GTC orders before market close if not desired overnight

### Pre-Trade Validation

```javascript
async function validateOrder(accountId, orderValue) {
  const account = await getAccountDetails(accountId);

  if (account.buyingPower < orderValue) {
    throw new Error('Insufficient buying power');
  }
  if (account.accountRestrictions.includes('TRADING_SUSPENDED')) {
    throw new Error('Account trading suspended');
  }
  if (account.dayTradesRemaining <= 0) {
    throw new Error('Day trade limit reached');
  }
  return true;
}
```

### Locate Best Practices

- Always generate unique `quoteReqID` values for each request
- Only attempt to accept quotes with status `65` (Offered)
- Verify `available > 0` in inventory before selling locates
- Cancel operations before locate status changes to `50` (Filled)

### Error Handling

Common scenarios to handle:

| Error | Cause | Resolution |
|---|---|---|
| Insufficient Buying Power | Order value exceeds buying power | Check account before placing |
| Invalid Symbol | Symbol doesn't exist or not tradeable | Validate symbol before order |
| Market Closed | Outside trading hours | Queue order or use GTC |
| Order Not Found | Already filled or canceled | Refresh order list |
| Expired Locate Quote | Locate offer timed out | Request a new quote |

---

## Common Workflows

### Building an Account Dashboard

```
1. GET /v1/api/accounts                          → List all accounts
2. GET /v1/api/account/{accountId}               → Get account details
3. GET /v1/api/accounts/{accountId}/pnl          → Get cash values & P&L
4. GET /v1/api/accounts/{accountId}/positions    → Get open positions
```

### Placing and Monitoring a Trade

```
1. GET  /v1/api/accounts/{accountId}/is-easy-to-borrow/symbol/{symbol}   → Check if locate needed
2. POST /v1/api/accounts/{accountId}/order                               → Place order
3. GET  /v1/api/accounts/{accountId}/orders                              → Monitor order status
4. GET  /v1/api/accounts/{accountId}/positions                           → Verify position update
```

### Complete Short-Sell Locate Workflow

```
1. POST   /v1/api/accounts/locates/quote                              → Request locate
2. GET    /v1/api/accounts/{accountId}/locates/history                → Poll until status = 65
3. POST   /v1/api/accounts/locates/accept                             → Accept offered quote
4. GET    /v1/api/accounts/{accountId}/locates/inventory              → Verify in inventory
5. POST   /v1/api/accounts/{accountId}/order  (side: "sell")         → Place short sell order
6. DELETE /v1/api/accounts/locates/cancel/…   (if needed)            → Cancel unfilled locate
```

### Account Health Monitor

```javascript
async function checkAccountHealth(accountId) {
  const account = await getAccountDetails(accountId);
  const pnl = await getAccountPnL(accountId);
  const alerts = [];

  const marginUsagePct = (account.marginUsed / account.equity) * 100;
  if (marginUsagePct > 80) alerts.push('⚠️ High margin usage — risk of margin call');

  const unrealizedLossPct = (pnl.totalUnrealizedPnL / account.equity) * 100;
  if (unrealizedLossPct < -10) alerts.push('⚠️ Significant unrealized losses');

  if (account.dayTradesRemaining <= 1) alerts.push('⚠️ Running low on day trades');

  return alerts;
}
```

---

## Disclaimer

> Trading securities and options involves risk and may result in the loss of your investment. TradeZero provides a trading platform and API tools but does not provide investment advice or recommendations. All investments involve risk, and past performance does not guarantee future results. Clients are solely responsible for their own trading decisions and code implementations. Consult with a qualified financial advisor before trading.
>
> TradeZero America, Inc. and TradeZero, Inc. are separate but affiliated companies. Securities trading is offered through TradeZero America, Inc., member [FINRA](https://www.finra.org) and [SIPC](https://www.sipc.org).

---

*README generated from [TradeZero Developer Documentation](https://developer.tradezero.com) — April 2026*
