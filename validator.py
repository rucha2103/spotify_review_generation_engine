"""
JSON schema validation for insight objects.
Validates that insight JSONs match the required structure.
"""
import json
from typing import Dict, List
from datetime import datetime


class InsightValidator:
    """
    Validator for insight JSON objects.
    Ensures compliance with the required schema.
    """
    
    # The 6 valid question IDs
    VALID_QUESTION_IDS = {"Q1", "Q2", "Q3", "Q4", "Q5", "Q6"}
    
    # The 6 research questions
    RESEARCH_QUESTIONS = {
        "Q1": "Why do users struggle to discover new music?",
        "Q2": "What are the most common frustrations with recommendations?",
        "Q3": "What listening behaviors are users trying to achieve?",
        "Q4": "What causes users to repeatedly listen to the same content?",
        "Q5": "Which user segments experience different discovery challenges?",
        "Q6": "What unmet needs emerge consistently across reviews?"
    }
    
    @staticmethod
    def validate_insight(insight: Dict) -> tuple[bool, str]:
        """
        Validate a single insight object.
        
        Args:
            insight: The insight dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        required_fields = ['question_id', 'question_text', 'insight_summary', 'key_findings', 'metadata']
        for field in required_fields:
            if field not in insight:
                return False, f"Missing required field: {field}"
        
        # Validate question_id
        question_id = insight['question_id']
        if question_id not in InsightValidator.VALID_QUESTION_IDS:
            return False, f"Invalid question_id: {question_id}. Must be one of {InsightValidator.VALID_QUESTION_IDS}"
        
        # Validate question_text matches expected question
        expected_question = InsightValidator.RESEARCH_QUESTIONS[question_id]
        if insight['question_text'] != expected_question:
            return False, f"question_text for {question_id} does not match expected question"
        
        # Validate insight_summary is a string
        if not isinstance(insight['insight_summary'], str):
            return False, "insight_summary must be a string"
        
        # Validate key_findings is a list
        if not isinstance(insight['key_findings'], list):
            return False, "key_findings must be a list"
        
        # Validate metadata structure
        metadata = insight['metadata']
        if not isinstance(metadata, dict):
            return False, "metadata must be a dictionary"
        
        required_metadata_fields = ['total_reviews_analyzed', 'last_updated']
        for field in required_metadata_fields:
            if field not in metadata:
                return False, f"Missing required metadata field: {field}"
        
        # Validate total_reviews_analyzed is an integer
        if not isinstance(metadata['total_reviews_analyzed'], int):
            return False, "total_reviews_analyzed must be an integer"
        
        # Validate last_updated is a valid ISO timestamp
        try:
            timestamp_str = metadata['last_updated']
            # Handle 'Z' suffix (UTC indicator)
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            datetime.fromisoformat(timestamp_str)
        except ValueError:
            return False, "last_updated must be a valid ISO timestamp"
        
        return True, ""
    
    @staticmethod
    def validate_insights_list(insights: List[Dict]) -> tuple[bool, str]:
        """
        Validate a list of insight objects.
        
        Args:
            insights: List of insight dictionaries to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if it's a list
        if not isinstance(insights, list):
            return False, "Input must be a list"
        
        # Check if exactly 6 insights
        if len(insights) != 6:
            return False, f"Expected 6 insights, got {len(insights)}"
        
        # Check for duplicate question_ids
        question_ids = [insight.get('question_id') for insight in insights]
        if len(set(question_ids)) != len(question_ids):
            return False, "Duplicate question_ids found"
        
        # Validate each insight
        for i, insight in enumerate(insights):
            is_valid, error = InsightValidator.validate_insight(insight)
            if not is_valid:
                return False, f"Insight {i+1} validation failed: {error}"
        
        # Check that all 6 question IDs are present
        present_ids = set(question_ids)
        missing_ids = InsightValidator.VALID_QUESTION_IDS - present_ids
        if missing_ids:
            return False, f"Missing question_ids: {missing_ids}"
        
        return True, ""
    
    @staticmethod
    def parse_and_validate_json(json_str: str) -> tuple[bool, List[Dict], str]:
        """
        Parse a JSON string and validate the insights.
        
        Args:
            json_str: JSON string to parse and validate
            
        Returns:
            Tuple of (is_valid, insights_list, error_message)
        """
        try:
            # Parse JSON
            data = json.loads(json_str)
            
            # Handle both formats: object with keys (Q1, Q2, etc.) or array
            if isinstance(data, dict):
                # Convert object format to array format
                insights = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        insights.append(value)
            elif isinstance(data, list):
                insights = data
            else:
                return False, [], "JSON must be an object or array"
            
            # Validate structure
            is_valid, error = InsightValidator.validate_insights_list(insights)
            
            if is_valid:
                return True, insights, ""
            else:
                return False, [], error
        
        except json.JSONDecodeError as e:
            return False, [], f"Invalid JSON: {e}"
        except Exception as e:
            return False, [], f"Error parsing JSON: {e}"
