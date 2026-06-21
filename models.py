from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from database import Base
import enum


class SourceType(str, enum.Enum):
    """Enum for review sources"""
    APP_STORE = "app_store"
    GOOGLE_PLAY = "google_play"
    REDDIT = "reddit"


class RawReview(Base):
    """
    Model for storing scraped reviews from various sources.
    """
    __tablename__ = "raw_reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)  # app_store, google_play, reddit
    review_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    rating = Column(Integer, nullable=True)  # Optional, for app stores (1-5 stars)
    
    def __repr__(self):
        return f"<RawReview(id={self.id}, source={self.source}, rating={self.rating})>"


class InsightState(Base):
    """
    Model for storing the 6 research insight JSON objects.
    Each record represents one of the 6 core research questions.
    """
    __tablename__ = "insights_state"

    question_id = Column(String(10), primary_key=True)  # Q1, Q2, Q3, Q4, Q5, Q6
    json_content = Column(JSON, nullable=False)  # Stores the complete JSON object
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<InsightState(question_id={self.question_id}, updated_at={self.updated_at})>"
