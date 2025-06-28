import os
from dotenv import load_dotenv
import google.generativeai as genai
from .restaurant_context import restaurant_context
from datetime import datetime
import time

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
        
        # Track API usage (optional)
        self.request_count = 0
        self.last_reset = datetime.now().date()

    async def generate_response(self, user_message: str) -> str:
        """
        Generate AI-powered response using Gemini model,
        integrating restaurant-specific context with user input.
        """
        try:
            # Increment request counter
            self.request_count += 1
            
            full_prompt = f"""{self.restaurant_context}

Customer Question: {user_message}

Please provide a helpful, friendly response as a restaurant staff member. Keep it concise and informative.

Response:"""
            
            # Use Gemini to generate a reply
            response = self.model.generate_content(full_prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._get_empty_response()
                
        except Exception as e:
            error_str = str(e)
            print(f"❌ Gemini Error: {e}")
            
            # Handle different types of errors
            if "429" in error_str or "quota" in error_str.lower():
                return self._get_quota_exceeded_response()
            elif "403" in error_str:
                return self._get_permission_error_response()
            elif "500" in error_str or "503" in error_str:
                return self._get_server_error_response()
            else:
                return self._get_fallback_response()

    def _get_quota_exceeded_response(self) -> str:
        """
        Response when API quota is exceeded.
        """
        return (
            "I'm currently experiencing high demand and have reached my daily response limit. "
            "Please try again in a few hours, or contact us directly at "
            "+1 (555) 123-CAFE or hello@caficafe.com for immediate assistance with your inquiry!"
        )

    def _get_permission_error_response(self) -> str:
        """
        Response for permission/authentication errors.
        """
        return (
            "I'm experiencing a technical issue with my AI service. "
            "Please contact us at +1 (555) 123-CAFE or email hello@caficafe.com "
            "and our staff will be happy to help you personally!"
        )

    def _get_server_error_response(self) -> str:
        """
        Response for server errors.
        """
        return (
            "I'm experiencing temporary technical difficulties. "
            "Please try again in a moment, or contact us directly at "
            "+1 (555) 123-CAFE or hello@caficafe.com for assistance!"
        )

    def _get_empty_response(self) -> str:
        """
        Response when API returns empty content.
        """
        return (
            "I'm having trouble generating a response right now. "
            "Please contact us at +1 (555) 123-CAFE or hello@caficafe.com "
            "and our team will assist you immediately!"
        )

    def _get_fallback_response(self) -> str:
        """
        Return a safe fallback response if AI fails.
        """
        return (
            "I apologize, but I'm currently unable to process your request. "
            "Please contact us at +1 (555) 123-CAFE or email hello@caficafe.com for assistance!"
        )

    def get_mock_response(self, user_message: str) -> str:
        """
        Temporary mock responses for testing when API is down.
        Remove this method when API is working properly.
        """
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["vegan", "plant-based", "vegetarian"]):
            return (
                "Yes, we do! We offer vegan options for most dishes upon request. "
                "To ensure we can accommodate your preferences perfectly, please speak "
                "directly with one of our staff members when you place your order. "
                "They can help you choose the best vegan options available."
            )
        elif any(word in message_lower for word in ["menu", "food", "dishes"]):
            return (
                "We have a diverse menu featuring local and international cuisine! "
                "Our specialties include fresh seafood, grilled meats, pasta dishes, "
                "and healthy salad options. Would you like to know about any specific "
                "category or dietary requirements?"
            )
        elif any(word in message_lower for word in ["hours", "open", "time"]):
            return (
                "We're open Monday through Sunday! Our hours are 11:00 AM to 10:00 PM "
                "Monday-Thursday, and 11:00 AM to 11:00 PM Friday-Sunday. "
                "We'd love to see you soon!"
            )
        elif any(word in message_lower for word in ["reservation", "booking", "table"]):
            return (
                "We'd be happy to help you make a reservation! You can call us at "
                "+1 (555) 123-CAFE or email hello@caficafe.com. We recommend booking "
                "in advance, especially for weekend dining."
            )
        elif any(word in message_lower for word in ["location", "address", "where"]):
            return (
                "We're conveniently located in the heart of the city! "
                "Please contact us at +1 (555) 123-CAFE or hello@caficafe.com "
                "for our exact address and directions."
            )
        else:
            return (
                "Thank you for your question! For the most accurate and detailed information, "
                "please contact us at +1 (555) 123-CAFE or hello@caficafe.com. "
                "Our friendly staff will be happy to assist you!"
            )

    async def generate_response_with_fallback(self, user_message: str) -> str:
        """
        Generate response with mock fallback for testing.
        Use this temporarily while API quota is exceeded.
        """
        try:
            # Try the real API first
            return await self.generate_response(user_message)
        except Exception as e:
            # If API fails, use mock responses for better testing
            print(f"Using mock response due to API error: {e}")
            return self.get_mock_response(user_message)

    def validate_api_key(self) -> bool:
        """
        Test if the API key and model are working correctly.
        """
        try:
            test_response = self.model.generate_content("Test prompt")
            return True
        except Exception as e:
            print("❌ API validation failed:", e)
            return False

    def get_api_status(self) -> dict:
        """
        Check the current status of the Gemini API.
        """
        try:
            # Simple test request
            test_response = self.model.generate_content("Hello")
            return {
                "status": "working",
                "api_available": True,
                "test_response": test_response.text[:50] + "..." if test_response.text else "Empty response",
                "request_count": self.request_count
            }
        except Exception as e:
            error_str = str(e)
            status_info = {
                "status": "error",
                "api_available": False,
                "error": error_str,
                "request_count": self.request_count
            }
            
            if "429" in error_str or "quota" in error_str.lower():
                status_info["error_type"] = "quota_exceeded"
                status_info["message"] = "Daily quota limit reached"
            elif "403" in error_str:
                status_info["error_type"] = "permission_denied"
                status_info["message"] = "API key authentication failed"
            else:
                status_info["error_type"] = "unknown"
                status_info["message"] = "Unknown API error"
            
            return status_info

    def reset_daily_counter(self):
        """
        Reset the daily request counter (call this daily or when quota resets).
        """
        current_date = datetime.now().date()
        if current_date > self.last_reset:
            self.request_count = 0
            self.last_reset = current_date
            print("✅ Daily request counter reset")

# ✅ Create a single instance to use in FastAPI app
gemini_client = GeminiClient()