# AI-Powered Product Discovery Engine for Spotify
## Phase-Wise Implementation Architecture

---

## Project Overview
Build a backend system that maintains a persistent state of 6 specific research insights and updates them dynamically using live data from Apple App Store, Google Play Store, and Reddit.

---

## Phase 1: JSON Storage Setup
**Priority: HIGH** | **Dependencies: None**

### 1.1 Storage Design
- **JSON file storage** as the primary storage mechanism
- Two main JSON files:
  - `data/insights.json`: Stores the 6 JSON insight objects
  - `data/reviews.json`: Stores scraped reviews

### 1.2 JSON Storage Service (`json_storage.py`)
```python
# JSONStorage Class
- load_insights(): Load insights from JSON file
- save_insights(): Save insights to JSON file
- load_reviews(): Load reviews from JSON file
- save_reviews(): Save reviews to JSON file
- append_reviews(): Append new reviews to existing file
- initialize_insights(): Initialize with 6 research questions
```

### 1.3 Storage Initialization Script
- Create `json_storage.py` to initialize JSON storage
- Seed initial 6 insight records with empty/default JSON structures
- Handle file creation and validation

### 1.4 Deliverables
- `json_storage.py` - JSON storage service

---

## Phase 2: Scraping Service
**Priority: HIGH** | **Dependencies: Phase 1**

### 2.1 Scraper Architecture
- Async-based scraping for parallel execution
- Three separate scrapers:
  - Apple App Store Scraper
  - Google Play Store Scraper
  - Reddit Scraper
- **Time Window**: Each scraper fetches reviews from the past 3 days only
- **Volume Requirement**: Each scraper must fetch at least 40,000 reviews per run

### 2.2 Filtering Logic Implementation

#### 2.2.1 Negative Sentiment Bias (App Stores)
- **Star Filter**: Only scrape 1-star, 2-star, and 3-star reviews
- **Configuration**: `rating: [1, 2, 3]`
- **Rationale**: 1-2 star = pure frustration, 3-star = constructive criticism

#### 2.2.2 Intent Filter (Reddit)
- **Search Terms Configuration**:
  ```python
  SEARCH_TERMS = [
    "Spotify recommendation engine feedback",
    "Spotify discovery issues complaint",
    "Spotify music recommendation frustration",
    "How to fix Spotify recommendations",
    "Spotify algorithm repetitive fix"
  ]
  ```
- **Negative Keywords**: "sucks", "fix", "annoying", "frustrated", "why is it so"

### 2.3 Deduplication Logic
- Hash-based deduplication using review text
- Maintain a set of seen review hashes
- Skip duplicate reviews before storage

### 2.4 Pre-processing Pipeline
- Minimum word count filter: Discard reviews < 10 words
- Text normalization (optional): Lowercase, remove special chars
- Validation: Ensure review text is not empty

### 2.5 Deliverables
- `scraper_service.py` - Main scraping orchestrator
- `app_store_scraper.py` - Apple App Store scraper
- `google_play_scraper.py` - Google Play Store scraper
- `reddit_scraper.py` - Reddit scraper
- `preprocessor.py` - Review filtering and deduplication logic
- `file_reader_service.py` - Alternative file-based data reader (for manually scraped data)

### 2.6 Alternative Data Source: File-Based Reading
- **Purpose**: Read manually scraped data files instead of live scraping
- **Location**: `Data from scraping` folder
- **File Types**: JSON files (App Store, Reddit, Google Play formats)
- **Workflow**: When generate insights is called, read files one by one from the folder
- **Parsing**: Automatic detection of file type and format conversion to standard review structure
- **Preprocessing**: Same filtering logic applies (word count, deduplication)

---

## Phase 3: Analysis Service (LLM Integration)
**Priority: HIGH** | **Dependencies: Phase 1, Phase 2**

### 3.1 LLM Integration
- **Provider**: Gemini/Groq (configurable)
- **Prompt Engineering**: Growth PM persona prompt
- **Input**: Historical JSON data + New raw reviews
- **Output**: List of 6 updated JSON objects

