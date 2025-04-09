// main.js — central JavaScript for all frontend features

document.addEventListener("DOMContentLoaded", function () {
  // ===== Materialize Init =====
  M.AutoInit();

  // ===== Parallax Init =====

  const parallaxElems = document.querySelectorAll(".parallax");
  M.Parallax.init(parallaxElems);

  // ===== Sidenav Init =====
  const sidenavElems = document.querySelectorAll('.sidenav');
  M.Sidenav.init(sidenavElems);

  // ===== Modal Init =====
  const modalElems = document.querySelectorAll(".modal");
  M.Modal.init(modalElems);

  // ===== WOW Animation Init =====
  if (typeof WOW === 'function') {
    new WOW().init();
  }

  // ===== Dark Mode Toggle =====
  const toggleBtn = document.getElementById("darkModeToggle");
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
    });
  }

  // ===== Form Error Toasts =====
  const djangoErrors = document.querySelectorAll(".django-error");
  djangoErrors.forEach(el => {
    M.toast({ html: el.textContent.trim(), classes: 'red darken-1 white-text' });
  });

  // ===== Password Strength Checker =====
  const passwordInput = document.querySelector('#id_password1');
  const strengthDisplay = document.getElementById('password-strength');

  if (passwordInput && strengthDisplay) {
    passwordInput.addEventListener('input', () => {
      const val = passwordInput.value;
      let strength = '';

      if (val.length < 6) {
        strength = 'Too short';
        strengthDisplay.className = 'red-text';
      } else if (/[A-Za-z]/.test(val) && /\d/.test(val) && val.length >= 8) {
        strength = 'Strong password';
        strengthDisplay.className = 'green-text';
      } else {
        strength = 'Weak password';
        strengthDisplay.className = 'orange-text';
      }

      strengthDisplay.textContent = strength;
    });
  }

  // ===== Spinner on Submit (Signup) =====
  const signupForm = document.querySelector("form[onsubmit='showSpinner()']");
  if (signupForm) {
    signupForm.addEventListener("submit", () => {
      const btn = document.getElementById("submit-btn");
      const spinner = document.getElementById("spinner");
      if (btn && spinner) {
        btn.style.display = "none";
        spinner.style.display = "inline-block";
      }
    });
  }
});

// ===== Autocomplete Search =====
function fetchSuggestions() {
  const input = document.getElementById("search");
  const suggestionsList = document.getElementById("suggestions-list");
  const query = input.value.trim();

  if (query.length < 2) {
    suggestionsList.style.display = "none";
    return;
  }

  fetch(`/reviews/autocomplete/?query=${encodeURIComponent(query)}`)
    .then((res) => res.json())
    .then((data) => {
      suggestionsList.innerHTML = "";
      if (data.length === 0) {
        suggestionsList.style.display = "none";
        return;
      }

      data.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        li.onclick = () => {
          input.value = item;
          suggestionsList.style.display = "none";
          document.getElementById("searchForm").submit();
        };
        suggestionsList.appendChild(li);
      });

      suggestionsList.style.display = "block";
    })
    .catch((err) => console.error("Autocomplete error:", err));
}


function showSpinner() {
  const btn = document.getElementById("submit-btn");
  const spinner = document.getElementById("spinner");
  if (btn && spinner) {
    btn.style.display = "none";
    spinner.style.display = "inline-block";
  }
}

window.addEventListener("click", (e) => {
  const target = e.target;
  if (!target.closest("#search") && !target.closest("#suggestions-list")) {
    const suggestionsList = document.getElementById("suggestions-list");
    if (suggestionsList) suggestionsList.style.display = "none";
  }
});

// ===== Smooth Scroll for Anchor Links =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });


});
