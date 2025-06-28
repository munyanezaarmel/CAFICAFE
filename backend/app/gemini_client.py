import os
from dotenv import load_dotenv
import google.generativeai as genai
from .restaurant_context import restaurant_context

# Load environment variables from .env
load_dotenv()

class GeminiClient:
    def __init__(self):
        # Load API key
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY environment variable is missing.")

        print("✅ GEMINI_API_KEY Loaded:", bool(self.api_key))

        # Configure Gemini API with the key
        genai.configure(api_key=self.api_key)

        # Choose the recommended latest model (can be updated)
        self.model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")

        # Load predefined restaurant context
        self.restaurant_context = restaurant_context.get_full_context()

    async def generate_response(self, user_message: str) -> str:
        """
        Generate AI-powered response using Gemini model,
        integrating restaurant-specific context with user input.
        """
        try:
            full_prompt = f"""{self.restaurant_context}

Customer Question: {user_message}

Response:"""

            # Use Gemini to generate a reply
            response = self.model.generate_content(full_prompt)
            return response.text.strip()

        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            return self._get_fallback_response()

    def _get_fallback_response(self) -> str:
        """
        Return a safe fallback response if AI fails.
        """
        return (
            "I apologize, but I'm currently unable to process your request.\n"
            "Please contact us at +1 (555) 123-CAFE or email hello@caficafe.com for assistance!"
        )

    def validate_api_key(self) -> bool:
        """
        Test if the API key and model are working correctly.
        """
        try:
            self.model.generate_content("Test prompt")
            return True
        except Exception as e:
            print("❌ API validation failed:", e)
            return False

# ✅ Create a single instance to use in FastAPI app
gemini_client = GeminiClient()
