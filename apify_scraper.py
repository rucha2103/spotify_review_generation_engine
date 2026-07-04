"""
Apify Scraper Service - Timestamped Edition
Fetches reviews and saves them with a unique timestamp for every run.
"""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ApifyScraper:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("APIFY_API_KEY")
        if not self.api_key:
            raise ValueError("APIFY_API_KEY not found in environment variables")
        
        self.client = ApifyClient(self.api_key)
        self.output_folder = "Data from scraping"
        
        # Ensure directory exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            
        # Generate a unique timestamp for this run (e.g., 2026-07-04_1625)
        self.run_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        
        self.actors = {
            "app_store": "seemuapps/apple-app-store-reviews-scraper",
            "google_play": "solidcode/google-play-store-reviews-scraper", 
            "reddit": "spry_wholemeal/reddit-scraper"
        }
        
        self.reddit_search_terms = [
            "Spotify recommendation engine feedback",
            "Spotify discovery issues complaint"
        ]

    def _save_to_local_file(self, base_name: str, data: List[Dict]):
        """Saves data to a file with a timestamp suffix."""
        filename = f"{base_name}_{self.run_timestamp}.json"
        file_path = os.path.join(self.output_folder, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved: {file_path}")
        except Exception as e:
            print(f"Failed to save {filename}: {e}")

    def fetch_app_store_reviews(self, app_id: str = "324684580", max_reviews: int = 100) -> List[Dict]:
        print(f"Fetching App Store reviews (Limit: {max_reviews})")
        run_input = {"appId": app_id, "rating": [1, 2, 3], "maxItems": max_reviews}
        run = self.client.actor(self.actors['app_store']).call(run_input=run_input)
        
        reviews = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            reviews.append({
                "source": "app_store",
                "review_text": item.get("title", "") + " " + item.get("body", ""),
                "rating": item.get("rating"),
                "timestamp": item.get("date", datetime.utcnow().isoformat())
            })
        
        final_reviews = reviews[:max_reviews]
        self._save_to_local_file("apify_app_store_reviews", final_reviews)
        return final_reviews
    
    def fetch_google_play_reviews(self, app_id: str = "com.spotify.music", max_reviews: int = 100) -> List[Dict]:
        print(f"Fetching Google Play reviews (Limit: {max_reviews})")
        run_input = {"appIdsOrUrls": [app_id], "minRating": 1, "maxItems": max_reviews}
        run = self.client.actor(self.actors['google_play']).call(run_input=run_input)
        
        reviews = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            reviews.append({
                "source": "google_play",
                "review_text": item.get("text", ""),
                "rating": item.get("score"),
                "timestamp": item.get("date", datetime.utcnow().isoformat())
            })
        
        final_reviews = reviews[:max_reviews]
        self._save_to_local_file("apify_google_play_reviews", final_reviews)
        return final_reviews
    
    def fetch_reddit_posts(self, max_posts: int = 100) -> List[Dict]:
        print(f"Fetching Reddit posts (Limit: {max_posts})")
        run_input = {
            "mode": "search", 
            "searchTargets": [{"query": self.reddit_search_terms[0], "maxResults": max_posts}], 
            "includeCommentsMode": "none"
        }
        run = self.client.actor(self.actors['reddit']).call(run_input=run_input)
        
        posts = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            posts.append({
                "source": "reddit",
                "review_text": f"{item.get('title', '')} {item.get('selftext', item.get('body', ''))}".strip(),
                "timestamp": item.get("createdAt", datetime.utcnow().isoformat()),
                "url": item.get("url", "")
            })
        
        final_posts = posts[:max_posts]
        self._save_to_local_file("apify_reddit_posts", final_posts)
        return final_posts
    
    def run_all(self, max_reviews: int = 100):
        self.fetch_app_store_reviews(max_reviews=max_reviews)
        self.fetch_google_play_reviews(max_reviews=max_reviews)
        self.fetch_reddit_posts(max_posts=max_reviews)
        print(f"\nFinished. All files saved to: {self.output_folder}")

if __name__ == "__main__":
    try:
        scraper = ApifyScraper()
        scraper.run_all(max_reviews=100)
    except Exception as e:
        print(f"An error occurred: {e}")