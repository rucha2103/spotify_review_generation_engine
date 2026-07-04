# Spotify Insights Engine

AI-Powered Product Discovery Engine for Spotify that maintains persistent research insights and updates them dynamically using live data from user reviews.

## Overview

This system analyzes user feedback from multiple sources (Apple App Store, Google Play Store, Reddit) to generate insights about Spotify's product discovery challenges. It uses Gemini AI to synthesize patterns from user reviews and maintain 6 core research questions.

## Features

- **6 Core Research Insights**: Persistent insights on music discovery challenges
- **Multi-Source Data**: Analyzes reviews from App Store, Google Play, and Reddit
- **AI-Powered Analysis**: Uses Gemini AI to synthesize patterns from user feedback
- **File-Based Data Loading**: Reads manually scraped data files for analysis
- **JSON File Storage**: Simple JSON-based storage (no database required)
- **RESTful API**: FastAPI backend with insights and refresh endpoints
- **Modern Frontend**: Streamlit dashboard with interactive cards
- **Metadata Tracking**: Shows total reviews analyzed and last update time

## Architecture

The system is built in 7 phases:

1. **Phase 1**: JSON Storage Setup (Simple file-based storage)
2. **Phase 2**: Scraping Service (Async scrapers with filtering)
3. **Phase 3**: Analysis Service (LLM integration with Gemini)
4. **Phase 4**: API Layer (FastAPI endpoints)
5. **Phase 5**: Frontend (Streamlit dashboard)
6. **Phase 6**: Configuration & Environment Setup
7. **Phase 7**: Testing & Validation

## Project Structure

```
graduation-project-2/
├── json_storage.py                    # JSON file storage service
├── phase 2/                           # Scraping service
│   ├── scraper_service.py
│   ├── app_store_scraper.py
│   ├── google_play_scraper.py
│   ├── reddit_scraper.py
│   ├── preprocessor.py
│   └── test_scrapers.py
├── file_reader_service.py             # File-based data reader
├── llm_client.py                      # Gemini API client
├── validator.py                       # JSON schema validation
├── analysis_service.py                # Main analysis orchestrator
├── main.py                            # FastAPI application
├── frontend.py                        # Streamlit dashboard
├── config.py                          # Configuration management
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .env                               # Your environment variables
├── ARCHITECTURE.md                    # Detailed architecture documentation
└── README.md                          # This file
```

## Prerequisites

- Python 3.8+
- Gemini API key
- (Optional) Reddit API credentials for Reddit scraping

## Installation

1. **Clone the repository**
   ```bash
   cd "Graduation Project 2"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Gemini API key
   ```

5. **Initialize JSON storage**
   ```bash
   python json_storage.py
   ```

6. **Prepare data files**
   ```bash
   # Add your manually scraped JSON files to 'Data from scraping' folder
   # Supported formats: App Store, Google Play, Reddit
   ```

## Usage

### Running the API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

API endpoints:
- `GET /insights` - Retrieve all 6 insight JSON objects
- `POST /refresh-insights` - Trigger insight refresh workflow
- `GET /health` - Health check endpoint
- `GET /` - API information

### Running the Frontend

```bash
streamlit run frontend.py
```

The frontend will be available at `http://localhost:8501`

### Running Analysis Standalone

```bash
python analysis_service.py
```

This will:
1. Load existing insights from database
2. Read files from 'Data from scraping' folder
3. Store reviews in database
4. Send to Gemini API for analysis
5. Update database with new insights

## Data Format

### Input Data Files

Place your manually scraped JSON files in the `Data from scraping` folder. The system automatically detects file type:

- **App Store**: Files containing review data with rating fields
- **Google Play**: Files containing review data with score fields
- **Reddit**: Files containing post data with title and body fields

### Insight JSON Structure

Each insight follows this schema:

```json
{
  "question_id": "Q1",
  "question_text": "Why do users struggle to discover new music?",
  "insight_summary": "Generated insight summary...",
  "key_findings": ["Finding 1", "Finding 2"],
  "metadata": {
    "total_reviews_analyzed": 15000,
    "last_updated": "2026-06-21T12:00:00"
  }
}
```

## The 6 Research Questions

1. **Q1**: Why do users struggle to discover new music?
2. **Q2**: What are the most common frustrations with recommendations?
3. **Q3**: What listening behaviors are users trying to achieve?
4. **Q4**: What causes users to repeatedly listen to the same content?
5. **Q5**: Which user segments experience different discovery challenges?
6. **Q6**: What unmet needs emerge consistently across reviews?

## Configuration

### Environment Variables

```bash
# LLM API
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=gemini

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_API_URL=http://localhost:8000
```

## Deployment

### Backend API (FastAPI)

Deploy using any Python hosting service:
- Render
- Railway
- Heroku
- AWS EC2

### Frontend (Streamlit)

Options for deployment:
1. **Streamlit Cloud**: Recommended for Streamlit apps
2. **Netlify**: Requires conversion to static frontend or experimental Python runtime
3. **Separate hosting**: Deploy API and frontend on different services

### Database

- **Production**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL, etc.)
- **Development**: Local PostgreSQL instance

## Testing

### Test Scrapers (Phase 2)

```bash
cd "phase 2"
python test_scrapers.py
```

### Test Analysis Service

```bash
python analysis_service.py
```

### Test API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test insights endpoint
curl http://localhost:8000/insights

# Test refresh endpoint
curl -X POST http://localhost:8000/refresh-insights
```

## Troubleshooting

### LLM API Errors
- Verify GEMINI_API_KEY is set correctly
- Check API quota and rate limits
- Ensure network connectivity

### File Reading Issues
- Verify 'Data from scraping' folder exists
- Check JSON file format is valid
- Ensure files contain review/post data

### JSON Storage Issues
- Verify 'data' folder exists
- Check file permissions
- Ensure JSON files are valid

### Frontend API Connection
- Update FRONTEND_API_URL in frontend.py
- Ensure API is running on correct port
- Check CORS configuration

## Contributing

This is a graduation project. For questions or issues, please refer to the ARCHITECTURE.md file for detailed implementation documentation.

## License

This project is for educational purposes.

## Acknowledgments

- Gemini AI for LLM capabilities
- Streamlit for frontend framework
- FastAPI for backend framework
- SQLAlchemy for database ORM
