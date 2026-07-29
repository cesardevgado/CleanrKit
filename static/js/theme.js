const themeToggle = document.querySelector("#themeToggle");
const colorSchemePreference = window.matchMedia("(prefers-color-scheme: dark)");
let themeWasManuallySet = false;

function setTheme(useDarkTheme) {
  document.documentElement.classList.toggle("dark", useDarkTheme);
  themeToggle?.setAttribute("aria-pressed", String(useDarkTheme));
  themeToggle?.setAttribute(
    "aria-label",
    `Switch to ${useDarkTheme ? "light" : "dark"} mode`,
  );
}

setTheme(colorSchemePreference.matches);

themeToggle?.addEventListener("click", () => {
  themeWasManuallySet = true;
  setTheme(!document.documentElement.classList.contains("dark"));
});

colorSchemePreference.addEventListener("change", (event) => {
  if (!themeWasManuallySet) {
    setTheme(event.matches);
  }
});
