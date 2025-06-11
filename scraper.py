from newspaper import Article
from datetime import datetime
from db_setup import ScrapedArticle, Session
from config import RSS_URLS

def fetch_articles(category):
    session = Session()
    new_count = 0

    # Get the list of URLs for the given category
    urls = RSS_URLS.get(category, [])
    if not urls:
        print(f"❌ No URLs found for category: {category}")
        return

    for url in urls:
        try:
            # Use newspaper3k to scrape the article
            article = Article(url)
            article.download()
            article.parse()

            # Check if the article already exists in the database
            if session.query(ScrapedArticle).filter_by(url=url).first():
                print(f"⚠️ Article already exists in the database: {url}")
                continue

            # Extract the publish date (if available)
            published = article.publish_date or datetime.now()

            # Create a new ScrapedArticle object
            new_article = ScrapedArticle(
                category=category,
                title=article.title or "No Title",
                url=url,
                summary=(article.text[:1000] if article.text else "No Content"),
                published_at=published
            )

            # Add the article to the database session
            session.add(new_article)
            new_count += 1
            print(f"✅ Successfully scraped: {url}")

        except Exception as e:
            print(f"❌ Failed to scrape article: {url}\nError: {e}")

    # Commit the session to save all new articles
    session.commit()
    session.close()
    print(f"✅ {category}: {new_count} new items scraped.")

# Example usage
if __name__ == "__main__":
    fetch_articles("CurrentTrends")