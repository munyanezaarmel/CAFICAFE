#!/usr/bin/env python3
"""
Quick test script to verify your chatbot setup
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_basic_setup():
    """Test basic setup"""
    print("🔍 Testing CAFICAFE Chatbot Setup")
    print("=" * 40)
    
    # 1. Check environment variable
    print("1. Checking environment variables...")
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"   ✅ GEMINI_API_KEY found (length: {len(api_key)})")
    else:
        print("   ❌ GEMINI_API_KEY not found")
        print("   Set it with: export GEMINI_API_KEY='AIzaSyBzHhdgUUsZax7gmFeEGoZg0ZFWxRNCnEM'")
        return False
    
    # 2. Test gemini_client import
    print("\n2. Testing gemini_client import...")
    try:
        from app.gemini_client import gemini_client
        print("   ✅ gemini_client imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import gemini_client: {e}")
        return False
    
    # 3. Test API status
    print("\n3. Testing Gemini API connection...")
    try:
        status = gemini_client.get_api_status()
        print(f"   Status: {status['status']}")
        print(f"   API Available: {status['api_available']}")
        if not status['api_available']:
            print(f"   Error: {status.get('error', 'Unknown error')}")
            return False
        print("   ✅ Gemini API working")
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False
    
    # 4. Test response generation
    print("\n4. Testing response generation...")
    try:
        test_message = "What are your opening hours?"
        response = await gemini_client.generate_response_with_fallback(test_message)
        print(f"   Question: {test_message}")
        print(f"   Response: {response[:100]}...")
        if response and response.strip():
            print("   ✅ Response generation working")
            return True
        else:
            print("   ❌ Empty response generated")
            return False
    except Exception as e:
        print(f"   ❌ Response generation failed: {e}")
        return False

async def test_chat_endpoint():
    """Test chat endpoint"""
    print("\n5. Testing chat endpoint...")
    try:
        from app.chat import ChatRequest, chat_endpoint
        
        # Create test request
        request = ChatRequest(
            message="What are your opening hours?",
            user_id="test_user"
        )
        
        # Call endpoint
        response = await chat_endpoint(request)
        
        print(f"   Request: {request.message}")
        print(f"   Response: {response.response[:100]}...")
        print(f"   Status: {response.status}")
        
        if response.response and response.status == "success":
            print("   ✅ Chat endpoint working")
            return True
        else:
            print("   ❌ Chat endpoint failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Chat endpoint test failed: {e}")
        return False

async def main():
    """Run all tests"""
    
    # Test basic setup
    basic_ok = await test_basic_setup()
    
    if not basic_ok:
        print("\n❌ Basic setup failed. Please fix the issues above.")
        return
    
    # Test chat endpoint
    chat_ok = await test_chat_endpoint()
    
    # Final result
    print("\n" + "=" * 40)
    if basic_ok and chat_ok:
        print("🎉 All tests passed! Your chatbot is ready.")
        print("\nTo start the server:")
        print("   python main.py")
        print("\nThen test with:")
        print("   curl -X POST http://localhost:8000/api/v1/chat \\")
        print("        -H 'Content-Type: application/json' \\")
        print("        -d '{\"message\": \"What are your opening hours?\", \"user_id\": \"test\"}'")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())