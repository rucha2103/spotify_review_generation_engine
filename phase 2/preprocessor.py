"""
Preprocessing module for review filtering and deduplication.
Implements negative sentiment bias and feedback-only focus.
"""
import hashlib
from typing import List, Set


class ReviewPreprocessor:
    """
    Handles review preprocessing including:
    - Minimum word count filter (10 words)
    - Deduplication based on review text
    """
    
    def __init__(self):
        self.seen_hashes: Set[str] = set()
    
    def _hash_review(self, review_text: str) -> str:
        """
        Generate a hash for the review text for deduplication.
        """
        return hashlib.md5(review_text.strip().lower().encode()).hexdigest()
    
    def _count_words(self, text: str) -> int:
        """
        Count the number of words in the text.
        """
        return len(text.split())
    
    def is_duplicate(self, review_text: str) -> bool:
        """
        Check if the review is a duplicate based on hash.
        """
        review_hash = self._hash_review(review_text)
        if review_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(review_hash)
        return False
    
    def meets_minimum_length(self, review_text: str, min_words: int = 10) -> bool:
        """
        Check if the review meets the minimum word count requirement.
        """
        return self._count_words(review_text) >= min_words
    
    def filter_reviews(self, reviews: List[dict], min_words: int = 10) -> List[dict]:
        """
        Filter reviews based on:
        1. Minimum word count (10 words)
        2. Deduplication
        
        Args:
            reviews: List of review dictionaries with 'review_text' key
            min_words: Minimum word count threshold
            
        Returns:
            Filtered list of reviews
        """
        filtered = []
        for review in reviews:
            review_text = review.get('review_text', '')
            
            # Check minimum word count
            if not self.meets_minimum_length(review_text, min_words):
                continue
            
            # Check for duplicates
            if self.is_duplicate(review_text):
                continue
            
            filtered.append(review)
        
        return filtered
    
    def reset(self):
        """
        Reset the deduplication cache.
        """
        self.seen_hashes.clear()
