"""
Analysis service for updating insights using LLM.
Loads existing insights, processes new reviews, and updates JSON storage.
"""
from typing import List, Dict
from datetime import datetime
from llm_client import LLMClient
from validator import InsightValidator
from file_reader_service import FileReaderService
from json_storage import JSONStorage


class AnalysisService:
    """
    Service for analyzing reviews and updating insights using LLM.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.file_reader = FileReaderService()
        self.storage = JSONStorage()
    
    def load_existing_insights(self) -> Dict[str, Dict]:
        """
        Load all 6 existing insights from JSON storage.
        
        Returns:
            Dictionary mapping question_id to insight JSON
        """
        return self.storage.load_insights()
    
    def load_new_reviews(self) -> List[Dict]:
        """
        Load new reviews from the 'Data from scraping' folder.
        
        Returns:
            List of review dictionaries
        """
        reviews = self.file_reader.read_all_files()
        return reviews
    
    def store_reviews_in_db(self, reviews: List[Dict]):
        """
        Store new reviews in JSON storage.
        
        Args:
            reviews: List of review dictionaries
        """
        self.storage.append_reviews(reviews)
        print(f"Stored {len(reviews)} reviews in JSON storage")
    
    def craft_llm_prompt(self, existing_insights: Dict[str, Dict], new_reviews: List[Dict]) -> str:
        """
        Craft the prompt for the LLM to update insights.
        
        Args:
            existing_insights: Dictionary of current insights
            new_reviews: List of new review dictionaries
            
        Returns:
            The prompt string
        """
        # Format existing insights
        existing_insights_str = json.dumps(existing_insights, indent=2)
        
        # Format new reviews (limit to prevent token overflow)
        reviews_sample = new_reviews[:500]  # Limit to 500 reviews for prompt
        reviews_str = "\n".join([
            f"Source: {r['source']}\nText: {r['review_text']}\nRating: {r.get('rating', 'N/A')}\n"
            for r in reviews_sample
        ])
        
        prompt = f"""You are an expert Growth Product Manager specializing in music streaming services. 

I have historical data (current insights) and new data (user reviews). Your task is to update the insights based on the new data.

CURRENT INSIGHTS:
{existing_insights_str}

NEW REVIEWS (sample of {len(reviews_sample)} reviews):
{reviews_str}

Total new reviews to analyze: {len(new_reviews)}

INSTRUCTIONS:
1. Update the 'insight_summary' for each question based on patterns in the new reviews
2. Update the 'key_findings' list with new findings from the reviews
3. Calculate the new 'total_reviews_analyzed' by adding the count of new reviews to the previous total
4. Update the 'last_updated' timestamp to the current time
5. Maintain the exact same JSON structure for all 6 insights
6. Output must be a valid JSON array containing exactly 6 insight objects
7. Do not include markdown formatting or code blocks - output raw JSON only

The 6 research questions are:
- Q1: Why do users struggle to discover new music?
- Q2: What are the most common frustrations with recommendations?
- Q3: What listening behaviors are users trying to achieve?
- Q4: What causes users to repeatedly listen to the same content?
- Q5: Which user segments experience different discovery challenges?
- Q6: What unmet needs emerge consistently across reviews?

Output the updated insights as a JSON array."""
        
        return prompt
    
    def update_insights(self) -> List[Dict]:
        """
        Main workflow to update insights:
        1. Run Apify Scraper to get fresh data
        2. If successful, use those 3 new files. If failed, pick 3 random files.
        3. Load reviews, send to LLM, validate, update insights
        """
        print("=== Starting Insight Update Workflow ===")
        
        # Step 1: Load existing insights
        existing_insights = self.load_existing_insights()
        
        # Step 2: Run Apify Scraper
        from apify_scraper import ApifyScraper
        import os
        import random
        newly_created_files = []
        try:
            print("\nStep 2: Running Apify Scraper for fresh data...")
            scraper = ApifyScraper()
            # This triggers the fetch and creates the files in 'Data from scraping'
            scraper.run_all(max_reviews=100)
            
            # Identify the 3 files created by this run (matching the timestamp)
            ts = scraper.run_timestamp
            newly_created_files = [
                f"apify_app_store_reviews_{ts}.json",
                f"apify_google_play_reviews_{ts}.json",
                f"apify_reddit_posts_{ts}.json"
            ]
            print(f"Scrape successful. Processing files: {newly_created_files}")
            
        except Exception as e:
            print(f"\nScraping failed: {e}. Falling back to random file selection...")
            
            data_folder = "Data from scraping"
            all_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
            newly_created_files = random.sample(all_files, min(3, len(all_files)))
            print(f"Randomly selected 3 files: {newly_created_files}")

        # Step 3: Load reviews from the 3 files
        combined_reviews = []
        for filename in newly_created_files:
            file_path = os.path.join("Data from scraping", filename)
            if os.path.exists(file_path):
                print(f"File found : {file_path} : {os.path.getsize(file_path)} bytes")
                reviews = self.file_reader.read_file(filename)
                combined_reviews.extend(reviews)
            else :
                print(f"File not found : {file_path}")
        
        print(f"Total reviews aggregated for analysis: {len(combined_reviews)}")
        
        if not combined_reviews:
            print("No reviews found to analyze.")
            return list(existing_insights.values())

        # Step 4: Store reviews and trigger LLM
        self.store_reviews_in_db(combined_reviews)
        
        print("Crafting LLM prompt...")
        prompt = self.craft_llm_prompt(existing_insights, combined_reviews)
        
        print("Sending to Gemini API for analysis...")
        response = self.llm_client.generate_json_response(prompt, temperature=0.7)
        
        print("Validating LLM response...")
        is_valid, updated_insights, error = InsightValidator.parse_and_validate_json(response)
        
        if not is_valid:
            raise ValueError(f"LLM response validation failed: {error}")
        
        self.update_database_insights(updated_insights)
        print("=== Insight Update Workflow Complete ===")
        
        return updated_insights

    def update_database_insights(self, insights: List[Dict]):
        """
        Update JSON storage with new insights.
        
        Args:
            insights: List of 6 insight JSON objects
        """
        self.storage.save_insights(insights)
        print(f"Updated {len(insights)} insights in JSON storage")


import json  # Import json for prompt crafting


# Convenience function for standalone usage
def main():
    """
    Main function for testing the analysis service.
    """
    service = AnalysisService()
    
    try:
        updated_insights = service.update_insights()
        
        print("\n=== Updated Insights ===")
        for insight in updated_insights:
            print(f"\n{insight['question_id']}: {insight['question_text']}")
            print(f"Summary: {insight['insight_summary'][:200]}...")
            print(f"Total reviews analyzed: {insight['metadata']['total_reviews_analyzed']}")
    
    except Exception as e:
        print(f"Error in analysis workflow: {e}")


if __name__ == "__main__":
    main()
