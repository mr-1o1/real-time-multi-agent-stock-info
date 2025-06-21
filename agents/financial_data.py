# Import required modules for type hints and API calls
from typing import Optional
from utils.api_calls import get_financial_metrics
from agents.state import StockState

# Agent that fetches financial metrics for a given stock symbol
def financial_data_node(state: StockState) -> StockState:
    # Try to get financial data for the stock symbol
    try:
        state["financials"] = get_financial_metrics(state["symbol"])
    # If there's an error getting financial data, log it and set to None
    except ValueError as e:
        print(f"Financial Data Agent error for {state['symbol']}: {e}")
        state["financials"] = None
    return state
