"""Pydantic models for the Locates module."""

from __future__ import annotations

from pydantic import BaseModel, Field

from tradezero.enums import LocateStatus, LocateTypeStr


class LocateQuoteRequest(BaseModel):
    """Payload for requesting a short-sell locate quote.

    Attributes:
        account: Account ID requesting the locate.
        symbol: Ticker to locate.
        quantity: Number of shares to locate.
        quote_req_id: Unique client-generated request identifier.
    """

    account: str
    symbol: str
    quantity: int = Field(gt=0)
    quote_req_id: str = Field(alias="quoteReqID")

    model_config = {"populate_by_name": True}


class LocateAcceptRequest(BaseModel):
    """Payload for accepting an offered locate quote.

    Attributes:
        account_id: Account ID that owns the locate.
        quote_req_id: Identifier from the original quote request.
    """

    account_id: str = Field(alias="accountId")
    quote_req_id: str = Field(alias="quoteReqID")

    model_config = {"populate_by_name": True}


class LocateSellRequest(BaseModel):
    """Payload for selling (crediting back) locate inventory.

    Attributes:
        account: Account ID.
        symbol: Ticker symbol of the locate.
        quote_req_id: New unique identifier for this sell action.
        quantity: Shares to sell back (must be ≤ available).
        locate_type: Type string (e.g., ``"Locate"``).
    """

    account: str
    symbol: str
    quote_req_id: str = Field(alias="quoteReqID")
    quantity: int = Field(gt=0)
    locate_type: LocateTypeStr = Field(alias="locateType")

    model_config = {"populate_by_name": True}


class LocateInventoryItem(BaseModel):
    """A single row from the locate inventory endpoint.

    Attributes:
        available: Shares currently available to borrow.
        sold: Shares already borrowed/sold.
        unavailable: Shares that cannot be located.
        locate_type: Integer type code.
    """

    available: int
    sold: int
    unavailable: int
    locate_type: int = Field(alias="locateType")

    model_config = {"populate_by_name": True}


class LocateHistoryItem(BaseModel):
    """A single locate history record used for polling quote status.

    Attributes:
        quote_req_id: Request identifier.
        symbol: Ticker symbol.
        quantity: Requested quantity.
        locate_status: Current lifecycle status code.
        rate: Borrow rate offered (if status is ``OFFERED``).
    """

    quote_req_id: str = Field(alias="quoteReqID")
    symbol: str
    quantity: int | None = None
    locate_status: LocateStatus = Field(alias="locateStatus")
    rate: float = Field(default=0.0)

    model_config = {"populate_by_name": True}
