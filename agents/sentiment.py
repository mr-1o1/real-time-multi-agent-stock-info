from typing import Optional
from utils.api_calls import get_news_articles
from utils.sentiment import analyze_sentiment
from agents.state import StockState

def sentiment_node(state: StockState) -> StockState:
    try:
        articles = get_news_articles(state["symbol"])
        state["sentiment"] = analyze_sentiment(articles)
    except ValueError as e:
        print(f"Sentiment Analysis Agent error for {state['symbol']}: {e}")
        state["sentiment"] = {"summary": "Error", "details": []}
    return state
