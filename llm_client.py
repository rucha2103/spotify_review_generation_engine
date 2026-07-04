"""
LLM client wrapper for Gemini API.
Handles API calls and response parsing.
"""
import os
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# load_dotenv()


class LLMClient:
    """
    Client for interacting with Gemini API.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-3-flash-preview"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.prompts_folder = "llm_prompts"
        
        # Create prompts folder if it doesn't exist
        os.makedirs(self.prompts_folder, exist_ok=True)
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)
    
    def save_prompt(self, prompt: str, response: str = None):
        """
        Save the prompt and optionally the response to a file.
        
        Args:
            prompt: The prompt sent to the LLM
            response: The response from the LLM (optional)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"prompt_{timestamp}.txt"
            filepath = os.path.join(self.prompts_folder, filename)
            
            print(f"Attempting to save prompt to: {filepath}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Model: {self.model}\n")
                f.write(f"{'='*50}\n")
                f.write("PROMPT:\n")
                f.write(prompt)
                f.write(f"\n{'='*50}\n")
                if response:
                    f.write("RESPONSE:\n")
                    f.write(response)
            
            print(f"Successfully saved prompt to {filepath}")
        except Exception as e:
            print(f"Error saving prompt: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_response(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            The LLM's response as a string
        """
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    top_p=0.8,
                    top_k=40,
                )
            )
            
            # Save prompt and response together
            self.save_prompt(prompt, response.text)
            
            return response.text
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            raise
    
    def generate_json_response(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate a JSON response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            The LLM's response as a string (expected to be JSON)
        """
        # Add instruction to output valid JSON
        json_prompt = f"{prompt}\n\nIMPORTANT: Output must be valid JSON only. No markdown, no code blocks, just raw JSON."
        
        return self.generate_response(json_prompt, temperature)