from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your chatbot components
try:
    from app.chat import chatbot, gemini_client
    from app.chat import router as chat_router
except ImportError as e:
    logger.warning(f"Import warning: {e}")
    # Create fallback objects if imports fail
    chatbot = None
    gemini_client = None
    chat_router = None

# Create FastAPI app
app = FastAPI(
    title="Restaurant Chatbot API",
    description="AI-powered chatbot for restaurant customer service",
    version="1.0.0"
)

# Configure CORS
origins = [
    # Local development
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    
    # GitHub Pages - Replace with your actual URL
    "https://munyanezaarmel.github.io",
    
    # Environment variables for flexibility
    os.getenv("FRONTEND_URL", ""),
    os.getenv("PRODUCTION_FRONTEND_URL", ""),
    os.getenv("GITHUB_PAGES_URL", "")
]

# Remove empty strings from origins
origins = [origin for origin in origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include chat router if available
if chat_router:
    app.include_router(chat_router, prefix="/api/v1")

# Request and response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool
    error_message: str = ""

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Restaurant Chatbot API is running!",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat - POST - Send a message to the chatbot",
            "health": "/health - GET - Check API health",
            "docs": "/docs - GET - API documentation"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check if gemini_client is available and has validation method
        api_valid = True
        if gemini_client and hasattr(gemini_client, 'validate_api_key'):
            api_valid = gemini_client.validate_api_key()
        
        return {
            "status": "healthy",
            "service": "restaurant-chatbot",
            "gemini_api": "connected" if api_valid else "disconnected",
            "allowed_origins": origins,
            "chatbot_available": chatbot is not None,
            "gemini_client_available": gemini_client is not None
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "restaurant-chatbot",
            "error": str(e)
        }

# Validate message input
def validate_input(message: str):
    if not message or not message.strip():
        return False, "Message cannot be empty."
    if len(message.strip()) > 1000:
        return False, "Message is too long (max 1000 characters)."
    return True, ""

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.message}")
        
        # Validate input
        is_valid, error_msg = validate_input(request.message)
        if not is_valid:
            return ChatResponse(
                response="",
                success=False,
                error_message=error_msg
            )
        
        # Generate response based on available components
        if gemini_client and hasattr(gemini_client, 'generate_response_with_fallback'):
            # Use gemini client with fallback
            response = await gemini_client.generate_response_with_fallback(request.message)
        elif chatbot:
            # Use chatbot function
            response = await chatbot(request.message)
        else:
            # Fallback response
            response = generate_fallback_response(request.message)
        
        logger.info(f"Generated response: {response[:100]}...")
        
        return ChatResponse(
            response=response,
            success=True,
            error_message=""
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            response="I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
            success=False,
            error_message=str(e)
        )

# Fallback response generator
def generate_fallback_response(message: str) -> str:
    """Generate a basic response when chatbot components are unavailable"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hours', 'open', 'close', 'time']):
        return "We're open Monday to Sunday, 8:00 AM to 10:00 PM. Thank you for your interest in our restaurant!"
    
    elif any(word in message_lower for word in ['menu', 'food', 'dish', 'eat']):
        return "We offer a variety of delicious dishes including pasta, pizza, grilled meats, and fresh salads. Visit us to see our full menu!"
    
    elif any(word in message_lower for word in ['location', 'address', 'where']):
        return "You can find us at our restaurant location. Please contact us for detailed directions and address information."
    
    elif any(word in message_lower for word in ['reservation', 'book', 'table']):
        return "You can make a reservation by calling us or visiting our restaurant. We'd be happy to accommodate you!"
    
    elif any(word in message_lower for word in ['vegetarian', 'vegan', 'dietary']):
        return "Yes, we have vegetarian and dietary-friendly options available. Please let our staff know about any dietary requirements."
    
    else:
        return f"Thank you for your message: '{message}'. We're here to help! Please feel free to ask about our menu, hours, reservations, or location."

# Test questions endpoint
@app.post("/test-questions")
async def test_questions():
    test_questions = [
        "What are your opening hours?",
        "What are your signature dishes?", 
        "Where is your restaurant located?",
        "How can I make a reservation?",
        "Do you have vegetarian options?",
        "How can I contact the restaurant?"
    ]

    results = []
    for question in test_questions:
        try:
            if chatbot:
                response = await chatbot(question)
            else:
                response = generate_fallback_response(question)
                
            results.append({
                "question": question,
                "response": response[:100] + "..." if len(response) > 100 else response,
                "success": True
            })
        except Exception as e:
            logger.error(f"Test question error: {e}")
            results.append({
                "question": question,
                "response": "",
                "success": False,
                "error": str(e)
            })

    return {"test_results": results}

# Uvicorn entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)