"""
Unit tests for JSON schema validation.
"""
import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validator import InsightValidator


class TestInsightValidator:
    """Test InsightValidator class."""
    
    def test_valid_insight(self):
        """Test validation of a valid insight."""
        insight = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Users struggle because...",
            "key_findings": ["Finding 1", "Finding 2"],
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert is_valid
        assert error == ""
    
    def test_missing_required_field(self):
        """Test validation fails with missing required field."""
        insight = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            # Missing insight_summary
            "key_findings": ["Finding 1"],
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert not is_valid
        assert "insight_summary" in error
    
    def test_invalid_question_id(self):
        """Test validation fails with invalid question_id."""
        insight = {
            "question_id": "Q7",  # Invalid
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Users struggle because...",
            "key_findings": ["Finding 1"],
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert not is_valid
        assert "Invalid question_id" in error
    
    def test_wrong_question_text(self):
        """Test validation fails with wrong question text."""
        insight = {
            "question_id": "Q1",
            "question_text": "Wrong question text",
            "insight_summary": "Users struggle because...",
            "key_findings": ["Finding 1"],
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert not is_valid
        assert "question_text" in error
    
    def test_invalid_key_findings_type(self):
        """Test validation fails with wrong key_findings type."""
        insight = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Users struggle because...",
            "key_findings": "Not a list",  # Should be list
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert not is_valid
        assert "key_findings" in error
    
    def test_invalid_metadata_type(self):
        """Test validation fails with wrong metadata type."""
        insight = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Users struggle because...",
            "key_findings": ["Finding 1"],
            "metadata": "Not a dict"  # Should be dict
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert not is_valid
        assert "metadata" in error
    
    def test_invalid_total_reviews_type(self):
        """Test validation fails with wrong total_reviews_analyzed type."""
        insight = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Users struggle because...",
            "key_findings": ["Finding 1"],
            "metadata": {
                "total_reviews_analyzed": "Not an integer",  # Should be int
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert not is_valid
        assert "total_reviews_analyzed" in error
    
    def test_invalid_timestamp_format(self):
        """Test validation fails with invalid timestamp format."""
        insight = {
            "question_id": "Q1",
            "question_text": "Why do users struggle to discover new music?",
            "insight_summary": "Users struggle because...",
            "key_findings": ["Finding 1"],
            "metadata": {
                "total_reviews_analyzed": 100,
                "last_updated": "Invalid timestamp"  # Should be ISO format
            }
        }
        
        is_valid, error = InsightValidator.validate_insight(insight)
        assert not is_valid
        assert "last_updated" in error
    
    def test_validate_insights_list_valid(self):
        """Test validation of valid insights list."""
        insights = []
        for i in range(1, 7):
            insights.append({
                "question_id": f"Q{i}",
                "question_text": InsightValidator.RESEARCH_QUESTIONS[f"Q{i}"],
                "insight_summary": f"Summary for Q{i}",
                "key_findings": [f"Finding {i}"],
                "metadata": {
                    "total_reviews_analyzed": 100,
                    "last_updated": datetime.utcnow().isoformat()
                }
            })
        
        is_valid, error = InsightValidator.validate_insights_list(insights)
        assert is_valid
        assert error == ""
    
    def test_validate_insights_list_wrong_count(self):
        """Test validation fails with wrong number of insights."""
        insights = [
            {
                "question_id": "Q1",
                "question_text": InsightValidator.RESEARCH_QUESTIONS["Q1"],
                "insight_summary": "Summary",
                "key_findings": ["Finding"],
                "metadata": {
                    "total_reviews_analyzed": 100,
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        ]  # Only 1 insight, should be 6
        
        is_valid, error = InsightValidator.validate_insights_list(insights)
        assert not is_valid
        assert "Expected 6 insights" in error
    
    def test_validate_insights_list_duplicate_ids(self):
        """Test validation fails with duplicate question_ids."""
        insights = [
            {
                "question_id": "Q1",
                "question_text": InsightValidator.RESEARCH_QUESTIONS["Q1"],
                "insight_summary": "Summary",
                "key_findings": ["Finding"],
                "metadata": {
                    "total_reviews_analyzed": 100,
                    "last_updated": datetime.utcnow().isoformat()
                }
            },
            {
                "question_id": "Q1",  # Duplicate
                "question_text": InsightValidator.RESEARCH_QUESTIONS["Q1"],
                "insight_summary": "Summary",
                "key_findings": ["Finding"],
                "metadata": {
                    "total_reviews_analyzed": 100,
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        ]
        
        is_valid, error = InsightValidator.validate_insights_list(insights)
        assert not is_valid
        assert "Duplicate" in error
    
    def test_validate_insights_list_missing_ids(self):
        """Test validation fails with missing question_ids."""
        insights = []
        for i in range(1, 5):  # Only Q1-Q4, missing Q5-Q6
            insights.append({
                "question_id": f"Q{i}",
                "question_text": InsightValidator.RESEARCH_QUESTIONS[f"Q{i}"],
                "insight_summary": f"Summary for Q{i}",
                "key_findings": [f"Finding {i}"],
                "metadata": {
                    "total_reviews_analyzed": 100,
                    "last_updated": datetime.utcnow().isoformat()
                }
            })
        
        is_valid, error = InsightValidator.validate_insights_list(insights)
        assert not is_valid
        assert "Missing question_ids" in error
    
    def test_parse_and_validate_json_valid(self):
        """Test parsing and validating valid JSON."""
        json_str = """[
            {
                "question_id": "Q1",
                "question_text": "Why do users struggle to discover new music?",
                "insight_summary": "Users struggle because...",
                "key_findings": ["Finding 1"],
                "metadata": {
                    "total_reviews_analyzed": 100,
                    "last_updated": "2026-06-21T12:00:00"
                }
            }
        ]"""
        
        is_valid, insights, error = InsightValidator.parse_and_validate_json(json_str)
        assert not is_valid  # Only 1 insight, should be 6
        assert "Expected 6 insights" in error
    
    def test_parse_and_validate_json_invalid_json(self):
        """Test parsing invalid JSON."""
        json_str = "not valid json"
        
        is_valid, insights, error = InsightValidator.parse_and_validate_json(json_str)
        assert not is_valid
        assert "Invalid JSON" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
