from typing import TypedDict, Optional

class StockState(TypedDict):
    symbol: str
    price: Optional[float]
    financials: Optional[dict]
    sentiment: Optional[dict]
    status: str
