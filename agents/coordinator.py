from typing import Optional
from agents.state import StockState

def coordinator_node(state: StockState) -> StockState:
    if state["status"] == "init":
        # Initialize state
        state["price"] = None
        state["financials"] = None
        state["sentiment"] = None
        state["status"] = "in_progress"
    elif state["status"] == "in_progress":
        # Check if all data is collected
        if (state["price"] is not None and 
            state["financials"] is not None and 
            state["sentiment"] is not None):
            state["status"] = "complete"
    return state
