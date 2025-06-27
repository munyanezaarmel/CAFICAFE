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

// Chat button functionality
function initChatButton() {
  const chatBtn = document.getElementById("chat-btn");
  chatBtn.addEventListener("click", () => {
    const chatbox = document.getElementById("chatbox");
    if (chatbox) {
      chatbox.scrollIntoView({ behavior: "smooth" });
    }
  });
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
        });
      }
    });
  });
}

// Initialize all functionality when page loads
document.addEventListener("DOMContentLoaded", () => {
  initCarousel();
  initChatButton();
  initSmoothScrolling();
});
