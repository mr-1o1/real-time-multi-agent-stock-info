import pytest
from utils.sentiment import analyze_sentiment

# This test checks if our sentiment analysis works on a list of articles.
def test_analyze_sentiment():
    # We'll create some sample news articles to test with.
    articles = [
        {
            "title": "IBM announces new AI platform",
            "description": "IBM's latest AI platform is expected to boost its stock."
        },
        {
            "title": "IBM faces challenges",
            "description": "IBM struggles with market competition."
        }
    ]
    
    # Let's run the analysis.
    result = analyze_sentiment(articles)

    # Now, we'll check if the results look right.
    assert result["summary"] in ["Positive", "Negative", "Neutral"]
    assert len(result["details"]) == 2
    assert result["details"][0]["title"] == "IBM announces new AI platform"
    assert result["details"][0]["sentiment"] in ["Positive", "Negative", "Neutral"]

# Here, we're making sure the function doesn't break if there are no articles.
def test_analyze_sentiment_empty():
    # What if we give it an empty list?
    result = analyze_sentiment([])
    # It should just tell us it found nothing.
    assert result["summary"] == "No articles found"
    assert result["details"] == []