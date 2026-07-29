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

const mobileMenuQuery = window.matchMedia("(max-width: 560px)");

function closeMobileMenu(header, toggle) {
  header.classList.remove("mobile-menu-open");
  toggle.setAttribute("aria-expanded", "false");
  toggle.setAttribute("aria-label", "Open navigation menu");
}

document.querySelectorAll(".mobile-menu-toggle").forEach((toggle) => {
  const header = toggle.closest(".suite-topbar, .topbar");

  if (!header) {
    return;
  }

  toggle.addEventListener("click", () => {
    const isOpen = header.classList.toggle("mobile-menu-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
    toggle.setAttribute(
      "aria-label",
      isOpen ? "Close navigation menu" : "Open navigation menu",
    );
  });

  header.querySelectorAll("nav a").forEach((link) => {
    link.addEventListener("click", () => closeMobileMenu(header, toggle));
  });

  mobileMenuQuery.addEventListener("change", (event) => {
    if (!event.matches) {
      closeMobileMenu(header, toggle);
    }
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") {
    return;
  }

  document.querySelectorAll(".mobile-menu-open").forEach((header) => {
    const toggle = header.querySelector(".mobile-menu-toggle");

    if (toggle) {
      closeMobileMenu(header, toggle);
      toggle.focus();
    }
  });
});
