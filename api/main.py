from fastapi import FastAPI, HTTPException
from graph import run_workflow
from agents.state import StockState

app = FastAPI(title="Stock Chatbot API")

@app.get("/stock/{symbol}", response_model=StockState)
async def get_stock_data(symbol: str) -> StockState:
    try:
        result = run_workflow(symbol.upper())
        if result["status"] != "complete":
            raise HTTPException(status_code=500, detail="Workflow failed to complete")
        if result["price"] is None or result["financials"] is None or result["sentiment"] is None:
            raise HTTPException(status_code=500, detail="Incomplete data returned")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing {symbol}: {str(e)}")
    
