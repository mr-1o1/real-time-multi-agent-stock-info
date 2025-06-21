# Import FastAPI framework and our custom workflow function
from fastapi import FastAPI, HTTPException
from graph import run_workflow
from agents.state import StockState

# Create the main FastAPI application with a title
app = FastAPI(title="Stock Chatbot API")

# Endpoint to get stock data for a given symbol
@app.get("/stock/{symbol}", response_model=StockState)
async def get_stock_data(symbol: str) -> StockState:
    try:
        # Run the workflow to gather stock data, price, and sentiment
        result = run_workflow(symbol.upper())
        
        # Check if the workflow completed successfully
        if result["status"] != "complete":
            raise HTTPException(status_code=500, detail="Workflow failed to complete")
        
        # Verify all required data fields are present
        if result["price"] is None or result["financials"] is None or result["sentiment"] is None:
            raise HTTPException(status_code=500, detail="Incomplete data returned")
        
        # Return the complete stock data
        return result
    except Exception as e:
        # Handle any unexpected errors and return a user-friendly message
        raise HTTPException(status_code=500, detail=f"Error processing {symbol}: {str(e)}")
    
