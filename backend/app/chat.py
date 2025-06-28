from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import re
from app.gemini_client import gemini_client  # Use already-instantiated singleton

# Create a router for all chatbot endpoints
router = APIRouter()


# =====================
# 🔷 Request & Response Models
# =====================

class ChatRequest(BaseModel):
    """Schema for user input to chatbot."""
    message: str
    user_id: Optional[str] = None

    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError("Message cannot be empty.")
        
        # Clean extra whitespace
        cleaned = re.sub(r'\s+', ' ', v.strip())

        if len(cleaned) > 1000:
            raise ValueError("Message too long (max 1000 characters).")

        # Basic content moderation
        prohibited_words = ['spam', 'hack', 'exploit']
        if any(word in cleaned.lower() for word in prohibited_words):
            raise ValueError("Message contains prohibited content.")

        return cleaned


class ChatResponse(BaseModel):
    """Schema for AI response output."""
    response: str
    status: str = "success"
    user_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for structured errors."""
    error: str
    status: str = "error"
    details: Optional[str] = None


# =====================
# 🔷 Chatbot Endpoint
# =====================

@router.post("/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}})
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to handle incoming chat requests and return Gemini AI-generated responses.
    """
    try:
        ai_response = await gemini_client.generate_response(request.message)

        return ChatResponse(
            response=ai_response,
            status="success",
            user_id=request.user_id
        )

    except ValueError as ve:
        # Expected validation error
        raise HTTPException(
            status_code=400,
            detail={"error": str(ve), "status": "error"}
        )

    except Exception as e:
        # Log unexpected internal errors
        print(f"❌ Unexpected error in /chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An unexpected error occurred. Please try again later.",
                "status": "error"
            }
        )


# =====================
# 🔷 Health Check
# =====================

@router.get("/health")
async def health_check():
    """
    Simple GET endpoint to check if chatbot and Gemini API are functional.
    """
    try:
        api_working = gemini_client.validate_api_key()
        return {
            "status": "healthy",
            "service": "CAFICAFE Chatbot API",
            "gemini_api": "connected" if api_working else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "CAFICAFE Chatbot API",
            "error": str(e)
        }


# =====================
# 🔷 Optional: Direct Use Function
# =====================

async def chatbot(prompt: str) -> str:
    """Direct access function for Gemini responses."""
    return await gemini_client.generate_response(prompt)
