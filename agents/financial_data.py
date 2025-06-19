from typing import Optional
from utils.api_calls import get_financial_metrics
from agents.state import StockState

def financial_data_node(state: StockState) -> StockState:
    try:
        state["financials"] = get_financial_metrics(state["symbol"])
    except ValueError as e:
        print(f"Financial Data Agent error for {state['symbol']}: {e}")
        state["financials"] = None
    return state
