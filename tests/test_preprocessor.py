"""
Unit tests for pre-processing logic.
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessor import ReviewPreprocessor


class TestReviewPreprocessor:
    """Test ReviewPreprocessor class."""
    
    def test_initialization(self):
        """Test preprocessor initialization."""
        preprocessor = ReviewPreprocessor()
        assert preprocessor.seen_hashes == set()
    
    def test_hash_review(self):
        """Test review hashing for deduplication."""
        preprocessor = ReviewPreprocessor()
        text1 = "This is a test review"
        text2 = "This is a test review"
        text3 = "This is different"
        
        hash1 = preprocessor._hash_review(text1)
        hash2 = preprocessor._hash_review(text2)
        hash3 = preprocessor._hash_review(text3)
        
        assert hash1 == hash2  # Same text should have same hash
        assert hash1 != hash3  # Different text should have different hash
    
    def test_count_words(self):
        """Test word counting."""
        preprocessor = ReviewPreprocessor()
        
        assert preprocessor._count_words("") == 0
        assert preprocessor._count_words("test") == 1
        assert preprocessor._count_words("test review") == 2
        assert preprocessor._count_words("This is a test review") == 5
    
    def test_is_duplicate(self):
        """Test duplicate detection."""
        preprocessor = ReviewPreprocessor()
        text = "This is a test review"
        
        # First occurrence should not be duplicate
        assert not preprocessor.is_duplicate(text)
        
        # Second occurrence should be duplicate
        assert preprocessor.is_duplicate(text)
        
        # Different text should not be duplicate
        assert not preprocessor.is_duplicate("Different review")
    
    def test_meets_minimum_length(self):
        """Test minimum word count filter."""
        preprocessor = ReviewPreprocessor()
        
        # Short review should fail
        assert not preprocessor.meets_minimum_length("short", min_words=10)
        
        # Long review should pass
        long_review = "This is a long review that definitely has more than ten words in it"
        assert preprocessor.meets_minimum_length(long_review, min_words=10)
    
    def test_filter_reviews(self):
        """Test review filtering."""
        preprocessor = ReviewPreprocessor()
        
        reviews = [
            {"review_text": "short"},  # Too short
            {"review_text": "This is a longer review that meets the minimum word count requirement"},
            {"review_text": "This is a longer review that meets the minimum word count requirement"},  # Duplicate
            {"review_text": "Another long review that should pass the word count filter"}
        ]
        
        filtered = preprocessor.filter_reviews(reviews, min_words=10)
        
        # Should filter out short and duplicate
        assert len(filtered) == 2
        assert filtered[0]["review_text"] == "This is a longer review that meets the minimum word count requirement"
        assert filtered[1]["review_text"] == "Another long review that should pass the word count filter"
    
    def test_reset(self):
        """Test resetting deduplication cache."""
        preprocessor = ReviewPreprocessor()
        
        # Add some hashes
        preprocessor.is_duplicate("test1")
        preprocessor.is_duplicate("test2")
        
        assert len(preprocessor.seen_hashes) == 2
        
        # Reset
        preprocessor.reset()
        
        assert len(preprocessor.seen_hashes) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
