 # ✅ Step 1: Add IssueHistory Table to db_setup.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class ScrapedArticle(Base):
    __tablename__ = 'scraped_articles'
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    summary = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

class ProcessedArticle(Base):
    __tablename__ = 'processed_articles'
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    summary = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)

class IssueHistory(Base):
    __tablename__ = 'issue_history'
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    summary = Column(Text)
    archived_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)

engine = create_engine('sqlite:///scrap.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
