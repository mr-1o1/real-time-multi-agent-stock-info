from utils.api_calls import get_stock_price, get_financial_metrics, get_news_articles
from utils.sentiment import analyze_sentiment

# We'll use Apple's stock for this little test drive.
symbol = "AAPL"

# Let's start by fetching the current stock price.
try:
    price = get_stock_price(symbol)
    print("–"*80)
    print(f"Stock Price for {symbol}: ${price}")
except ValueError as e:
    print(e)

# Now, let's get the company's financial details.
try:
    metrics = get_financial_metrics(symbol)
    print("–"*80)
    print(f"Financial Metrics for {symbol}: {metrics}")
except ValueError as e:
    print(e)

# Lastly, let's pull in news articles and check the general vibe.
try:
    articles = get_news_articles(symbol)
    sentiment = analyze_sentiment(articles)
    print("–"*80)
    print(f"News Articles for {symbol}: {articles}")
    print("–"*80)
    print(f"Sentiment for {symbol}: {sentiment}")
except ValueError as e:
    print(e)
