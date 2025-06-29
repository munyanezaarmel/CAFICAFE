// === Carousel Functionality ===
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

  function updateCarousel() {
    slides.forEach((slide, index) => {
      if (index === currentSlide) {
        slide.classList.remove("hidden");
        slide.classList.add("active");
      } else {
        slide.classList.add("hidden");
        slide.classList.remove("active");
      }
    });

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

  // Add null checks for buttons and dots
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      currentSlide = currentSlide === 0 ? totalSlides - 1 : currentSlide - 1;
      updateCarousel();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      currentSlide = currentSlide === totalSlides - 1 ? 0 : currentSlide + 1;
      updateCarousel();
    });
  }

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
const API_BASE_URL = 'https://caficafe-1.onrender.com'; 

// Chat functionality
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendButton = document.getElementById('sendButton');
    const sendText = document.getElementById('sendText');
    const loadingText = document.getElementById('loadingText');
    const errorMessage = document.getElementById('errorMessage');
    
    // Check if elements exist
    if (!chatInput || !chatMessages || !sendButton) {
        console.error('Chat elements not found');
        return;
    }
    
    const userMessage = chatInput.value.trim();
    
    // Hide any previous error messages
    if (errorMessage) {
        errorMessage.style.display = 'none';
    }
    
    // Validate input
    if (!userMessage) {
        showError('Please enter a message');
        return;
    }
    
    // Add user message to chat
    addMessage(userMessage, 'user');
    
    // Clear input and disable button
    chatInput.value = '';
    sendButton.disabled = true;
    
    // Handle loading state
    if (sendText) sendText.style.display = 'none';
    if (loadingText) loadingText.style.display = 'inline';
    
    try {
        console.log('Sending message to:', `${API_BASE_URL}/chat`);
        
        // Send request to backend - FIXED: matches your backend response model
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({
                message: userMessage,
                userId: generateUserId(), // Optional: generate a user ID
                timestamp: new Date().toISOString()
            })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Response error:', errorText);
            throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        // FIXED: Use the correct field name from your backend response
        if (data.success) {
            // Your backend returns 'message', not 'response'
            addMessage(data.message, 'bot');
        } else {
            // Show error from backend
            showError(data.error_message || 'Sorry, something went wrong. Please try again.');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Show user-friendly error message based on error type
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showError('Unable to connect to our chat service. Please check your internet connection and try again.');
        } else if (error.message.includes('CORS')) {
            showError('Connection blocked by browser security. Please try refreshing the page.');
        } else if (error.message.includes('400')) {
            showError('Invalid request. Please try a different message.');
        } else if (error.message.includes('500')) {
            showError('Server error. Our team has been notified. Please try again later.');
        } else {
            showError('Sorry, something went wrong. Please try again in a moment.');
        }
    } finally {
        // Re-enable button and reset loading state
        sendButton.disabled = false;
        if (sendText) sendText.style.display = 'inline';
        if (loadingText) loadingText.style.display = 'none';
        
        // Focus back on input
        chatInput.focus();
    }
}

function addMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Add timestamp
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    const messageContent = document.createElement('div');
    messageContent.innerHTML = `
        <p class="message-text">${escapeHtml(message)}</p>
        <span class="message-time">${timestamp}</span>
    `;
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom with smooth behavior
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    if (!errorDiv) {
        console.error('Error message div not found:', message);
        return;
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Hide error after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Generate a simple user ID for session tracking
function generateUserId() {
    return 'user_' + Math.random().toString(36).substr(2, 9);
}

// Enhanced connection test
// Enhanced connection test
async function testConnection() {
    try {
        console.log('Testing connection to:', `${API_BASE_URL}/health`);
        
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend connection successful:', data);
            return true;
        } else {
            console.warn('⚠️ Backend responded with error status:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
        return false;
    }
}

// Generate a simple user ID for session tracking
function generateUserId() {
    return 'user_' + Math.random().toString(36).substr(2, 9);
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    
    // Initialize carousel if elements exist
    if (document.querySelector('.carousel-dot')) {
        initCarousel();
    }
    
    // Set up chat input handler
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-focus on chat input
        chatInput.focus();
    }
    
    // Set up send button
    const sendButton = document.getElementById('sendButton');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    // Test connection on page load
    testConnection().then(connected => {
        if (!connected) {
            showError('Connection to chat service failed. Some features may not work properly.');
        }
    });
    
    console.log('Initialization complete');
});