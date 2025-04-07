import google.generativeai as genai
from config.config import GOOGLE_API_KEY

# Configure Google API Key
genai.configure(api_key=GOOGLE_API_KEY)

# List available models
models = genai.list_models()

print("Available models:")
for model in models:
    print(model.name)
