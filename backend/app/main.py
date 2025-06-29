from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging

# Import your modules
from app.chat import chatbot, gemini_client

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Restaurant Chatbot API",
    description="AI-powered chatbot for restaurant customer service",
    version="1.0.0"
)

# Configure CORS with your actual domains
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://caficafe-5.onrender.com",
    "https://munyanezaarmel.github.io/CAFICAFE",
    "file://",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# Request and response models
class ChatRequest(BaseModel):
    message: str
    userId: str = None
    timestamp: str = None

class ChatResponse(BaseModel):
    message: str 
    timestamp: str
    status: str
    success: bool = True
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

@app.head("/")
async def head_root():
    return await root()

# Health check
@app.get("/health")
async def health_check():
    try:
        api_valid = gemini_client.validate_api_key() if hasattr(gemini_client, 'validate_api_key') else True
        return {
            "status": "healthy",
            "service": "restaurant-chatbot",
            "gemini_api": "connected" if api_valid else "disconnected",
            "timestamp": str(__import__('datetime').datetime.now())
        }
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "restaurant-chatbot",
            "error": str(e),
            "timestamp": str(__import__('datetime').datetime.now())
        }

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logging.info(f"🔍 Received message: {request.message}")
        
        # Generate response using your existing method
        response_data = await gemini_client.generate_response_with_fallback(request.message)
        
        # Handle the response based on its type
        if isinstance(response_data, dict) and "response" in response_data:
            logging.warning(f"Unexpected dictionary response from gemini_client: {response_data}")
            raise Exception("Internal fallback triggered")
        else:
            response_text = response_data
        
        logging.info(f"🔍 Generated response: {response_text[:100]}...")
        
        return ChatResponse(
            message=response_text,
            timestamp=str(__import__('datetime').datetime.now().isoformat()),
            status="success",
            success=True
        )
        
    except Exception as e:
        logging.error(f"❌ Chat endpoint error: {e}")
        return ChatResponse(
            message="I'm currently experiencing technical difficulties. Please try again in a few moments, or contact us directly for immediate assistance.",
            timestamp=str(__import__('datetime').datetime.now().isoformat()),
            status="error",
            success=False,
            error_message=str(e)
        )

@app.get("/chat")
async def chat_status():
    return {
        "message": "Chat service is running",
        "status": "online",
        "timestamp": str(__import__('datetime').datetime.now().isoformat()),
        "service": "CafiCafe Chat"
    }

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
            response = await gemini_client.generate_response_with_fallback(question)
            results.append({
                "question": question,
                "response": response[:100] + "..." if len(response) > 100 else response,
                "success": True
            })
        except Exception as e:
            logging.error(f"❌ Test question error for '{question}': {e}")
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)