### 3.2 Analysis Workflow (`analysis_service.py`)

#### 3.2.1 Load Existing Insights
- Fetch all 6 JSON objects from `insights_state` table
- Parse JSONB content to Python dictionaries

#### 3.2.2 Pre-process New Reviews
- Apply word count filter (> 10 words)
- Remove duplicates
- Format for LLM consumption

#### 3.2.3 Craft LLM Prompt
```
You are an expert Growth PM. You have historical data (Current JSONs) 
and new data (List of Raw Reviews). Update the JSONs.

Logic: 
- Update 'insight_summary' and 'key_findings' based on new data
- Calculate new 'total_reviews_analyzed' (previous total + count of new reviews)
- Update 'last_updated' timestamp
- Output must be a list of 6 updated JSON objects
```

#### 3.2.4 Parse & Validate Response
- Validate JSON structure matches schema
- Ensure all 6 question_ids are present
- Validate metadata fields

#### 3.2.5 Database Update
- Use `db.session.merge()` for upsert operation
- Call `db.session.commit()` to persist changes
- Handle transaction rollback on errors

### 3.3 Error Handling
- Retry logic for LLM API failures
- Fallback to previous insights if LLM fails
- Logging of all LLM interactions

### 3.4 Deliverables
- `analysis_service.py` - Main analysis orchestrator
- `llm_client.py` - LLM API client wrapper
- `validator.py` - JSON schema validation

---

## Phase 4: API Layer
**Priority: HIGH** | **Dependencies: Phase 1, Phase 3**

### 4.1 API Framework
- **Framework**: Flask or FastAPI
- **CORS**: Enabled for frontend integration
- **Error Handling**: Standardized error responses

### 4.2 Endpoints (`main.py`)

#### 4.2.1 GET /insights
- **Purpose**: Retrieve all 6 insight JSON objects
- **Response**: List of 6 JSON objects
- **Cache**: Optional 5-minute cache

#### 4.2.2 POST /refresh-insights
- **Purpose**: Trigger the full refresh workflow
- **Workflow**:
  1. Fetch current insights from DB
  2. Read files from 'Data from scraping' folder (file-based approach)
  3. Store new reviews in `raw_reviews`
  4. Call `analysis_service.update_insights()`
  5. Return refreshed insights
- **Response**: Updated list of 6 JSON objects with metadata (total_reviews_analyzed, last_updated)
- **Timeout**: 60 seconds (async execution)

#### 4.2.3 GET /health (Optional)
- **Purpose**: Health check endpoint
- **Response**: Service status

### 4.3 Async Task Management
- Use Celery or background tasks for long-running scrapes
- Task queue for concurrent scraping
- Status tracking for refresh operations

### 4.4 Deliverables
- `main.py` - API application with endpoints
- `requirements.txt` - Python dependencies
- `config.py` - Configuration management

---

## Phase 5: Frontend (Streamlit)
**Priority: MEDIUM** | **Dependencies: Phase 4**

### 5.1 UI Components
- **Framework**: Streamlit
- **Layout**: 6 cards (one per question_id)

### 5.2 Card Design
Each card displays:
- **Question Text**: The research question
- **Insight Summary**: Generated insight
- **Key Findings**: Bullet list of findings
- **Metadata Badge**: 
  - "Based on [total_reviews_analyzed] reviews"
  - "Last updated: [last_updated]"

### 5.3 Interactive Features
- **Refresh Button**: Triggers POST /refresh-insights
- **Loading State**: Spinner during refresh
- **Error Handling**: Display error messages
- **Auto-refresh**: Optional periodic refresh

### 5.4 Styling
- Modern, clean UI
- Color-coded cards
- Responsive design
- Badge styling for metadata

### 5.5 Deliverables
- `frontend.py` - Streamlit application
- `styles.css` - Custom styling (optional)

