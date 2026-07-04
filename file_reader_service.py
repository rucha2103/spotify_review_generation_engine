"""
File reader service for reading manually scraped data files.
Reads JSON files from 'Data from scraping' folder and converts to standard review format.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from preprocessor import ReviewPreprocessor


class FileReaderService:
    """
    Service for reading and parsing manually scraped data files.
    Supports multiple file formats (App Store, Reddit, etc.) with flexible fallback keys.
    """
    
    def __init__(self, data_folder: str = "Data from scraping"):
        self.data_folder = data_folder
        self.preprocessor = ReviewPreprocessor()
        
        # Flexible key groups to prevent failure if scraper API schemas slightly shift
        self.fallback_text_keys = ['review_text', 'review', 'content', 'body', 'text', 'message']
        self.fallback_rating_keys = ['rating', 'score', 'stars', 'userRating']
        self.fallback_time_keys = ['date', 'created_at', 'timestamp', 'createdAt']
    
    def _read_json_file(self, file_path: str) -> List[Dict]:
        """Read a JSON file and handle nested root envelopes safely."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # If Apify wrapped the dataset array inside a dictionary envelope
                if isinstance(data, dict):
                    for envelope_key in ['items', 'data', 'results']:
                        if envelope_key in data and isinstance(data[envelope_key], list):
                            return data[envelope_key]
                    return [data]
                    
                return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

    def _get_flexible_field(self, item: Dict, exact_key: str, fallback_list: List[str]) -> Any:
        """Helper to try an explicit key first, then scan fallback variants."""
        if exact_key in item and item[exact_key] is not None:
            return item[exact_key]
        for key in fallback_list:
            if key in item and item[key] is not None:
                return item[key]
        return None

    def _parse_app_store_file(self, data: List[Dict]) -> List[Dict]:
        """Parse App Store review data from JSON file with nested block detection."""
        reviews = []
        
        for item in data:
            try:
                review_text = None
                rating = None
                timestamp = None

                # Format 1: Direct review object or nested content
                if any(k in item for k in ['review', 'body', 'content', 'reviewText']):
                    review_text = self._get_flexible_field(item, 'review', self.fallback_text_keys)
                    rating = self._get_flexible_field(item, 'rating', self.fallback_rating_keys)
                    timestamp = self._get_flexible_field(item, 'date', self.fallback_time_keys)
                
                # Format 2: Nested inside applicationData metadata tracks
                elif 'applicationData' in item:
                    if 'review' not in item and 'body' not in item:
                        continue
                    review_text = item.get('review') or item.get('body', '')
                    rating = item.get('rating')
                    timestamp = item.get('date')
                
                # Fallback: Dynamic grabber if structure matches neither but has elements
                else:
                    review_text = self._get_flexible_field(item, '', self.fallback_text_keys)
                    rating = self._get_flexible_field(item, '', self.fallback_rating_keys)
                    timestamp = self._get_flexible_field(item, '', self.fallback_time_keys)
                
                if review_text:
                    reviews.append({
                        'source': 'app_store',
                        'review_text': str(review_text).strip(),
                        'rating': rating,
                        'timestamp': timestamp or datetime.utcnow().isoformat()
                    })
            
            except Exception as e:
                print(f"Error parsing App Store review: {e}")
                continue
        
        return reviews
    
    def _parse_reddit_file(self, data: List[Dict]) -> List[Dict]:
        """Parse Reddit post data, skipping community nodes and assembling text layout."""
        reviews = []
        
        for item in data:
            try:
                # Retained explicit rule: Skip community metadata entries
                if item.get('dataType') == 'community':
                    continue
                
                title = item.get('title', '')
                body = self._get_flexible_field(item, 'body', ['selftext', 'text', 'content'])
                
                if body:
                    review_text = f"{title}. {body}" if title and title != body else body
                else:
                    review_text = title
                
                timestamp = self._get_flexible_field(item, 'createdAt', self.fallback_time_keys)
                
                if review_text:
                    reviews.append({
                        'source': 'reddit',
                        'review_text': str(review_text).strip(),
                        'rating': None,  # Reddit platform doesn't have 1-5 ratings
                        'timestamp': timestamp or datetime.utcnow().isoformat()
                    })
            
            except Exception as e:
                print(f"Error parsing Reddit post: {e}")
                continue
        
        return reviews
    
    def _parse_google_play_file(self, data: List[Dict]) -> List[Dict]:
        """Parse Google Play Store review data dynamically mapping content metrics."""
        reviews = []
        
        for item in data:
            try:
                review_text = self._get_flexible_field(item, 'review', self.fallback_text_keys)
                rating = self._get_flexible_field(item, 'rating', self.fallback_rating_keys)
                timestamp = self._get_flexible_field(item, 'date', self.fallback_time_keys)
                
                if review_text:
                    reviews.append({
                        'source': 'google_play',
                        'review_text': str(review_text).strip(),
                        'rating': rating,
                        'timestamp': timestamp or datetime.utcnow().isoformat()
                    })
            
            except Exception as e:
                print(f"Error parsing Google Play review: {e}")
                continue
        
        return reviews
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect the type of data file based on filename patterns."""
        filename = os.path.basename(file_path).lower()
        if 'reddit' in filename:
            return 'reddit'
        elif any(pattern in filename for pattern in ['appstore', 'app_store', 'apple']):
            return 'app_store'
        elif any(pattern in filename for pattern in ['google', 'play', 'playstore']):
            return 'google_play'
        return 'unknown'
    
    def _parse_file(self, file_path: str) -> List[Dict]:
        """Route parsing duties depending on file categorization rules."""
        data = self._read_json_file(file_path)
        if not data:
            return []
        
        file_type = self._detect_file_type(file_path)
        
        if file_type == 'reddit':
            return self._parse_reddit_file(data)
        elif file_type == 'app_store':
            return self._parse_app_store_file(data)
        elif file_type == 'google_play':
            return self._parse_google_play_file(data)
        else:
            print(f"Unknown file layout for {file_path}, falling back to generic parsing engine.")
            return self._parse_generic_file(data)
    
    def _parse_generic_file(self, data: List[Dict]) -> List[Dict]:
        """Fallback framework for non-standardized dataset schemas."""
        reviews = []
        for item in data:
            try:
                review_text = self._get_flexible_field(item, '', self.fallback_text_keys)
                if review_text:
                    reviews.append({
                        'source': 'unknown',
                        'review_text': str(review_text).strip(),
                        'rating': self._get_flexible_field(item, '', self.fallback_rating_keys),
                        'timestamp': self._get_flexible_field(item, '', self.fallback_time_keys) or datetime.utcnow().isoformat()
                    })
            except Exception as e:
                print(f"Error parsing generic row item: {e}")
                continue
        return reviews
    
    def read_all_files(self) -> List[Dict]:
        """Scan, read, parse, process, and output details for all data files."""
        if not os.path.exists(self.data_folder):
            print(f"Data folder '{self.data_folder}' not found.")
            return []
        
        all_reviews = []
        json_files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        
        print(f"Found {len(json_files)} JSON files in '{self.data_folder}'")
        
        for filename in json_files:
            file_path = os.path.join(self.data_folder, filename)
            print(f"\nProcessing file: {filename}")
            
            reviews = self._parse_file(file_path)
            print(f"  Extracted {len(reviews)} raw reviews")
            all_reviews.extend(reviews)
        
        # Preprocessing run
        # NOTE: If counts are zero here, test by temporarily dropping min_words to 0
        filtered_reviews = self.preprocessor.filter_reviews(all_reviews, min_words=10)
        
        print(f"\n--- Aggregation Summary ---")
        print(f"Total reviews extracted: {len(all_reviews)}")
        print(f"After preprocessing: {len(filtered_reviews)} reviews")
        
        source_counts = {}
        for r in filtered_reviews:
            source = r.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        print(f"Source breakdown: {source_counts}")
        
        return filtered_reviews
    
    def read_file(self, filename: str) -> List[Dict]:
        """Read a single targets isolated file directly from the active directory data pool."""
        file_path = os.path.join(self.data_folder, filename)
        if not os.path.exists(file_path):
            print(f"File '{filename}' not found in '{self.data_folder}'")
            return []
        
        reviews = self._parse_file(file_path)
        filtered_reviews = self.preprocessor.filter_reviews(reviews, min_words=10)
        return filtered_reviews


def main():
    service = FileReaderService()
    reviews = service.read_all_files()
    
    print(f"\n=== Sample Output Data (Top 5 Head Entries) ===")
    for i, review in enumerate(reviews[:5], 1):
        print(f"\nReview {i}:")
        print(f"Source: {review['source']}")
        print(f"Rating: {review.get('rating', 'N/A')}")
        print(f"Text: {review['review_text'][:120]}...")


if __name__ == "__main__":
    main()