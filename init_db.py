"""
Database initialization script.
Creates tables and seeds initial insight records.
"""
from datetime import datetime
from database import engine, SessionLocal, Base
from models import RawReview, InsightState


# The 6 core research questions
INITIAL_QUESTIONS = {
    "Q1": "Why do users struggle to discover new music?",
    "Q2": "What are the most common frustrations with recommendations?",
    "Q3": "What listening behaviors are users trying to achieve?",
    "Q4": "What causes users to repeatedly listen to the same content?",
    "Q5": "Which user segments experience different discovery challenges?",
    "Q6": "What unmet needs emerge consistently across reviews?"
}


def create_default_json(question_id: str, question_text: str) -> dict:
    """
    Create a default JSON structure for an insight.
    """
    return {
        "question_id": question_id,
        "question_text": question_text,
        "insight_summary": "No data analyzed yet. Run the refresh-insights endpoint to generate insights.",
        "key_findings": [],
        "metadata": {
            "total_reviews_analyzed": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
    }


def init_database():
    """
    Initialize the database:
    1. Create all tables
    2. Seed initial insight records
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
    
    print("Seeding initial insight records...")
    db = SessionLocal()
    
    try:
        # Check if insights already exist
        existing_insights = db.query(InsightState).count()
        
        if existing_insights == 0:
            # Create initial insight records
            for question_id, question_text in INITIAL_QUESTIONS.items():
                insight = InsightState(
                    question_id=question_id,
                    json_content=create_default_json(question_id, question_text)
                )
                db.add(insight)
            
            db.commit()
            print(f"Successfully seeded {len(INITIAL_QUESTIONS)} insight records.")
        else:
            print(f"Insight records already exist ({existing_insights} found). Skipping seed.")
            
    except Exception as e:
        db.rollback()
        print(f"Error seeding insights: {e}")
        raise
    finally:
        db.close()
    
    print("Database initialization complete.")


if __name__ == "__main__":
    init_database()
