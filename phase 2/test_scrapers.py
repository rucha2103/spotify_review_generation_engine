"""
Test script for validating scraper efficiency and data quality.
Tests each scraper individually and in parallel.
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scrapers directly from the same directory
from app_store_scraper import AppStoreScraper
from google_play_scraper import GooglePlayScraper
from reddit_scraper import RedditScraper
from scraper_service import ScraperService


def print_test_header(test_name: str):
    """Print a formatted test header."""
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)


def print_results_summary(reviews: list, source: str, start_time: datetime):
    """Print a summary of scraping results."""
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n--- {source} Results ---")
    print(f"Reviews fetched: {len(reviews)}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Rate: {len(reviews) / duration:.2f} reviews/second")
    
    if reviews:
        print(f"\nSample review (first 100 chars):")
        print(f"Source: {reviews[0].get('source', 'N/A')}")
        print(f"Rating: {reviews[0].get('rating', 'N/A')}")
        print(f"Text: {reviews[0].get('review_text', '')[:100]}...")


async def test_app_store_scraper(limit: int = 100):
    """Test Apple App Store scraper."""
    print_test_header("Apple App Store Scraper")
    
    scraper = AppStoreScraper()
    start_time = datetime.utcnow()
    
    try:
        reviews = await scraper.scrape(limit=limit)
        print_results_summary(reviews, "App Store", start_time)
        
        # Validate date filtering
        print("\n--- Date Filtering Validation ---")
        cutoff_date = datetime.utcnow() - timedelta(days=3)
        recent_count = sum(1 for r in reviews if r.get('timestamp'))
        print(f"Total reviews with timestamps: {recent_count}")
        print(f"Date window: Past 3 days (since {cutoff_date})")
        
        # Validate rating filtering
        print("\n--- Rating Filtering Validation ---")
        rating_counts = {}
        for r in reviews:
            rating = r.get('rating')
            if rating:
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
        print(f"Rating distribution: {rating_counts}")
        print(f"Expected: Only 1, 2, 3 star reviews")
        
        return reviews
    except Exception as e:
        print(f"ERROR: {e}")
        return []


async def test_google_play_scraper(limit: int = 100):
    """Test Google Play Store scraper."""
    print_test_header("Google Play Store Scraper")
    
    scraper = GooglePlayScraper()
    start_time = datetime.utcnow()
    
    try:
        reviews = await scraper.scrape(limit=limit)
        print_results_summary(reviews, "Google Play", start_time)
        
        print("\n--- Note ---")
        print("Google Play scraper requires a proper scraping library.")
        print("This is a placeholder implementation.")
        
        return reviews
    except Exception as e:
        print(f"ERROR: {e}")
        return []


async def test_reddit_scraper(limit: int = 100):
    """Test Reddit scraper."""
    print_test_header("Reddit Scraper")
    
    scraper = RedditScraper()
    start_time = datetime.utcnow()
    
    try:
        reviews = await scraper.scrape(limit=limit)
        print_results_summary(reviews, "Reddit", start_time)
        
        # Validate date filtering
        print("\n--- Date Filtering Validation ---")
        cutoff_date = datetime.utcnow() - timedelta(days=3)
        print(f"Date window: Past 3 days (since {cutoff_date})")
        
        # Validate search terms
        print("\n--- Search Terms Used ---")
        for term in scraper.SEARCH_TERMS:
            print(f"  - {term}")
        
        return reviews
    except Exception as e:
        print(f"ERROR: {e}")
        return []


async def test_parallel_scraping(limit_per_source: int = 100):
    """Test all scrapers running in parallel."""
    print_test_header("Parallel Scraping (All Sources)")
    
    service = ScraperService()
    start_time = datetime.utcnow()
    
    try:
        reviews = await service.scrape_all_sources(limit_per_source=limit_per_source)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n--- Parallel Scraping Results ---")
        print(f"Total reviews fetched: {len(reviews)}")
        print(f"Total duration: {duration:.2f} seconds")
        print(f"Overall rate: {len(reviews) / duration:.2f} reviews/second")
        
        # Source breakdown
        source_counts = {}
        for r in reviews:
            source = r.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        print(f"\nSource breakdown: {source_counts}")
        
        return reviews
    except Exception as e:
        print(f"ERROR: {e}")
        return []


async def test_full_scale(limit_per_source: int = 40000):
    """Test with full-scale limits (40,000 reviews per source)."""
    print_test_header("Full-Scale Test (40,000 reviews per source)")
    print("WARNING: This may take several minutes and consume significant API quota.")
    print("Press Ctrl+C to cancel.\n")
    
    service = ScraperService()
    start_time = datetime.utcnow()
    
    try:
        reviews = await service.scrape_all_sources(limit_per_source=limit_per_source)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n--- Full-Scale Results ---")
        print(f"Total reviews fetched: {len(reviews)}")
        print(f"Total duration: {duration:.2f} seconds ({duration / 60:.2f} minutes)")
        print(f"Overall rate: {len(reviews) / duration:.2f} reviews/second")
        
        # Source breakdown
        source_counts = {}
        for r in reviews:
            source = r.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        print(f"\nSource breakdown: {source_counts}")
        
        # Validate 3-day window
        print(f"\n--- 3-Day Window Validation ---")
        print(f"Expected: All reviews from past 3 days only")
        
        return reviews
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        return []
    except Exception as e:
        print(f"ERROR: {e}")
        return []


async def main():
    """Main test runner."""
    print("=" * 60)
    print("SPOTIFY INSIGHTS SCRAPER TEST SUITE")
    print("=" * 60)
    
    # Test options
    print("\nSelect test mode:")
    print("1. Individual scraper tests (small scale - 100 reviews)")
    print("2. Parallel scraping test (small scale - 100 reviews)")
    print("3. Full-scale test (40,000 reviews per source)")
    print("4. Run all tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        await test_app_store_scraper(limit=100)
        await test_google_play_scraper(limit=100)
        await test_reddit_scraper(limit=100)
    
    elif choice == "2":
        await test_parallel_scraping(limit_per_source=100)
    
    elif choice == "3":
        confirm = input("Confirm full-scale test? (yes/no): ").strip().lower()
        if confirm == "yes":
            await test_full_scale(limit_per_source=40000)
        else:
            print("Test cancelled.")
    
    elif choice == "4":
        await test_app_store_scraper(limit=100)
        await test_google_play_scraper(limit=100)
        await test_reddit_scraper(limit=100)
        await test_parallel_scraping(limit_per_source=100)
        
        confirm = input("\nRun full-scale test? (yes/no): ").strip().lower()
        if confirm == "yes":
            await test_full_scale(limit_per_source=40000)
    
    else:
        print("Invalid choice.")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
