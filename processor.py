from db_setup import ScrapedArticle, ProcessedArticle, Session
from datetime import datetime, timedelta
from llm_utils import summarize_text
from newspaper import Article

def deduplicate_and_process():
    session = Session()
    one_week = datetime.utcnow() - timedelta(days=7)

    for category, in session.query(ScrapedArticle.category).distinct():
        for art in session.query(ScrapedArticle).filter_by(category=category).all():
            if session.query(ProcessedArticle).filter(
                ProcessedArticle.url == art.url,
                ProcessedArticle.scraped_at >= one_week
            ).first():
                continue

            try:
                article = Article(art.url)
                article.download()
                article.parse()
                text = article.text.strip()
                summary = summarize_text(text[:2000]) if text else art.summary
            except Exception as e:
                print(f"⚠️ Failed to parse or summarize {art.url}: {e}")
                summary = art.summary

            processed = ProcessedArticle(
                category=category,
                title=art.title,
                url=art.url,
                summary=summary,
                scraped_at=art.scraped_at,
                published_at=art.published_at
            )
            session.add(processed)

    session.commit()
    session.close()
    print("✅ Processed and summarized new articles.")


