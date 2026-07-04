"""
Main scraping service orchestrator.
Runs three asynchronous scrapers in parallel and applies preprocessing.
"""
import asyncio
from typing import List, Dict
from app_store_scraper import AppStoreScraper
from google_play_scraper import GooglePlayScraper
from reddit_scraper import RedditScraper
from preprocessor import ReviewPreprocessor


class ScraperService:
    """
    Orchestrates scraping from multiple sources:
    - Apple App Store
    - Google Play Store
    - Reddit
    
    Applies preprocessing including:
    - Negative sentiment bias (1-3 star reviews)
    - Intent filter (Reddit search terms)
    - Minimum word count (10 words)
    - Deduplication
    """
    
    def __init__(self):
        self.app_store_scraper = AppStoreScraper()
        self.google_play_scraper = GooglePlayScraper()
        self.reddit_scraper = RedditScraper()
        self.preprocessor = ReviewPreprocessor()
    
    async def scrape_all_sources(self, limit_per_source: int = 40000) -> List[Dict]:
        """
        Scrape all three sources in parallel.
        
        Args:
            limit_per_source: Maximum reviews to fetch from each source (default: 40,000)
            
        Returns:
            Combined and preprocessed list of reviews
        """
        # Run all scrapers in parallel
        tasks = [
            self.app_store_scraper.scrape(limit_per_source),
            self.google_play_scraper.scrape(limit_per_source),
            self.reddit_scraper.scrape(limit_per_source)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_reviews = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Scraper error: {result}")
            elif isinstance(result, list):
                all_reviews.extend(result)
        
        # Apply preprocessing
        filtered_reviews = self.preprocessor.filter_reviews(all_reviews, min_words=10)
        
        print(f"Scraped {len(all_reviews)} total reviews")
        print(f"After preprocessing: {len(filtered_reviews)} reviews")
        
        return filtered_reviews
    
    async def scrape_app_store(self, limit: int = 40000) -> List[Dict]:
        """
        Scrape only Apple App Store.
        """
        reviews = await self.app_store_scraper.scrape(limit)
        return self.preprocessor.filter_reviews(reviews, min_words=10)
    
    async def scrape_google_play(self, limit: int = 40000) -> List[Dict]:
        """
        Scrape only Google Play Store.
        """
        reviews = await self.google_play_scraper.scrape(limit)
        return self.preprocessor.filter_reviews(reviews, min_words=10)
    
    async def scrape_reddit(self, limit: int = 40000) -> List[Dict]:
        """
        Scrape only Reddit.
        """
        reviews = await self.reddit_scraper.scrape(limit)
        return self.preprocessor.filter_reviews(reviews, min_words=10)


# Convenience function for standalone usage
async def main():
    """
    Main function for testing the scraper service.
    """
    service = ScraperService()
    reviews = await service.scrape_all_sources(limit_per_source=20)
    
    print(f"\n=== Scraped {len(reviews)} reviews ===")
    for i, review in enumerate(reviews[:5], 1):
        print(f"\nReview {i}:")
        print(f"Source: {review['source']}")
        print(f"Rating: {review.get('rating', 'N/A')}")
        print(f"Text: {review['review_text'][:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
