from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
# Import your modules
from app.chat import chatbot, gemini_client

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# FastAPI instance + CORS
# -------------------------------------------------------------------
app = FastAPI(
    title="Restaurant Chatbot API",
    description="AI‑powered chatbot for restaurant customer service",
    version="1.0.0",
)

# FIXED: Remove wildcard "*" and set proper CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://munyanezaarmel.github.io",
    "https://munyanezaarmel.github.io/CAFICAFE",
    # Remove "*" and "file://" - they cause issues
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # FIXED: Set to False to avoid conflicts
    allow_methods=["GET", "POST", "OPTIONS"],  # FIXED: Only necessary methods
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
    ],
    expose_headers=["*"],
)

# -------------------------------------------------------------------
# Pydantic models - FIXED: Proper type hints
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    userId: str = None  # Changed from str | None for broader compatibility
    timestamp: str = None

class ChatResponse(BaseModel):
    message: str
    timestamp: str  # FIXED: Use string instead of datetime for JSON serialization
    status: str
    success: bool = True
    error_message: str = None

class HealthResponse(BaseModel):
    status: str
    service: str
    gemini_api: str = None
    timestamp: str
    error: str = None

# -------------------------------------------------------------------
# Root + health endpoints
# -------------------------------------------------------------------
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Restaurant Chatbot API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)",
        },
    }

@app.head("/")
async def head_root():
    return {"status": "ok"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        logger.info("Health check requested")
        
        # FIXED: Safer API validation check
        api_valid = True
        try:
            if hasattr(gemini_client, "validate_api_key"):
                api_valid = gemini_client.validate_api_key()
            elif hasattr(gemini_client, "api_key"):
                api_valid = bool(gemini_client.api_key)
        except Exception as api_error:
            logger.warning(f"API validation error: {api_error}")
            api_valid = False

        response = HealthResponse(
            status="healthy",
            service="restaurant-chatbot",
            gemini_api="connected" if api_valid else "disconnected",
            timestamp=datetime.utcnow().isoformat(),
        )
        
        logger.info("Health check successful")
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            service="restaurant-chatbot",
            error=str(e),
            timestamp=datetime.utcnow().isoformat(),
        )

# -------------------------------------------------------------------
# CORS preflight handlers
# -------------------------------------------------------------------
@app.options("/chat")
async def chat_options():
    """Handle CORS preflight requests for /chat endpoint"""
    return {"message": "OK"}

@app.options("/health")
async def health_options():
    """Handle CORS preflight requests for /health endpoint"""
    return {"message": "OK"}

# -------------------------------------------------------------------
# /chat endpoint - FIXED: Better error handling and response format
# -------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Chat request received: {request.message[:50]}...")
        
        # Validate input
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # FIXED: Better error handling for the chat function
        try:
            # Try gemini client first
            if hasattr(gemini_client, 'generate_response_with_fallback'):
                reply_text = await gemini_client.generate_response_with_fallback(request.message)
            else:
                # Fallback to basic chatbot
                reply_text = await chatbot(request.message, gemini_client)
                
        except Exception as chat_error:
            logger.error(f"Chat generation error: {chat_error}")
            # Fallback response
            reply_text = "I'm sorry, I'm having trouble processing your request right now. Please try again later."

        logger.info(f"Chat response generated: {len(reply_text)} characters")
        
        return ChatResponse(
            message=reply_text,
            timestamp=datetime.utcnow().isoformat(),  # FIXED: Convert to string
            status="success",
            success=True,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception(f"Chat endpoint error: {e}")
        return ChatResponse(
            message="Service temporarily unavailable. Please try again.",
            timestamp=datetime.utcnow().isoformat(),
            status="error",
            success=False,
            error_message="Internal server error",
        )

# -------------------------------------------------------------------
# /test-questions helper
# -------------------------------------------------------------------
@app.post("/test-questions")
async def test_questions():
    questions = [
        "What are your opening hours?",
        "What are your signature dishes?",
        "Where is your restaurant located?",
        "How can I make a reservation?",
        "Do you have vegetarian options?",
        "How can I contact the restaurant?",
    ]
    
    results = []
    for q in questions:
        try:
            r = await chatbot(q, gemini_client)
            results.append({
                "question": q,
                "response": r if len(r) < 100 else r[:100] + "...",
                "success": True,
            })
        except Exception as e:
            logger.error(f"Test question failed: {q} - {e}")
            results.append({
                "question": q, 
                "response": "", 
                "success": False, 
                "error": str(e)
            })
    
    return {"test_results": results}

# -------------------------------------------------------------------
# Startup and shutdown events
# -------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Restaurant Chatbot API starting up...")
    logger.info(f"Allowed CORS origins: {origins}")
    logger.info("✅ API is ready to receive requests")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Restaurant Chatbot API shutting down...")

# -------------------------------------------------------------------
# Uvicorn entry point - FIXED: For Render deployment
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "main:app",  # FIXED: Use module:app format
        host="0.0.0.0", 
        port=port, 
        reload=False,
        log_level="info"
    )