const builtForWord = document.querySelector(".built-for-word");

if (builtForWord) {
  const words = [
    "developers.",
    "analysts.",
    "designers.",
    "creators.",
    "everyone.",
    "YOU.",
  ];
  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;
  let wordIndex = 0;

  setInterval(() => {
    wordIndex = (wordIndex + 1) % words.length;

    if (reduceMotion) {
      builtForWord.textContent = words[wordIndex];
      return;
    }

    builtForWord.classList.add("is-changing");
    setTimeout(() => {
      builtForWord.textContent = words[wordIndex];
      builtForWord.classList.remove("is-changing");
    }, 180);
  }, 2400);
}
