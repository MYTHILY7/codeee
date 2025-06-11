import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_setup import ProcessedArticle, Session
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENTS

CATEGORY_NAMES = {
    "CurrentTrends": "🔍 Current Trends",
    "LearnTechnologies": "📚 Learn Technologies",
    "NewTools": "🛠️ New Tools",
    "UseCases": "💡 Use Cases"
}

def send_summary_email():
    session = Session()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Weekly AI Digest"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(RECIPIENTS)

    html = "<h2>📰 Weekly AI Digest</h2>"
    sent_articles = []

    for cat, display_name in CATEGORY_NAMES.items():
        html += f"<h3>{display_name}</h3>"
        items = session.query(ProcessedArticle)\
                       .filter_by(category=cat)\
                       .order_by(ProcessedArticle.scraped_at.desc())\
                       .limit(3).all()
        if items:
            for art in items:
                html += (
                    f"<p><a href='{art.url}'><strong>{art.title}</strong></a><br>"
                    f"<small>{art.summary[:300]}...</small></p>"
                )
            sent_articles.extend(items)
        else:
            html += "<p><em>No articles found this week.</em></p>"

    session.close()
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as s:
            s.starttls()
            s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.sendmail(EMAIL_ADDRESS, RECIPIENTS, msg.as_string())
        print("✅ Email sent.")
        return sent_articles  # ✅ Return only those that were sent
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return []

