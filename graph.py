from langgraph.graph import StateGraph, END
from agents.state import StockState  # Replace with your actual state definition
from agents.coordinator import coordinator_node  # Replace with your actual nodes
from agents.stock_price import stock_price_node
from agents.financial_data import financial_data_node
from agents.sentiment import sentiment_node
import time

# Define the workflow
graph = StateGraph(StockState)

# Add nodes
graph.add_node("coordinator_start", coordinator_node)
graph.add_node("stock_price_agent", stock_price_node)
graph.add_node("financial_data_agent", financial_data_node)
graph.add_node("sentiment_agent", sentiment_node)
graph.add_node("coordinator_check", coordinator_node)

# Set entry point
graph.set_entry_point("coordinator_start")

# Define edges
graph.add_edge("coordinator_start", "stock_price_agent")
graph.add_edge("stock_price_agent", "financial_data_agent")
graph.add_edge("financial_data_agent", "sentiment_agent")
graph.add_edge("sentiment_agent", "coordinator_check")
graph.add_edge("coordinator_check", END)

# Compile the graph without config
app = graph.compile(checkpointer=None, interrupt_after=None, interrupt_before=None)

# Function to run the workflow
def run_workflow(symbol: str) -> StockState:
    initial_state = StockState(symbol=symbol, status="init", price=None, financials=None, sentiment=None)
    # Pass config with recursion_limit to invoke
    final_state = app.invoke(initial_state, config={"recursion_limit": 100})
    return final_state

# Test the workflow
if __name__ == "__main__":
    symbol = "IBM"
    start_time = time.time()
    result = run_workflow(symbol)
    end_time = time.time()
    print(f"Final State: {result}")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")

