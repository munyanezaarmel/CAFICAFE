from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

# ✅ Correct imports
from app.chat import chatbot, gemini_client
from app.chat import router as chat_router  # ✅ FIXED

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Restaurant Chatbot API",
    description="AI-powered chatbot for restaurant customer service",
    version="1.0.0"
)

# ✅ Add this line to prefix all routes with /api/v1
app.include_router(chat_router, prefix="/api/v1")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    os.getenv("FRONTEND_URL", ""),
    os.getenv("PRODUCTION_FRONTEND_URL", "")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
            "health": "/health - GET - Check API health"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    try:
        api_valid = gemini_client.validate_api_key() if hasattr(gemini_client, 'validate_api_key') else True
        return {
            "status": "healthy",
            "service": "restaurant-chatbot",
            "gemini_api": "connected" if api_valid else "disconnected"
        }
    except Exception as e:
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

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        is_valid, error_msg = validate_input(request.message)
        if not is_valid:
            return ChatResponse(response="", success=False, error_message=error_msg)

        ai_reply = await chatbot(request.message)

        return ChatResponse(response=ai_reply, success=True)

    except Exception as e:
        print(f"Error in /chat: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please try again later."
        )

# Test question endpoint
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
            response = await chatbot(question)
            results.append({
                "question": question,
                "response": response[:100] + "..." if len(response) > 100 else response,
                "success": True
            })
        except Exception as e:
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
