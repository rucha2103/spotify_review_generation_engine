"""
Unit tests for analysis service.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis_service import AnalysisService


class TestAnalysisService:
    """Test AnalysisService class."""
    
    @patch('analysis_service.LLMClient')
    @patch('analysis_service.FileReaderService')
    def test_initialization(self, mock_file_reader, mock_llm_client):
        """Test analysis service initialization."""
        service = AnalysisService()
        assert service.llm_client is not None
        assert service.file_reader is not None
    
    @patch('analysis_service.SessionLocal')
    def test_load_existing_insights(self, mock_session):
        """Test loading existing insights from database."""
        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock insight data
        mock_insight1 = MagicMock()
        mock_insight1.question_id = "Q1"
        mock_insight1.json_content = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Test summary",
            "key_findings": ["Finding 1"],
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        mock_db.query.return_value.all.return_value = [mock_insight1]
        
        service = AnalysisService()
        insights = service.load_existing_insights()
        
        assert "Q1" in insights
        assert insights["Q1"]["question_id"] == "Q1"
    
    @patch('analysis_service.FileReaderService')
    def test_load_new_reviews(self, mock_file_reader_class):
        """Test loading new reviews from file reader."""
        # Mock file reader
        mock_file_reader = MagicMock()
        mock_file_reader.read_all_files.return_value = [
            {"source": "app_store", "review_text": "Test review", "rating": 3}
        ]
        mock_file_reader_class.return_value = mock_file_reader
        
        service = AnalysisService()
        reviews = service.load_new_reviews()
        
        assert len(reviews) == 1
        assert reviews[0]["source"] == "app_store"
    
    @patch('analysis_service.SessionLocal')
    def test_store_reviews_in_db(self, mock_session):
        """Test storing reviews in database."""
        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        reviews = [
            {"source": "app_store", "review_text": "Test review", "rating": 3}
        ]
        
        service = AnalysisService()
        service.store_reviews_in_db(reviews)
        
        # Verify review was added
        assert mock_db.add.call_count == 1
        assert mock_db.commit.called
    
    def test_craft_llm_prompt(self):
        """Test LLM prompt crafting."""
        service = AnalysisService()
        
        existing_insights = {
            "Q1": {
                "question_id": "Q1",
                "question_text": "Why do users struggle to discover new music?",
                "insight_summary": "Old summary",
                "key_findings": ["Old finding"],
                "metadata": {
                    "total_reviews_analyzed": 100,
                    "last_updated": "2026-06-20T12:00:00"
                }
            }
        }
        
        new_reviews = [
            {"source": "app_store", "review_text": "New review", "rating": 3}
        ]
        
        prompt = service.craft_llm_prompt(existing_insights, new_reviews)
        
        assert "CURRENT INSIGHTS" in prompt
        assert "NEW REVIEWS" in prompt
        assert "Growth Product Manager" in prompt
        assert "Q1" in prompt
    
    @patch('analysis_service.SessionLocal')
    def test_update_database_insights(self, mock_session):
        """Test updating database with new insights."""
        # Mock database session
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        
        # Mock existing insight
        mock_existing = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_existing
        
        insights = [
            {
                "question_id": "Q1",
                "question_text": "Why do users struggle to discover new music?",
                "insight_summary": "New summary",
                "key_findings": ["New finding"],
                "metadata": {
                    "total_reviews_analyzed": 200,
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        ]
        
        service = AnalysisService()
        service.update_database_insights(insights)
        
        # Verify commit was called
        assert mock_db.commit.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
