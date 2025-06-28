import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

# 🔐 Check if the key is loaded
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in environment.")

# ✅ Configure Gemini with API key
genai.configure(api_key=api_key)

# List all models and supported methods
print("✅ GEMINI_API_KEY Loaded. Fetching available models...\n")
for model in genai.list_models():
    print(f"Model: {model.name} | Methods: {model.supported_generation_methods}")
