"""
Apple App Store scraper for Spotify reviews.
Implements negative sentiment bias (1-3 star reviews only).
Fetches reviews from the past 3 days only.
"""
import os
import asyncio
import aiohttp
from typing import List, Dict
from datetime import datetime, timedelta


class AppStoreScraper:
    """
    Scraper for Apple App Store reviews.
    Filters to only 1-star, 2-star, and 3-star reviews.
    """
    
    def __init__(self, app_id: str = None):
        self.app_id = app_id or os.getenv("APPLE_APP_ID", "324684580")
        self.base_url = f"https://itunes.apple.com/us/rss/customerreviews/page=1/id={self.app_id}/sortBy=mostRecent/json"
        self.rating_filter = [1, 2, 3]  # Negative sentiment bias
        self.days_window = 3  # Fetch reviews from past 3 days
        self.min_reviews = 40000  # Minimum reviews to fetch
    
    async def fetch_reviews(self, limit: int = 40000) -> List[Dict]:
        """
        Fetch reviews from Apple App Store.
        
        Args:
            limit: Maximum number of reviews to fetch (default: 40,000)
            
        Returns:
            List of review dictionaries from past 3 days only
        """
        reviews = []
        cutoff_date = datetime.utcnow() - timedelta(days=self.days_window)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        entries = data.get('feed', {}).get('entry', [])
                        
                        for entry in entries:
                            if len(reviews) >= limit:
                                break
                            
                            # Extract review data
                            review = self._parse_review(entry)
                            
                            if not review:
                                continue
                            
                            # Apply rating filter (1-3 stars only)
                            if review.get('rating') not in self.rating_filter:
                                continue
                            
                            # Apply date filter (past 3 days only)
                            review_date = self._parse_review_date(entry)
                            if review_date and review_date < cutoff_date:
                                continue
                            
                            reviews.append(review)
        
        except Exception as e:
            print(f"Error fetching App Store reviews: {e}")
        
        return reviews
    
    def _parse_review(self, entry: Dict) -> Dict:
        """
        Parse a single review entry from the API response.
        """
        try:
            # Handle both single entry and list cases
            if isinstance(entry, dict) and 'id' in entry:
                rating = int(entry.get('im:rating', {}).get('label', 0))
                title = entry.get('title', {}).get('label', '')
                content = entry.get('content', {}).get('label', '')
                
                # Combine title and content for full review text
                review_text = f"{title}. {content}" if title else content
                
                return {
                    'source': 'app_store',
                    'review_text': review_text,
                    'rating': rating,
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"Error parsing review: {e}")
        
        return None
    
    def _parse_review_date(self, entry: Dict) -> datetime:
        """
        Parse the review date from the API response.
        """
        try:
            if isinstance(entry, dict) and 'updated' in entry:
                date_str = entry.get('updated', {}).get('label', '')
                if date_str:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            print(f"Error parsing review date: {e}")
        
        return None
    
    async def scrape(self, limit: int = 40000) -> List[Dict]:
        """
        Main scraping method.
        """
        return await self.fetch_reviews(limit)
