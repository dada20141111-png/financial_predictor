import feedparser
from textblob import TextBlob
import statistics

class SentimentAnalyzer:
    def __init__(self, symbol: str = "BTC"):
        self.symbol = symbol
        # Google News RSS URL
        self.rss_url = f"https://news.google.com/rss/search?q={symbol}+crypto+finance&hl=en-US&gl=US&ceid=US:en"

    def fetch_news(self):
        """
        Fetches news from Google News RSS.
        """
        try:
            feed = feedparser.parse(self.rss_url)
            return feed.entries
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def analyze_sentiment(self) -> float:
        """
        Analyzes the sentiment of the latest news headlines.
        Returns a score between -1.0 (Negative) and 1.0 (Positive).
        """
        news_items = self.fetch_news()
        if not news_items:
            return 0.0

        scores = []
        # Analyze last 20 headlines
        for item in news_items[:20]:
            title = item.title
            analysis = TextBlob(title)
            scores.append(analysis.sentiment.polarity)

        if not scores:
            return 0.0

        # Return average sentiment
        avg_score = statistics.mean(scores)
        return avg_score

    def get_market_mood(self, score: float) -> str:
        """
        Converts score to a readable mood.
        """
        if score > 0.15:
            return "Bullish 🚀"
        elif score < -0.15:
            return "Bearish 🐻"
        else:
            return "Neutral 😐"

if __name__ == "__main__":
    analyzer = SentimentAnalyzer("Bitcoin")
    score = analyzer.analyze_sentiment()
    print(f"Sentiment Score for Bitcoin: {score:.4f}")
    print(f"Market Mood: {analyzer.get_market_mood(score)}")
