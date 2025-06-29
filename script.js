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

  prevBtn.addEventListener("click", () => {
    currentSlide = currentSlide === 0 ? totalSlides - 1 : currentSlide - 1;
    updateCarousel();
  });

  nextBtn.addEventListener("click", () => {
    currentSlide = currentSlide === totalSlides - 1 ? 0 : currentSlide + 1;
    updateCarousel();
  });

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

// ConfigurationAdd commentMore actions
const API_BASE_URL = 'https://caficafe-7.onrender.com'; 

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
    errorMessage.style.display = 'none';
    
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
    sendText.style.display = 'none';
    loadingText.style.display = 'inline';
    
    try {
        // Send request to backend
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userMessage
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Add bot response to chat
            addMessage(data.response, 'bot');
        } else {
            // Show error from backend
            showError(data.error_message || 'Sorry, something went wrong. Please try again.');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        
        // Show user-friendly error message
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showError('Unable to connect to our chat service. Please check your internet connection and try again.');
        } else {
            showError('Sorry, something went wrong. Please try again in a moment.');
        }
    } finally {
        // Re-enable button
        sendButton.disabled = false;
        sendText.style.display = 'inline';
        loadingText.style.display = 'none';
        
        // Focus back on input
        chatInput.focus();
    }
}

function addMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const messageP = document.createElement('p');
    messageP.textContent = message;
    
    messageDiv.appendChild(messageP);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Hide error after 5 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Allow sending message with Enter key
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

// Test connection on page load (optional)
async function testConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend connection successful');
        } else {
            console.warn('⚠️ Backend responded with error status');
        }
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
    }
}

// Uncomment the line below if you want to test connection on page load
// testConnection();