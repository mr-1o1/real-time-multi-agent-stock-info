from typing import Optional
from utils.api_calls import get_stock_price
from agents.state import StockState

def stock_price_node(state: StockState) -> StockState:
    try:
        state["price"] = get_stock_price(state["symbol"])
    except ValueError as e:
        print(f"Stock Price Agent error for {state['symbol']}: {e}")
        state["price"] = None
    return state
