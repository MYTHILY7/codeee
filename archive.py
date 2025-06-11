from db_setup import Session, ProcessedArticle, IssueHistory

def archive_processed_articles(sent_articles):
    if not sent_articles:
        print("No articles to archive.")
        return

    session = Session()
    sent_ids = [article.id for article in sent_articles]

    for article in sent_articles:
        history = IssueHistory(
            category=article.category,
            title=article.title,
            url=article.url,
            summary=article.summary,
            published_at=article.published_at
        )
        session.add(history)

    session.commit()

    # Delete only those that were emailed
    session.query(ProcessedArticle).filter(ProcessedArticle.id.in_(sent_ids)).delete(synchronize_session=False)
    session.commit()
    session.close()
    print("🗂️ Archived and removed only emailed articles.")