### 5.6 Deployment Considerations
- **Netlify Deployment**: Streamlit requires Python runtime. For Netlify deployment:
  - Option 1: Deploy Streamlit on Streamlit Cloud, API on separate server
  - Option 2: Use Netlify Functions with Python runtime (experimental)
  - Option 3: Convert to static frontend (React/Vue) and deploy on Netlify
- **API URL**: Configure `API_URL` in frontend to point to deployed backend

---

## Phase 6: Configuration & Environment Setup
**Priority: MEDIUM** | **Dependencies: None**

### 6.1 Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/spotify_insights

# LLM API
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
LLM_PROVIDER=groq  # or gemini

# Scraper Configuration
APPLE_APP_ID=spotify.app.id
GOOGLE_PLAY_PACKAGE=com.spotify.music
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### 6.2 Project Structure
```
graduation-project-2/
├── models.py
├── init_db.py
├── database.py
├── scraper_service.py
├── app_store_scraper.py
├── google_play_scraper.py
├── reddit_scraper.py
├── preprocessor.py
├── analysis_service.py
├── llm_client.py
├── validator.py
├── main.py
├── frontend.py
├── config.py
├── requirements.txt
├── .env
└── ARCHITECTURE.md
```

### 6.3 Dependencies
```txt
# Core
fastapi
uvicorn
sqlalchemy
psycopg2-binary

# Scraping
requests
asyncio
aiohttp
praw  # Reddit API
app-store-scraper  # or alternative
google-play-scraper  # or alternative

# LLM
groq
google-generativeai

# Frontend
streamlit
requests

# Utilities
python-dotenv
pydantic
```

### 6.4 Deliverables
- `.env.example` - Environment variable template
- `requirements.txt` - Python dependencies
- `README.md` - Setup and usage instructions

---

## Phase 7: Testing & Validation
**Priority: MEDIUM** | **Dependencies: All previous phases**

### 7.1 Unit Tests
- Test SQLAlchemy models
- Test pre-processing logic (word count, deduplication)
- Test JSON schema validation
- Test LLM prompt crafting

### 7.2 Integration Tests
- Test scraper with real APIs (mocked)
- Test database operations (CRUD)
- Test LLM integration (mocked)
- Test API endpoints

### 7.3 End-to-End Tests
- Test full refresh workflow
- Test frontend-backend integration
- Test error scenarios

### 7.4 Validation Checklist
- [ ] All 6 questions have valid JSON structure
- [ ] Scraping filters work correctly (1-3 star only)
- [ ] Reddit search terms surface relevant posts
- [ ] Reviews < 10 words are filtered out
- [ ] Deduplication prevents duplicate storage
- [ ] LLM updates insights correctly
- [ ] Database commits persist state
- [ ] API endpoints return correct data
- [ ] Frontend displays all 6 cards
- [ ] Refresh button triggers workflow

### 7.5 Deliverables
- `tests/` directory with test files
- `test_models.py`
- `test_scraper.py`
- `test_analysis.py`
- `test_api.py`
- `pytest.ini` configuration

---

## Implementation Sequence
1. **Phase 6** (Setup environment first)
2. **Phase 1** (Database foundation)
3. **Phase 2** (Data acquisition)
4. **Phase 3** (Data processing)
5. **Phase 4** (API layer)
6. **Phase 5** (Frontend)
7. **Phase 7** (Testing throughout)

---

## Critical Success Factors
1. **Data Quality**: Strict filtering ensures only valuable feedback is analyzed
2. **State Persistence**: Database commits must be reliable
3. **LLM Accuracy**: Prompt engineering determines insight quality
4. **Performance**: Async scraping prevents bottlenecks
5. **User Experience**: Frontend must be intuitive and responsive

---

## Risk Mitigation
- **Scraper Failures**: Implement retry logic and fallback mechanisms
- **LLM Rate Limits**: Implement exponential backoff
- **Database Connection**: Use connection pooling
- **API Timeouts**: Set appropriate timeouts and use async tasks
