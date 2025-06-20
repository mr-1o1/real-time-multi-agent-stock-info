from typing import Optional
from agents.state import StockState

def coordinator_node(state: StockState) -> StockState:
    print(f"Coordinator: Current state: {state}")
    
    if state["status"] == "init":
        # Initialize state
        state["price"] = None
        state["financials"] = None
        state["sentiment"] = None
        state["status"] = "in_progress"
        print("Coordinator: Initialized state")
    
    # Check if all data is collected
    elif state["status"] == "in_progress":
        if (state["price"] is not None and 
            state["financials"] is not None and 
            state["sentiment"] is not None):
            state["status"] = "complete"
            print("Coordinator: All data collected, setting status to complete")
        else:
            print("Coordinator: Waiting for agents to complete")
    
    return state

