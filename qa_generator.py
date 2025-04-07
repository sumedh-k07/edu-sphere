import google.generativeai as genai
import time
from config.config import GOOGLE_API_KEY

# Configure Google API
genai.configure(api_key=GOOGLE_API_KEY)

# Use Gemini 1.5 Pro Latest
model = genai.GenerativeModel("gemini-1.5-pro-latest")

def generate_qa(text, difficulty, max_retries=3, delay=5):
    """Generate Q&A using Gemini 1.5 Pro Latest with proper response handling."""

    prompt = f"Generate a {difficulty}-level Q&A from the following text:\n\n{text}"
  
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)  # API Call
            
            # ✅ Extracting the actual response text
            if response and response.candidates:
                generated_text = response.candidates[0].content.parts[0].text
                print("DEBUG: Raw AI Output:\n", generated_text[:500])  # Log first 500 chars
                return generated_text
            
            else:
                raise ValueError("Empty response from API")

        except Exception as e:
            print(f"⚠️ API Error: {e}. Retrying in {delay} seconds... ({attempt+1}/{max_retries})")
            time.sleep(delay)  # Wait before retrying

    return "❌ Error: Unable to generate Q&A after multiple attempts."
