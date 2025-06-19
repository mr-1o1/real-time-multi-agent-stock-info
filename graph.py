from langgraph.graph import StateGraph, END
from agents.state import StockState
from agents.coordinator import coordinator_node
from agents.stock_price import stock_price_node
from agents.financial_data import financial_data_node
from agents.sentiment import sentiment_node

# Workflow
graph = StateGraph(StockState)

# Nodes
graph.add_node("coordinator_start", coordinator_node)
graph.add_node("stock_price", stock_price_node)
graph.add_node("financial_data", financial_data_node)
graph.add_node("sentiment_agent", sentiment_node)
graph.add_node("coordinator_check", coordinator_node)

# Entry point
graph.set_entry_point("coordinator_start")

# Edges
graph.add_edge("coordinator_start", "stock_price")
graph.add_edge("stock_price", "financial_data")
graph.add_edge("financial_data", "sentiment_agent")
graph.add_edge("sentiment_agent", "coordinator_check")
graph.add_edge("coordinator_check", END)

app = graph.compile()

# Manual test function
def run_workflow(symbol: str) -> StockState:
    initial_state = StockState(symbol=symbol, status="init", price=None, financials=None, sentiment=None)
    final_state = app.invoke(initial_state)
    return final_state

if __name__ == "__main__":
    symbol = "AAPL"
    result = run_workflow(symbol)
    print("Final State:", result)
