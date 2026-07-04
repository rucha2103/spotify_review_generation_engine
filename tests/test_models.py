"""
Unit tests for SQLAlchemy models.
"""
import pytest
from datetime import datetime
from models import RawReview, InsightState


class TestRawReview:
    """Test RawReview model."""
    
    def test_raw_review_creation(self):
        """Test creating a RawReview instance."""
        review = RawReview(
            source="app_store",
            review_text="This is a test review",
            rating=3
        )
        
        assert review.source == "app_store"
        assert review.review_text == "This is a test review"
        assert review.rating == 3
        assert review.id is None  # Not assigned until saved to DB
    
    def test_raw_review_repr(self):
        """Test RawReview string representation."""
        review = RawReview(
            source="reddit",
            review_text="Test review",
            rating=None
        )
        repr_str = repr(review)
        
        assert "RawReview" in repr_str
        assert "reddit" in repr_str


class TestInsightState:
    """Test InsightState model."""
    
    def test_insight_state_creation(self):
        """Test creating an InsightState instance."""
        json_content = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Test summary",
            "key_findings": ["Finding 1", "Finding 2"],
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        insight = InsightState(
            question_id="Q1",
            json_content=json_content
        )
        
        assert insight.question_id == "Q1"
        assert insight.json_content == json_content
    
    def test_insight_state_repr(self):
        """Test InsightState string representation."""
        insight = InsightState(
            question_id="Q2",
            json_content={"test": "data"}
        )
        repr_str = repr(insight)
        
        assert "InsightState" in repr_str
        assert "Q2" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
