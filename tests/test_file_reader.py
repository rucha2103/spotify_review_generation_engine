"""
Unit tests for file reader service.
"""
import pytest
import sys
import os
import json
import tempfile

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_reader_service import FileReaderService


class TestFileReaderService:
    """Test FileReaderService class."""
    
    def test_initialization(self):
        """Test file reader initialization."""
        service = FileReaderService()
        assert service.data_folder == "Data from scraping"
        assert service.preprocessor is not None
    
    def test_initialization_custom_folder(self):
        """Test file reader initialization with custom folder."""
        service = FileReaderService(data_folder="custom_folder")
        assert service.data_folder == "custom_folder"
    
    def test_detect_file_type_reddit(self):
        """Test Reddit file type detection."""
        service = FileReaderService()
        assert service._detect_file_type("reddit_data.json") == "reddit"
        assert service._detect_file_type("dataset_reddit-scraper.json") == "reddit"
    
    def test_detect_file_type_app_store(self):
        """Test App Store file type detection."""
        service = FileReaderService()
        assert service._detect_file_type("appstore_reviews.json") == "app_store"
        assert service._detect_file_type("spotify_appstore_reviews.json") == "app_store"
    
    def test_detect_file_type_google_play(self):
        """Test Google Play file type detection."""
        service = FileReaderService()
        assert service._detect_file_type("google_play_reviews.json") == "google_play"
        assert service._detect_file_type("play_store_data.json") == "google_play"
    
    def test_detect_file_type_unknown(self):
        """Test unknown file type detection."""
        service = FileReaderService()
        assert service._detect_file_type("unknown_file.json") == "unknown"
    
    def test_parse_reddit_file(self):
        """Test parsing Reddit file format."""
        service = FileReaderService()
        
        data = [
            {
                "id": "test1",
                "title": "Test post",
                "body": "Test content",
                "createdAt": "2026-06-21T12:00:00Z"
            },
            {
                "dataType": "community",  # Should be skipped
                "name": "test_subreddit"
            }
        ]
        
        reviews = service._parse_reddit_file(data)
        
        assert len(reviews) == 1  # Community entry should be skipped
        assert reviews[0]["source"] == "reddit"
        assert "Test post" in reviews[0]["review_text"]
        assert "Test content" in reviews[0]["review_text"]
    
    def test_parse_app_store_file(self):
        """Test parsing App Store file format."""
        service = FileReaderService()
        
        data = [
            {
                "review": "Great app",
                "rating": 5,
                "date": "2026-06-21"
            },
            {
                "body": "Good app",
                "score": 4,
                "created_at": "2026-06-21"
            }
        ]
        
        reviews = service._parse_app_store_file(data)
        
        assert len(reviews) == 2
        assert reviews[0]["source"] == "app_store"
        assert reviews[0]["review_text"] == "Great app"
        assert reviews[0]["rating"] == 5
    
    def test_parse_google_play_file(self):
        """Test parsing Google Play file format."""
        service = FileReaderService()
        
        data = [
            {
                "review": "Good app",
                "rating": 4,
                "date": "2026-06-21"
            }
        ]
        
        reviews = service._parse_google_play_file(data)
        
        assert len(reviews) == 1
        assert reviews[0]["source"] == "google_play"
        assert reviews[0]["review_text"] == "Good app"
        assert reviews[0]["rating"] == 4
    
    def test_parse_generic_file(self):
        """Test parsing generic file format."""
        service = FileReaderService()
        
        data = [
            {
                "review_text": "Generic review",
                "rating": 3,
                "timestamp": "2026-06-21T12:00:00"
            }
        ]
        
        reviews = service._parse_generic_file(data)
        
        assert len(reviews) == 1
        assert reviews[0]["source"] == "unknown"
        assert reviews[0]["review_text"] == "Generic review"
    
    def test_read_json_file(self):
        """Test reading JSON file."""
        service = FileReaderService()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{"test": "data"}], f)
            temp_path = f.name
        
        try:
            data = service._read_json_file(temp_path)
            assert len(data) == 1
            assert data[0]["test"] == "data"
        finally:
            os.unlink(temp_path)
    
    def test_read_json_file_invalid(self):
        """Test reading invalid JSON file."""
        service = FileReaderService()
        
        # Create temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name
        
        try:
            data = service._read_json_file(temp_path)
            assert len(data) == 0  # Should return empty list on error
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
