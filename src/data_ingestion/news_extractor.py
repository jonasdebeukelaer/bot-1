from typing import Tuple, List, Dict
import re

import feedparser

# see https://www.google.com/alerts# for setup
RSS_FEED_URL = "https://www.google.com/alerts/feeds/08285277604393949885/9336531935903264427"


class NewsExtractor:
    def __init__(self, limit: int = 10):
        self.url = RSS_FEED_URL
        self.limit = limit

    def get_news(self) -> List[Dict]:
        try:
            feed = feedparser.parse(self.url)

            if feed.bozo:
                raise ValueError(f"Failed to parse Google News RSS feed: {feed.bozo_exception}")

            news_items = []
            for entry in feed.entries[: self.limit]:
                news_items.append(
                    {
                        "title": self._clean_html(entry.title),
                        "published": entry.published,
                        "summary": self._clean_html(entry.summary),
                    }
                )

            return news_items
        except Exception as e:
            raise ValueError(f"An error occurred while fetching news: {str(e)}")

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from a string."""
        clean_text = re.sub(r"<[^>]+>", "", html_text)
        return clean_text


if __name__ == "__main__":
    # test
    extractor = NewsExtractor(limit=2)
    news = extractor.get_news()
    print(news)
