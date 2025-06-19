import requests
from dotenv import load_dotenv
import os

load_dotenv()

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def get_stock_price(symbol: str) -> float:
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    response = requests.get(url)
    data = response.json()
    if "Global Quote" in data and "05. price" in data["Global Quote"]:
        return float(data["Global Quote"]["05. price"])
    else:
        raise ValueError(f"Unable to fetch stock price for {symbol}")

def get_financial_metrics(symbol: str) -> dict:
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    response = requests.get(url)
    data = response.json()
    if "MarketCapitalization" in data and "RevenueTTM" in data and "EBITDA" in data:
        return {
            "market_cap": data["MarketCapitalization"],
            "revenue": data["RevenueTTM"],
            "earnings": data["EBITDA"]
        }
    else:
        raise ValueError(f"Unable to fetch financial metrics for {symbol}")

def get_news_articles(symbol: str, max_articles: int = 5) -> list:
    symbol_to_company = {
        "IBM": "IBM",
        "AAPL": "Apple",
        "TSLA": "Tesla",
        # TODO: Add more mappings
    }
    query = symbol_to_company.get(symbol, symbol)
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWSAPI_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("status") == "ok":
        return [
            {
                "title": article.get("title", ""),
                "description": article.get("description", "")
            }
            for article in data.get("articles", [])
        ]
    else:
        raise ValueError(f"Unable to fetch news articles for {symbol}")
    
