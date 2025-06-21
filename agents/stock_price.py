# Import required modules for type hints and API calls
from typing import Optional
from utils.api_calls import get_stock_price
from agents.state import StockState

# Main function that fetches current stock price for a given symbol
def stock_price_node(state: StockState) -> StockState:
    try:
        # Get the current stock price and store it in the state
        state["price"] = get_stock_price(state["symbol"])
    except ValueError as e:
        # Handle errors by setting price to None and logging the issue
        print(f"Stock Price Agent error for {state['symbol']}: {e}")
        state["price"] = None
    return state
