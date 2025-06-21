# Import necessary modules for sentiment analysis functionality
from typing import Optional
from utils.api_calls import get_news_articles
from utils.sentiment import analyze_sentiment
from agents.state import StockState

def sentiment_node(state: StockState) -> StockState:
    # Main sentiment analysis function that processes news articles for a stock symbol
    try:
        # Fetch recent news articles related to the stock symbol
        articles = get_news_articles(state["symbol"])
        # Analyze the sentiment of the collected articles and store results
        state["sentiment"] = analyze_sentiment(articles)
    except ValueError as e:
        # Handle errors by setting a default error sentiment
        print(f"Sentiment Analysis Agent error for {state['symbol']}: {e}")
        state["sentiment"] = {"summary": "Error", "details": []}
    return state
