"""
Configuration management for Spotify Insights Engine.
Loads environment variables and provides configuration access.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # LLM API
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Frontend Configuration
    FRONTEND_API_URL: str = os.getenv("FRONTEND_API_URL", "http://localhost:8000")
    
    # Data Configuration
    DATA_FOLDER: str = "Data from scraping"
    STORAGE_FOLDER: str = "data"  # JSON storage folder
    
    # Analysis Configuration
    MAX_REVIEWS_FOR_PROMPT: int = 500  # Limit reviews sent to LLM to prevent token overflow
    MIN_WORD_COUNT: int = 10  # Minimum word count for review filtering
    
    # Scraper Configuration (for reference, not used in file-based approach)
    DAYS_WINDOW: int = 3  # Days window for scraping
    MIN_REVIEWS_PER_SOURCE: int = 40000  # Minimum reviews to fetch per source
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Check LLM API key
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            print("ERROR: GEMINI_API_KEY not found")
            return False
        
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            print("ERROR: GROQ_API_KEY not found")
            return False
        
        # Check data folder
        if not os.path.exists(cls.DATA_FOLDER):
            print(f"WARNING: Data folder '{cls.DATA_FOLDER}' not found")
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)."""
        print("=== Configuration ===")
        print(f"LLM Provider: {cls.LLM_PROVIDER}")
        print(f"API Host: {cls.API_HOST}:{cls.API_PORT}")
        print(f"Frontend API URL: {cls.FRONTEND_API_URL}")
        print(f"Data Folder: {cls.DATA_FOLDER}")
        print(f"Storage Folder: {cls.STORAGE_FOLDER}")
        print(f"Max Reviews for Prompt: {cls.MAX_REVIEWS_FOR_PROMPT}")
        print(f"Min Word Count: {cls.MIN_WORD_COUNT}")
        print("====================")


# Create a singleton instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    Config.print_config()
    is_valid = Config.validate()
    print(f"\nConfiguration valid: {is_valid}")
