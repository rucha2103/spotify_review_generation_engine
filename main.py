"""
FastAPI application for Spotify Insights API.
Provides endpoints for retrieving and updating research insights.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import os

from json_storage import JSONStorage
from analysis_service import AnalysisService

app = FastAPI(
    title="Spotify Insights API",
    description="API for AI-Powered Product Discovery Engine",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response Models
class InsightMetadata(BaseModel):
    total_reviews_analyzed: int
    last_updated: str


class Insight(BaseModel):
    question_id: str
    question_text: str
    insight_summary: str
    key_findings: List[str]
    metadata: InsightMetadata


class RefreshResponse(BaseModel):
    insights: List[Insight]
    message: str
    reviews_processed: int
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_connected: bool


# Endpoints
@app.get("/insights", response_model=List[Insight])
async def get_insights():
    """
    Retrieve all 6 insight JSON objects from JSON storage.
    
    Returns:
        List of 6 insight objects with metadata including total_reviews_analyzed
    """
    storage = JSONStorage()
    try:
        insights_dict = storage.load_insights()
        
        if not insights_dict:
            raise HTTPException(status_code=404, detail="No insights found in storage")
        
        # Convert to response model
        response_insights = []
        for question_id, insight in insights_dict.items():
            response_insights.append({
                "question_id": insight["question_id"],
                "question_text": insight["question_text"],
                "insight_summary": insight["insight_summary"],
                "key_findings": insight["key_findings"],
                "metadata": {
                    "total_reviews_analyzed": insight["metadata"]["total_reviews_analyzed"],
                    "last_updated": insight["metadata"]["last_updated"]
                }
            })
        
        return response_insights
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving insights: {str(e)}")


@app.post("/refresh-insights", response_model=RefreshResponse)
async def refresh_insights(background_tasks: BackgroundTasks):
    """
    Trigger the full refresh workflow.
    
    Workflow:
    1. Fetch current insights from DB
    2. Read files from 'Data from scraping' folder
    3. Store new reviews in raw_reviews table
    4. Call analysis_service.update_insights()
    5. Return refreshed insights
    
    Returns:
        Updated list of 6 insight objects with metadata including total_reviews_analyzed
    """
    try:
        # Initialize analysis service
        analysis_service = AnalysisService()
        
        # Run the update workflow
        updated_insights = analysis_service.update_insights()
        
        # Calculate total reviews processed
        total_reviews = sum(
            insight["metadata"]["total_reviews_analyzed"] 
            for insight in updated_insights
        )
        
        # Convert to response model
        response_insights = []
        for insight in updated_insights:
            response_insights.append({
                "question_id": insight["question_id"],
                "question_text": insight["question_text"],
                "insight_summary": insight["insight_summary"],
                "key_findings": insight["key_findings"],
                "metadata": {
                    "total_reviews_analyzed": insight["metadata"]["total_reviews_analyzed"],
                    "last_updated": insight["metadata"]["last_updated"]
                }
            })
        
        return RefreshResponse(
            insights=response_insights,
            message="Insights updated successfully",
            reviews_processed=total_reviews,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        print(f"Error in refresh_insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error refreshing insights: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Service status including storage availability
    """
    storage = JSONStorage()
    try:
        # Test storage availability
        insights = storage.load_insights()
        storage_available = True
    except Exception:
        storage_available = False
    
    return HealthResponse(
        status="healthy" if storage_available else "unhealthy",
        timestamp=datetime.utcnow().isoformat(),
        database_connected=storage_available
    )


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Spotify Insights API",
        "version": "1.0.0",
        "description": "AI-Powered Product Discovery Engine for Spotify",
        "endpoints": {
            "GET /insights": "Retrieve all 6 insight JSON objects",
            "POST /refresh-insights": "Trigger insight refresh workflow",
            "GET /health": "Health check endpoint"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
