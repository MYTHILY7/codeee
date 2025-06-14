import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from db_setup import ProcessedArticle, IssueHistory, Session
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENTS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATEGORY_NAMES = {
    "CurrentTrends": "⌚️ Current Trends",
    "LearnTechnologies": "🧑🏽‍💻 Learn Technologies",
    "NewTools": "🛠️ New Tools",
    "UseCases": "💡 Use Cases"
}

AI_BANNER_URL = "https://raw.githubusercontent.com/MYTHILY7/codeee/refs/heads/main/hexa%20logo.png"

def get_top_articles_by_category(session, category, max_count=3):
    selected = []
    candidates = (
        session.query(ProcessedArticle)
        .filter(
            ProcessedArticle.category == category,
            ProcessedArticle.summary.isnot(None),
            ProcessedArticle.summary != ""
        )
        .order_by(ProcessedArticle.scraped_at.desc())
        .limit(max_count * 5)
        .all()
    )

    for art in candidates:
        if not art.summary.strip():
            logger.info(f"⛔ Skipping article with empty summary: {art.url}")
            continue

        already_sent = session.query(IssueHistory).filter_by(url=art.url).first()
        if already_sent:
            logger.info(f"📭 Already sent, skipping: {art.url}")
            continue

        selected.append(art)
        if len(selected) == max_count:
            break

    return selected

def send_summary_email():
    session = Session()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Weekly AI DIGEST"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(RECIPIENTS)

    # 🗓️ Format today's date
    today = datetime.now().strftime("%A, %B %d, %Y")

    # 📨 HTML email template
    html = f"""
    <html>
    <body style="font-family:Arial, sans-serif; color:#222; background-color:#f7f7f7; padding:20px;">
        <div style="max-width:700px; margin:auto; background:white; padding:20px; border-radius:10px;">
            <img src="{AI_BANNER_URL}" alt="AI Digest Banner" style="width:100%; border-radius:10px 10px 0 0;"/>
            <h1 style="text-align:center; color:#D60000; font-weight:900; font-size:36px; font-family:'Georgia', serif; margin-top:20px;">
                <span style="letter-spacing:2px;">AI DIGEST</span>
            </h1>
            <p style="text-align:center; color:#aaa; font-size:14px; margin-top:-10px;">{today}</p>
            <p style="text-align:center; color:#888;">Curated updates from the world of Artificial Intelligence</p>
            <hr style="border:0; height:1px; background:#eee;"/>
    """

    sent_articles = []

    for cat, display_name in CATEGORY_NAMES.items():
        html += f"<h2 style='color:#f5f5dc; background-color:#333; padding:5px 10px; border-radius:5px;'>{display_name}</h2>"
        new_articles = get_top_articles_by_category(session, cat, max_count=3)

        if not new_articles:
            html += "<p><em>No new articles this week.</em></p>"
            logger.info(f"🕵️ No new valid articles for category: {cat}")
            continue

        for art in new_articles:
            html += f"""
                <div style="margin-bottom:15px;">
                    <a href="{art.url}" style="text-decoration:none; color:#add8e6;">
                        <strong>{art.title}</strong>
                    </a><br/>
                    <small style="color:#555;">{art.summary.strip()}</small>
                </div>
            """
        sent_articles.extend(new_articles)

    html += "</div></body></html>"
    session.close()
    msg.attach(MIMEText(html, "html"))

    if not sent_articles:
        logger.info("🛑 No new content to send. Skipping email.")
        return []

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as s:
            s.starttls()
            s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.sendmail(EMAIL_ADDRESS, RECIPIENTS, msg.as_string())
        logger.info("✅ Email sent successfully.")
        return sent_articles
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return []

def send_and_archive():
    sent_articles = send_summary_email()
    if not sent_articles:
        return

    session = Session()
    for art in sent_articles:
        history = IssueHistory(
            category=art.category,
            title=art.title,
            url=art.url,
            summary=art.summary,
            published_at=art.published_at
        )
        session.add(history)
    session.commit()
    session.close()
    logger.info("🗂️ Archived sent articles.")

if __name__ == "__main__":
    send_and_archive()
    
