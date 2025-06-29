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

# -------------------------------------------------------------------
# FastAPI instance + CORS
# -------------------------------------------------------------------
app = FastAPI(
    title="Restaurant Chatbot API",
    description="AI‑powered chatbot for restaurant customer service",
    version="1.0.0",
)

# Fixed CORS origins - added your frontend URL
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://caficafe-1.onrender.com",
    "https://munyanezaarmel.github.io",  # Fixed: removed specific path
    "https://munyanezaarmel.github.io/CAFICAFE",  # Keep this too
    "file://",
    "*",  # Allow all origins for testing (remove in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# -------------------------------------------------------------------
# Pydantic models
# -------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    userId: str | None = None
    timestamp: str | None = None

class ChatResponse(BaseModel):
    message: str
    timestamp: datetime
    status: str
    success: bool = True
    error_message: str | None = None

# -------------------------------------------------------------------
# Root + health endpoints
# -------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Restaurant Chatbot API is running!",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat  (POST)",
            "health": "/health  (GET)",
        },
    }

@app.head("/")
async def head_root():
    return await root()

@app.get("/health")
async def health_check():
    try:
        # Fixed: Added safer API validation check
        api_valid = True
        try:
            if hasattr(gemini_client, "validate_api_key"):
                api_valid = gemini_client.validate_api_key()
            elif hasattr(gemini_client, "api_key"):
                api_valid = bool(gemini_client.api_key)
        except Exception:
            api_valid = False
            
        return {
            "status": "healthy",
            "service": "restaurant-chatbot",
            "gemini_api": "connected" if api_valid else "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logging.error("Health check failed: %s", e)
        return {
            "status": "unhealthy",
            "service": "restaurant-chatbot",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }

# -------------------------------------------------------------------
# /chat endpoint - Fixed error handling and response format
# -------------------------------------------------------------------
@app.options("/chat")
async def chat_options():
    """Handle CORS preflight requests for /chat endpoint"""
    return {"message": "OK"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logging.info("🔍 Received: %s", request.message)

        # Fixed: Better error handling for the chat function
        try:
            reply_text: str = await gemini_client.generate_response_with_fallback(
                request.message
            )
        except Exception as chat_error:
            logging.error("Chat generation error: %s", chat_error)
            # Fallback to basic chatbot if gemini fails
            try:
                reply_text = await chatbot(request.message)
            except Exception as fallback_error:
                logging.error("Fallback chatbot error: %s", fallback_error)
                reply_text = "I'm sorry, I'm having trouble processing your request right now. Please try again later."

        logging.info("🔍 Reply (truncated): %s", reply_text[:100])

        return ChatResponse(
            message=reply_text,
            timestamp=datetime.utcnow(),
            status="success",
            success=True,
        )

    except Exception as e:
        logging.exception("❌ Chat endpoint error: %s", e)
        return ChatResponse(
            message="Service temporarily unavailable. Please try again.",
            timestamp=datetime.utcnow(),
            status="error",
            success=False,
            error_message=str(e),
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
            r = await chatbot(q)
            results.append(
                {
                    "question": q,
                    "response": r if len(r) < 100 else r[:100] + "...",
                    "success": True,
                }
            )
        except Exception as e:
            results.append({"question": q, "response": "", "success": False, "error": str(e)})

    return {"test_results": results}

# -------------------------------------------------------------------
# Uvicorn entry point - Fixed for Render deployment
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)