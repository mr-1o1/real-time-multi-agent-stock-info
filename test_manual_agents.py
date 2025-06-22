from agents.state import StockState
from agents.stock_price import stock_price_node
from agents.financial_data import financial_data_node
from agents.sentiment import sentiment_node
from agents.coordinator import coordinator_node

# Just a little helper to make our prints easier to read.
def my_print(*args, **kwargs):
    print("–" * 80)
    print(*args, **kwargs)

# This function lets us test the whole agent process for a single stock.
def test_agents_manually(symbol: str):
    # Here's the starting point for our data journey.
    state: StockState = {
        "symbol": symbol,
        "price": None,
        "financials": None,
        "sentiment": None,
        "status": "init"
    }
    
    # The coordinator runs first to see what needs to be done.
    my_print("Initial State:", state)
    state = coordinator_node(state)
    my_print("After Coordinator (init):", state)
    
    # Now, let's run each agent one by one.
    state = stock_price_node(state)
    my_print("After Stock Price Agent:", state)
    
    state = financial_data_node(state)
    my_print("After Financial Data Agent:", state)
    
    state = sentiment_node(state)
    my_print("After Sentiment Analysis Agent:", state)
    
    # The coordinator runs again to wrap things up.
    state = coordinator_node(state)
    my_print("Final State:", state)
    
    # A few checks to make sure everything worked as expected.
    assert state["status"] == "complete", f"Expected status 'complete', got {state['status']}"
    assert state["price"] is not None, "Price should not be None"
    assert state["financials"] is not None, "Financials should not be None"
    assert state["sentiment"] is not None, "Sentiment should not be None"
    my_print("All tests passed!")

# This makes the script runnable from the command line.
if __name__ == "__main__":
    # We'll use Apple as our test case.
    test_agents_manually("AAPL")
