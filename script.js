// Carousel functionality with real image switching
function initCarousel() {
  let currentSlide = 0;
  const totalSlides = 3;
  const carouselDots = document.querySelectorAll(".carousel-dot");
  const prevBtn = document.getElementById("prev-btn");
  const nextBtn = document.getElementById("next-btn");
  const slides = [
    document.getElementById("slide-1"),
    document.getElementById("slide-2"),
    document.getElementById("slide-3"),
  ];

  // Function to update carousel display
  function updateCarousel() {
    // Hide all slides
    slides.forEach((slide, index) => {
      if (index === currentSlide) {
        slide.classList.remove("hidden");
        slide.classList.add("active");
      } else {
        slide.classList.add("hidden");
        slide.classList.remove("active");
      }
    });

    // Update dots appearance
    carouselDots.forEach((dot, index) => {
      if (index === currentSlide) {
        dot.classList.remove("bg-gray-400");
        dot.classList.add("bg-gray-800");
      } else {
        dot.classList.remove("bg-gray-800");
        dot.classList.add("bg-gray-400");
      }
    });
  }

  // Previous button click handler
  prevBtn.addEventListener("click", () => {
    currentSlide = currentSlide === 0 ? totalSlides - 1 : currentSlide - 1;
    updateCarousel();
  });

  // Next button click handler
  nextBtn.addEventListener("click", () => {
    currentSlide = currentSlide === totalSlides - 1 ? 0 : currentSlide + 1;
    updateCarousel();
  });

  // Dot navigation click handlers
  carouselDots.forEach((dot, index) => {
    dot.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      currentSlide = index;
      updateCarousel();
    });
  });

  updateCarousel();
}

// Configuration
const API_BASE_URL = 'https://caficafe-5.onrender.com'; // Your deployed backend URL

// Global variables for connection status
let isBackendConnected = false;
let connectionCheckInterval = null;

// Chat functionality
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendButton = document.getElementById('sendButton');
    const sendText = document.getElementById('sendText');
    const loadingText = document.getElementById('loadingText');
    const errorMessage = document.getElementById('errorMessage');
    
    const userMessage = chatInput.value.trim();
    
    // Hide any previous error messages
    hideError();
    
    // Validate input
    if (!userMessage) {
        showError('Please enter a message');
        return;
    }
    
    if (userMessage.length > 1000) {
        showError('Message is too long. Please keep it under 1000 characters.');
        return;
    }
    
    // Add user message to chat
    addMessage(userMessage, 'user');
    
    // Clear input and show loading state
    chatInput.value = '';
    setLoadingState(true);
    
    try {
        console.log('Sending message to:', `${API_BASE_URL}/chat`);
        
        // Send request to backend
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                message: userMessage
            })
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            // Handle specific HTTP errors
            if (response.status === 404) {
                throw new Error('Chat service not found. Please contact support.');
            } else if (response.status === 500) {
                throw new Error('Server error. Please try again in a moment.');
            } else if (response.status === 429) {
                throw new Error('Too many requests. Please wait a moment and try again.');
            } else {
                throw new Error(`Service error (${response.status}). Please try again.`);
            }
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        // Handle different response formats
        if (data.success === true || data.success === undefined) {
            // Successful response
            const botResponse = data.response || data.message || 'I received your message but couldn\'t generate a response.';
            addMessage(botResponse, 'bot');
            isBackendConnected = true;
        } else {
            // Backend returned an error
            const errorMsg = data.error_message || data.error || 'Sorry, something went wrong. Please try again.';
            showError(errorMsg);
            console.error('Backend error:', data);
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        isBackendConnected = false;
        
        // Show user-friendly error messages based on error type
        if (error.name === 'TypeError' || error.message.includes('Failed to fetch')) {
            showError('Unable to connect to our chat service. Please check your internet connection and try again.');
        } else if (error.message.includes('CORS')) {
            showError('Connection blocked. Please contact support if this continues.');
        } else if (error.message.includes('timeout')) {
            showError('Request timed out. Please try again.');
        } else {
            showError(error.message || 'Sorry, something went wrong. Please try again in a moment.');
        }
        
        // Add fallback response for better UX
        setTimeout(() => {
            addMessage("I'm currently experiencing technical difficulties. Please try again in a few moments, or contact us directly for immediate assistance.", 'bot error');
        }, 1000);
        
    } finally {
        // Reset loading state
        setLoadingState(false);
        
        // Focus back on input
        chatInput.focus();
    }
}

function addMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Add timestamp
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const messageP = document.createElement('p');
    messageP.textContent = message;
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = timestamp;
    
    messageContent.appendChild(messageP);
    messageContent.appendChild(timeSpan);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom with smooth animation
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    if (!errorDiv) {
        console.error('Error message div not found');
        alert(message); // Fallback to alert
        return;
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    errorDiv.className = 'error-message show';
    
    // Hide error after 8 seconds
    setTimeout(() => {
        hideError();
    }, 8000);
}

function hideError() {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.style.display = 'none';
        errorDiv.className = 'error-message';
    }
}

function setLoadingState(isLoading) {
    const sendButton = document.getElementById('sendButton');
    const sendText = document.getElementById('sendText');
    const loadingText = document.getElementById('loadingText');
    const chatInput = document.getElementById('chatInput');
    
    if (sendButton) sendButton.disabled = isLoading;
    if (chatInput) chatInput.disabled = isLoading;
    
    if (sendText && loadingText) {
        sendText.style.display = isLoading ? 'none' : 'inline';
        loadingText.style.display = isLoading ? 'inline' : 'none';
    }
}

// Test backend connection
async function testConnection() {
    try {
        console.log('Testing connection to:', `${API_BASE_URL}/health`);
        
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend connection successful:', data);
            isBackendConnected = true;
            updateConnectionStatus(true);
            return true;
        } else {
            console.warn('⚠️ Backend responded with error status:', response.status);
            isBackendConnected = false;
            updateConnectionStatus(false);
            return false;
        }
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
        isBackendConnected = false;
        updateConnectionStatus(false);
        return false;
    }
}

function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
        statusElement.textContent = connected ? 'Connected' : 'Disconnected';
        statusElement.className = connected ? 'status-connected' : 'status-disconnected';
    }
}

// Retry connection periodically if disconnected
function startConnectionMonitoring() {
    // Test connection immediately
    testConnection();
    
    // Set up periodic connection checks
    connectionCheckInterval = setInterval(async () => {
        if (!isBackendConnected) {
            console.log('Retrying connection...');
            await testConnection();
        }
    }, 30000); // Check every 30 seconds if disconnected
}

function stopConnectionMonitoring() {
    if (connectionCheckInterval) {
        clearInterval(connectionCheckInterval);
        connectionCheckInterval = null;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing chat application...');
    
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    
    // Set up enter key listener
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Focus on input
        chatInput.focus();
    }
    
    // Set up send button listener
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    // Start connection monitoring
    startConnectionMonitoring();
    
    // Add welcome message
    setTimeout(() => {
        addMessage("Hello! I'm your restaurant assistant. Ask me about our menu, hours, reservations, or anything else you'd like to know!", 'bot');
    }, 500);
});

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    stopConnectionMonitoring();
});

// Expose functions for debugging (optional)
window.chatDebug = {
    testConnection,
    sendTestMessage: () => sendMessage('Hello, this is a test message'),
    clearChat: () => {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) chatMessages.innerHTML = '';
    },
    getConnectionStatus: () => isBackendConnected
};