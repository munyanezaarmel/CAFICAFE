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

const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://your-deployed-backend-url.com';

async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  addMessage("You", message);

  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data = await res.json();
  addMessage("Bot", data.response);
  input.value = "";
}

function addMessage(sender, text) {
  const chatBox = document.getElementById("chat-box");
  const msg = document.createElement("p");
  msg.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatBox.appendChild(msg);
}
