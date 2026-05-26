const THEME_STORAGE_KEY = "todo-ui-theme";

function resolveInitialTheme() {
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  if (savedTheme === "light" || savedTheme === "dark") {
    return savedTheme;
  }
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
}

function setupThemeToggle() {
  const toggleButton = document.getElementById("theme-toggle");
  if (!toggleButton) {
    return;
  }
  toggleButton.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem(THEME_STORAGE_KEY, next);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  applyTheme(resolveInitialTheme());
  setupThemeToggle();
});
