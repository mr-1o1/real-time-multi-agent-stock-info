from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_sentiment(articles: list) -> dict:
    analyzer = SentimentIntensityAnalyzer()
    sentiments = []
    for article in articles:
        text = article["title"] + " " + article["description"]
        score = analyzer.polarity_scores(text)
        sentiment = "Positive" if score["compound"] > 0.05 else "Negative" if score["compound"] < -0.05 else "Neutral"
        sentiments.append({
            "title": article["title"],
            "sentiment": sentiment
        })
    
    if sentiments:
        positive_count = sum(1 for s in sentiments if s["sentiment"] == "Positive")
        negative_count = sum(1 for s in sentiments if s["sentiment"] == "Negative")
        if positive_count > negative_count:
            summary = "Positive"
        elif negative_count > positive_count:
            summary = "Negative"
        else:
            summary = "Neutral"
    else:
        summary = "No articles found"
    
    return {
        "summary": summary,
        "details": sentiments
    }

