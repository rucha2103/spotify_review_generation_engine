"""
JSON file storage service.
Replaces PostgreSQL database with simple JSON file storage.
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class JSONStorage:
    """
    Simple JSON file storage for insights and reviews.
    """
    
    def __init__(self, storage_folder: str = "data"):
        self.storage_folder = storage_folder
        self.insights_file = os.path.join(storage_folder, "insights.json")
        self.reviews_file = os.path.join(storage_folder, "reviews.json")
        
        # Create storage folder if it doesn't exist
        os.makedirs(storage_folder, exist_ok=True)
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with empty structures if they don't exist."""
        if not os.path.exists(self.insights_file):
            self.save_insights([])
        
        if not os.path.exists(self.reviews_file):
            self.save_reviews([])
    
    def load_insights(self) -> Dict[str, Dict]:
        """
        Load insights from JSON file.
        
        Returns:
            Dictionary mapping question_id to insight JSON
        """
        try:
            with open(self.insights_file, 'r', encoding='utf-8') as f:
                insights_list = json.load(f)
            
            # Convert list to dictionary for easy access
            insights_dict = {}
            for insight in insights_list:
                insights_dict[insight['question_id']] = insight
            
            return insights_dict
        except Exception as e:
            print(f"Error loading insights: {e}")
            return {}
    
    def save_insights(self, insights: List[Dict]):
        """
        Save insights to JSON file.
        
        Args:
            insights: List of insight JSON objects
        """
        try:
            with open(self.insights_file, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving insights: {e}")
            raise
    
    def load_reviews(self) -> List[Dict]:
        """
        Load reviews from JSON file.
        
        Returns:
            List of review JSON objects
        """
        try:
            with open(self.reviews_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading reviews: {e}")
            return []
    
    def save_reviews(self, reviews: List[Dict]):
        """
        Save reviews to JSON file.
        
        Args:
            reviews: List of review JSON objects
        """
        try:
            with open(self.reviews_file, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving reviews: {e}")
            raise
    
    def append_reviews(self, reviews: List[Dict]):
        """
        Append new reviews to existing reviews file.
        
        Args:
            reviews: List of review JSON objects to append
        """
        existing_reviews = self.load_reviews()
        existing_reviews.extend(reviews)
        self.save_reviews(existing_reviews)
    
    def initialize_insights(self):
        """
        Initialize insights file with the 6 research questions.
        """
        from validator import InsightValidator
        
        insights = []
        for question_id in InsightValidator.VALID_QUESTION_IDS:
            insight = {
                "question_id": question_id,
                "question_text": InsightValidator.RESEARCH_QUESTIONS[question_id],
                "insight_summary": "",
                "key_findings": [],
                "metadata": {
                    "total_reviews_analyzed": 0,
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
            insights.append(insight)
        
        self.save_insights(insights)
        print(f"Initialized {len(insights)} insights")
    
    def clear_reviews(self):
        """Clear all reviews from storage."""
        self.save_reviews([])
        print("Cleared all reviews from storage")


# Convenience function for standalone usage
def main():
    """
    Main function for testing JSON storage.
    """
    storage = JSONStorage()
    
    # Initialize insights
    storage.initialize_insights()
    
    # Load and display insights
    insights = storage.load_insights()
    print(f"\nLoaded {len(insights)} insights:")
    for question_id, insight in insights.items():
        print(f"{question_id}: {insight['question_text']}")


if __name__ == "__main__":
    main()
