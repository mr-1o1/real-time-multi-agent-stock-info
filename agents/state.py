# Import type hints for creating structured data types
from typing import TypedDict, Optional

# Defines the structure for storing stock information across different data sources
class StockState(TypedDict):
    symbol: str  # Stock ticker symbol (e.g., AAPL, GOOGL)
    price: Optional[float]  # Current stock price, can be None if not fetched yet
    financials: Optional[dict]  # Financial data like P/E ratio, market cap, etc.
    sentiment: Optional[dict]  # Sentiment analysis results from news/social media
    status: str  # Current status of data collection (e.g., "pending", "complete", "error")
