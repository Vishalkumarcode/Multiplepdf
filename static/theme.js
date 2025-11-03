// Zistal Theme Toggle (default = light theme)
document.addEventListener("DOMContentLoaded", () => {
  const STORAGE_KEY = "zistal_theme";
  const toggleButton = document.getElementById("theme-toggle");

  // Load saved theme or default to light
  let currentTheme = localStorage.getItem(STORAGE_KEY) || "light";
  applyTheme(currentTheme);

  if (toggleButton) {
    toggleButton.addEventListener("click", () => {
      currentTheme = currentTheme === "light" ? "dark" : "light";
      localStorage.setItem(STORAGE_KEY, currentTheme);
      applyTheme(currentTheme);
    });
  }

  function applyTheme(theme) {
    document.body.classList.remove("light-theme", "dark-theme");
    document.body.classList.add(theme === "dark" ? "dark-theme" : "light-theme");

    if (toggleButton) {
      toggleButton.innerHTML = theme === "dark" ? "🌙" : "☀️";
    }
  }
});
