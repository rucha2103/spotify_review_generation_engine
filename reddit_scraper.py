"""
Reddit scraper for Spotify-related discussions.
Implements intent filter with negative sentiment keywords.
Fetches posts from the past 3 days only.
"""
import os
import asyncio
from typing import List, Dict
from datetime import datetime, timedelta
import praw


class RedditScraper:
    """
    Scraper for Reddit discussions about Spotify.
    Uses intent filter to surface posts with negative sentiment.
    """
    
    # Search terms with negative/intent keywords
    SEARCH_TERMS = [
        "Spotify recommendation engine feedback",
        "Spotify discovery issues complaint",
        "Spotify music recommendation frustration",
        "How to fix Spotify recommendations",
        "Spotify algorithm repetitive fix"
    ]
    
    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = os.getenv("REDDIT_USER_AGENT", "SpotifyInsightBot/1.0")
        self.reddit = None
        self.days_window = 3  # Fetch posts from past 3 days
        self.min_reviews = 40000  # Minimum posts to fetch
    
    def _initialize_reddit(self):
        """
        Initialize the Reddit API client.
        """
        if not self.client_id or not self.client_secret:
            print("Reddit credentials not found. Skipping Reddit scraping.")
            return None
        
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            return self.reddit
        except Exception as e:
            print(f"Error initializing Reddit client: {e}")
            return None
    
    async def fetch_reviews(self, limit: int = 40000) -> List[Dict]:
        """
        Fetch posts from Reddit using search terms.
        
        Args:
            limit: Maximum number of posts to fetch (default: 40,000)
            
        Returns:
            List of post dictionaries from past 3 days only
        """
        reviews = []
        reddit = self._initialize_reddit()
        cutoff_date = datetime.utcnow() - timedelta(days=self.days_window)
        
        if not reddit:
            return reviews
        
        try:
            # Search for each term
            for search_term in self.SEARCH_TERMS:
                if len(reviews) >= limit:
                    break
                
                try:
                    # Search Reddit
                    for submission in reddit.subreddit("all").search(
                        search_term,
                        limit=limit // len(self.SEARCH_TERMS),
                        sort='new'
                    ):
                        if len(reviews) >= limit:
                            break
                        
                        # Parse the submission
                        review = self._parse_submission(submission)
                        if not review:
                            continue
                        
                        # Apply date filter (past 3 days only)
                        submission_date = self._parse_submission_date(submission)
                        if submission_date and submission_date < cutoff_date:
                            continue
                        
                        reviews.append(review)
                
                except Exception as e:
                    print(f"Error searching for term '{search_term}': {e}")
                    continue
        
        except Exception as e:
            print(f"Error fetching Reddit posts: {e}")
        
        return reviews
    
    def _parse_submission(self, submission) -> Dict:
        """
        Parse a Reddit submission into a review format.
        """
        try:
            # Combine title and selftext for full content
            title = submission.title if hasattr(submission, 'title') else ''
            content = submission.selftext if hasattr(submission, 'selftext') else ''
            
            # Use title if selftext is empty
            if not content:
                content = title
            else:
                content = f"{title}. {content}"
            
            return {
                'source': 'reddit',
                'review_text': content,
                'rating': None,  # Reddit doesn't have ratings
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error parsing submission: {e}")
        
        return None
    
    def _parse_submission_date(self, submission) -> datetime:
        """
        Parse the submission date from the Reddit submission.
        """
        try:
            if hasattr(submission, 'created_utc'):
                return datetime.fromtimestamp(submission.created_utc)
        except Exception as e:
            print(f"Error parsing submission date: {e}")
        
        return None
    
    async def scrape(self, limit: int = 40000) -> List[Dict]:
        """
        Main scraping method.
        """
        return await self.fetch_reviews(limit)
