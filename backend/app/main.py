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
# FastAPI instance
# -------------------------------------------------------------------
app = FastAPI(
    title="Restaurant Chatbot API",
    description="AI‑powered chatbot for restaurant customer service",
    version="1.0.0",
)

# -------------------------------------------------------------------
# CORS Configuration (NO custom middleware)
# -------------------------------------------------------------------
origins = [
    "https://munyanezaarmel.github.io",  # ✅ GitHub Pages domain
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Pydantic models
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    userId: str = None
    timestamp: str = None

class ChatResponse(BaseModel):
    message: str
    timestamp: str
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
# Root endpoint
# -------------------------------------------------------------------
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Restaurant Chatbot API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "cors_origins": origins,
        "endpoints": {
            "chat": "/chat (POST)",
            "health": "/health (GET)",
        },
    }

# -------------------------------------------------------------------
# Health endpoint
# -------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        logger.info("Health check requested")
        api_valid = True
        try:
            if hasattr(gemini_client, "validate_api_key"):
                api_valid = gemini_client.validate_api_key()
            elif hasattr(gemini_client, "api_key"):
                api_valid = bool(gemini_client.api_key)
        except Exception as api_error:
            logger.warning(f"API validation error: {api_error}")
            api_valid = False

        return HealthResponse(
            status="healthy",
            service="restaurant-chatbot",
            gemini_api="connected" if api_valid else "disconnected",
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            service="restaurant-chatbot",
            error=str(e),
            timestamp=datetime.utcnow().isoformat(),
        )

# -------------------------------------------------------------------
# OPTIONS preflight catch-all
# -------------------------------------------------------------------
from fastapi.responses import Response

@app.options("/{path:path}")
async def preflight_handler(path: str):
    return Response(status_code=204)

# -------------------------------------------------------------------
# Chat endpoint
# -------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info("Chat request received")

        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        try:
            if hasattr(gemini_client, 'generate_response_with_fallback'):
                reply_text = await gemini_client.generate_response_with_fallback(request.message)
            else:
                reply_text = await chatbot(request.message, gemini_client)

        except Exception as chat_error:
            logger.error(f"Chat generation error: {chat_error}")
            reply_text = "I'm sorry, I'm having trouble processing your request right now. Please try again later."

        logger.info(f"Chat response generated: {len(reply_text)} characters")

        return ChatResponse(
            message=reply_text,
            timestamp=datetime.utcnow().isoformat(),
            status="success",
            success=True,
        )

    except HTTPException:
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
# Startup event
# -------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Restaurant Chatbot API starting up...")
    logger.info(f"Allowed CORS origins: {origins}")
    logger.info("✅ API is ready to receive requests")

# -------------------------------------------------------------------
# Main entry point (if local run)
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
