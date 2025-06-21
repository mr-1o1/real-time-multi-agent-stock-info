from typing import Optional
from agents.state import StockState

def coordinator_node(state: StockState) -> StockState:
    print(f"Coordinator: Current state: {state}")
    
    if state["status"] == "init":
        # Set up the initial state with empty data fields
        state["price"] = None
        state["financials"] = None
        state["sentiment"] = None
        state["status"] = "in_progress"
        print("Coordinator: Initialized state")
    
    # Check if all the required data has been collected from other agents
    elif state["status"] == "in_progress":
        if (state["price"] is not None and 
            state["financials"] is not None and 
            state["sentiment"] is not None):
            # All data is ready, mark the process as complete
            state["status"] = "complete"
            print("Coordinator: All data collected, setting status to complete")
        else:
            # Still waiting for some agents to finish their work
            print("Coordinator: Waiting for agents to complete")
    
    return state

