"""
Script to list available Gemini models.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


# api_key = os.getenv("GEMINI_API_KEY")

# if not api_key:
#     print("GEMINI_API_KEY not found in environment variables")
#     exit(1)

# Debug line
api_key = os.getenv("GEMINI_API_KEY")

print(f"DEBUG: The value of GEMINI_API_KEY is: {api_key}") 

if api_key:
    genai.configure(api_key=api_key)
else:
    print("CRITICAL: The key is still None/Empty.")


print("Available Gemini models:")
print("=" * 50)

try:
    for model in genai.list_models():
        print(f"Name: {model.name}")
        print(f"Display Name: {model.display_name}")
        print(f"Description: {model.description}")
        print(f"Supported Generation Methods: {model.supported_generation_methods}")
        print("-" * 50)
except Exception as e:
    print(f"Error listing models: {e}")
