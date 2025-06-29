from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.gemini_client import gemini_client
except ImportError as e:
    logger.error(f"Failed to import gemini_client: {e}")
    gemini_client = None

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
        # Check if gemini_client is available
        if gemini_client is None:
            logger.error("Gemini client not initialized")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Gemini client not initialized",
                    "status": "error"
                }
            )
        
        logger.info(f"Processing chat request: '{request.message[:50]}...' for user: {request.user_id}")
        
        # Generate AI response using the method from your gemini_client
        ai_response = await gemini_client.generate_response_with_fallback(request.message)
        
        # Ensure we have a response
        if not ai_response or not ai_response.strip():
            logger.warning("Empty response from AI service, using mock response")
            ai_response = gemini_client.get_mock_response(request.message)
        
        logger.info(f"Response generated successfully: '{ai_response[:100]}...'")
        
        return ChatResponse(
            response=ai_response,
            status="success",
            user_id=request.user_id
        )
        
    except ValueError as ve:
        # Expected validation error
        logger.warning(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail={"error": str(ve), "status": "error"}
        )
        
    except Exception as e:
        # Log unexpected internal errors
        logger.error(f"Unexpected error in /chat endpoint: {str(e)}", exc_info=True)
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
        if gemini_client is None:
            return {
                "status": "unhealthy",
                "service": "CAFICAFE Chatbot API",
                "gemini_api": "not_initialized",
                "error": "Gemini client not available"
            }
        
        # Use the get_api_status method from your gemini_client
        api_status = gemini_client.get_api_status()
        
        return {
            "status": "healthy" if api_status["api_available"] else "unhealthy",
            "service": "CAFICAFE Chatbot API",
            "gemini_api": api_status["status"],
            "request_count": api_status["request_count"],
            "details": api_status
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "CAFICAFE Chatbot API",
            "gemini_api": "error",
            "error": str(e)
        }

# =====================
# 🔷 Chat History Endpoint (Optional)
# =====================
@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str):
    """
    Get chat history for a specific user.
    Note: This is a placeholder - implement based on your storage solution.
    """
    # TODO: Implement chat history retrieval
    return {
        "user_id": user_id,
        "history": [],
        "message": "Chat history feature not implemented yet"
    }

# =====================
# 🔷 Direct Use Function
# =====================
async def chatbot(prompt: str) -> str:
    """
    Direct access function for Gemini responses.
    Use this for internal API calls without HTTP overhead.
    """
    if gemini_client is None:
        raise RuntimeError("Gemini client not initialized")
    
    try:
        response = await gemini_client.generate_response_with_fallback(prompt)
        return response
    except Exception as e:
        logger.error(f"Direct chatbot call failed: {str(e)}")
        return gemini_client.get_mock_response(prompt)