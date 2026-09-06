document.addEventListener("DOMContentLoaded", () => {
  // 1. Dynamic Typing Effect
  const words = ["AI Engineer", "Software Engineer", "Problem Solver"];
  let wordIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  const typedTextSpan = document.getElementById("typed-text");
  const typingSpeed = 100;
  const deletingSpeed = 60;
  const pauseTime = 1800;

  function type() {
    const currentWord = words[wordIndex];

    if (isDeleting) {
      typedTextSpan.textContent = currentWord.substring(0, charIndex - 1);
      charIndex--;
    } else {
      typedTextSpan.textContent = currentWord.substring(0, charIndex + 1);
      charIndex++;
    }

    let currentSpeed = isDeleting ? deletingSpeed : typingSpeed;

    if (!isDeleting && charIndex === currentWord.length) {
      currentSpeed = pauseTime;
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      wordIndex = (wordIndex + 1) % words.length;
      currentSpeed = 500;
    }

    setTimeout(type, currentSpeed);
  }

  type();

  // 2. Sticky Navbar Glass Effect
  const navbar = document.getElementById("navbar");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 40) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });

  // 3. Mobile Navigation Menu Toggle
  const hamburger = document.getElementById("hamburger");
  const navLinks = document.getElementById("nav-links");
  const allNavLinks = document.querySelectorAll(".nav-link");

  hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("active");
    const icon = hamburger.querySelector("i");
    icon.classList.toggle("fa-bars");
    icon.classList.toggle("fa-xmark");
  });

  // Close mobile drawer when a link is clicked
  allNavLinks.forEach((link) => {
    link.addEventListener("click", () => {
      navLinks.classList.remove("active");
      const icon = hamburger.querySelector("i");
      icon.classList.add("fa-bars");
      icon.classList.remove("fa-xmark");
    });
  });

  // 4. Contact Form Handling
  const form = document.getElementById("contact-form");
  const formStatus = document.getElementById("form-status");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    formStatus.textContent = "Sending message...";
    formStatus.style.color = "#38bdf8";

    // Simulate an async sending request
    setTimeout(() => {
      formStatus.textContent =
        "Thank you! Your message has been sent successfully.";
      formStatus.style.color = "#10b981";
      form.reset();

      setTimeout(() => {
        formStatus.textContent = "";
      }, 5000);
    }, 1000);
  });

  // 5. Dynamic Footer Year
  document.getElementById("year").textContent = new Date().getFullYear();
});
