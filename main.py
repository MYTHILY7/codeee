import time
import schedule
import logging
from datetime import datetime, timedelta
from scraper import fetch_articles
from processor import deduplicate_and_process
from emailer import send_summary_email
from archive import archive_processed_articles  # ✅ NEW import
from db_setup import ScrapedArticle, ProcessedArticle, IssueHistory, Session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def full_pipeline():
    try:
        logging.info("⏰ Pipeline start")
        for cat in ["CurrentTrends", "LearnTechnologies", "NewTools", "UseCases"]:
            fetch_articles(cat)
        deduplicate_and_process()
        sent_articles = send_summary_email()  # ✅ Capture sent articles
        logging.info("📧 Email sent!")

        archive_processed_articles(sent_articles)  # ✅ Archive only emailed ones

    except Exception as e:
        logging.error(f"Pipeline error: {e}")

def cleanup():
    try:
        session = Session()
        cutoff = datetime.utcnow() - timedelta(days=30)
        session.query(ScrapedArticle).filter(ScrapedArticle.scraped_at < cutoff).delete()
        session.query(ProcessedArticle).filter(ProcessedArticle.scraped_at < cutoff).delete()
        session.query(IssueHistory).filter(IssueHistory.published_at < cutoff).delete()
        session.commit()
        session.close()
        logging.info("✅ Weekly cleanup done.")
    except Exception as e:
        logging.error(f"Cleanup error: {e}")

# === IMMEDIATE RUN TO SEND MAIL NOW ===
full_pipeline()

# === SCHEDULED RUNS ===
schedule.every().day.at("20:50").do(full_pipeline)
schedule.every().sunday.at("23:00").do(cleanup)

logging.info("📅 Scheduler running...")

try:
    while True:
        schedule.run_pending()
        time.sleep(60)
except KeyboardInterrupt:
    logging.info("🛑 Scheduler stopped.")
