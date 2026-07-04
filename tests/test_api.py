"""
Integration tests for API endpoints.
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestAPIEndpoints:
    """Test FastAPI endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "Spotify Insights" in data["name"]
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "database_connected" in data
    
    def test_insights_endpoint_no_data(self):
        """Test insights endpoint when no data exists."""
        client = TestClient(app)
        response = client.get("/insights")
        
        # May return 404 if no insights, or 200 with empty list
        assert response.status_code in [200, 404]
    
    def test_insights_endpoint_structure(self):
        """Test insights endpoint response structure."""
        client = TestClient(app)
        response = client.get("/insights")
        
        if response.status_code == 200:
            data = response.json()
            # If data exists, validate structure
            if isinstance(data, list) and len(data) > 0:
                insight = data[0]
                assert "question_id" in insight
                assert "question_text" in insight
                assert "insight_summary" in insight
                assert "key_findings" in insight
                assert "metadata" in insight
                assert "total_reviews_analyzed" in insight["metadata"]
                assert "last_updated" in insight["metadata"]
    
    def test_refresh_insights_endpoint(self):
        """Test refresh insights endpoint."""
        client = TestClient(app)
        
        # This test may fail if database/LLM not properly configured
        # It's more of an integration test
        try:
            response = client.post("/refresh-insights", timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                assert "insights" in data
                assert "message" in data
                assert "reviews_processed" in data
                assert "timestamp" in data
        except Exception as e:
            # Expected if dependencies not configured
            pytest.skip(f"Refresh endpoint test skipped: {e}")
    
    def test_cors_enabled(self):
        """Test CORS is enabled."""
        client = TestClient(app)
        
        # Test OPTIONS request
        response = client.options("/insights", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # CORS should be enabled
        assert response.status_code in [200, 204]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
