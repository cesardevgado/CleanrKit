const markdownUrl = document.querySelector(".app").dataset.markdownUrl;
const inputMarkdown = document.querySelector("#inputMarkdown");
const outputMarkdown = document.querySelector("#outputMarkdown");
const formatButton = document.querySelector("#formatNow");
const controls = Array.from(document.querySelectorAll("[data-action]"));
const subOptionGroups = Array.from(document.querySelectorAll("[data-parent-action]"));
const linkCleanupModes = Array.from(document.querySelectorAll('[name="linkCleanupMode"]'));
const imageCleanupModes = Array.from(document.querySelectorAll('[name="imageCleanupMode"]'));
const selectedCount = document.querySelector("#selectedCount");
const inputCharacterCount = document.querySelector("#inputCharacterCount");
const inputWordCount = document.querySelector("#inputWordCount");
const inputLineCount = document.querySelector("#inputLineCount");
const outputCharacterCount = document.querySelector("#outputCharacterCount");
const outputWordCount = document.querySelector("#outputWordCount");
const outputLineCount = document.querySelector("#outputLineCount");
const initialMarkdown = inputMarkdown.value;
const defaultActions = new Set(["cleanMarkdown", "normalizeHeaders"]);
const minimumProcessingMs = 350;
let toastTimer;
let refreshTimer;
let latestRequestId = 0;

const headingNodes = {
  total: document.querySelector("#headingTotal"),
  h1: document.querySelector("#headingH1"),
  h2: document.querySelector("#headingH2"),
  h3: document.querySelector("#headingH3"),
  h4h6: document.querySelector("#headingH4H6")
};

function selectedActions() {
  return controls.filter((control) => control.checked).map((control) => control.dataset.action);
}

function selectedLinkCleanupMode() {
  return linkCleanupModes.find((mode) => mode.checked)?.value || "label";
}

function selectedImageCleanupMode() {
  return imageCleanupModes.find((mode) => mode.checked)?.value || "label";
}

function applyDefaultActions() {
  controls.forEach((control) => {
    control.checked = defaultActions.has(control.dataset.action);
  });
  linkCleanupModes.forEach((mode) => {
    mode.checked = mode.value === "label";
  });
  imageCleanupModes.forEach((mode) => {
    mode.checked = mode.value === "label";
  });
}

function syncSubOptions() {
  subOptionGroups.forEach((group) => {
    const parent = document.querySelector(`[data-action="${group.dataset.parentAction}"]`);
    const enabled = parent?.checked ?? false;
    group.classList.toggle("is-disabled", !enabled);
    group.querySelectorAll("input").forEach((input) => {
      input.disabled = !enabled;
    });
  });
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function updateStats(statistics, nodes) {
  nodes.characters.textContent = formatNumber(statistics?.characters);
  nodes.words.textContent = formatNumber(statistics?.words);
  nodes.lines.textContent = formatNumber(statistics?.lines);
}

function updateHeadingStats(statistics) {
  const stats = statistics || {};
  headingNodes.total.textContent = formatNumber(stats.total);
  headingNodes.h1.textContent = formatNumber(stats.h1);
  headingNodes.h2.textContent = formatNumber(stats.h2);
  headingNodes.h3.textContent = formatNumber(stats.h3);
  headingNodes.h4h6.textContent = formatNumber((stats.h4 || 0) + (stats.h5 || 0) + (stats.h6 || 0));
}

function updateSelectedCount() {
  syncSubOptions();
  const selected = controls.filter((control) => control.checked).length;
  selectedCount.textContent = `${selected} selected`;
}

function setFormatProcessing(isProcessing) {
  formatButton.disabled = isProcessing;
  formatButton.classList.toggle("is-processing", isProcessing);
}

function syncHtmlOptions(changedAction) {
  const htmlToMarkdown = document.querySelector('[data-action="htmlToMarkdown"]');
  const removeHtml = document.querySelector('[data-action="removeHtml"]');

  if (changedAction === "htmlToMarkdown" && htmlToMarkdown.checked) {
    removeHtml.checked = false;
  }

  if (changedAction === "removeHtml" && removeHtml.checked) {
    htmlToMarkdown.checked = false;
  }
}

async function refresh() {
  clearTimeout(refreshTimer);
  const requestId = ++latestRequestId;
  const processingStartedAt = performance.now();

  updateSelectedCount();
  setFormatProcessing(true);

  try {
    const response = await fetch(markdownUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputMarkdown.value,
        actions: selectedActions(),
        linkCleanupMode: selectedLinkCleanupMode(),
        imageCleanupMode: selectedImageCleanupMode()
      })
    });
    const data = await response.json();

    if (requestId !== latestRequestId) {
      return;
    }

    if (!response.ok) {
      throw new Error();
    }

    outputMarkdown.textContent = data.output;
    updateStats(data.input_statistics, {
      characters: inputCharacterCount,
      words: inputWordCount,
      lines: inputLineCount
    });
    updateStats(data.output_statistics, {
      characters: outputCharacterCount,
      words: outputWordCount,
      lines: outputLineCount
    });
    updateHeadingStats(data.heading_statistics);
  } catch {
    if (requestId === latestRequestId) {
      showToast("Unable to clean Markdown");
    }
  } finally {
    if (requestId === latestRequestId) {
      const elapsedMs = performance.now() - processingStartedAt;
      const remainingMs = Math.max(minimumProcessingMs - elapsedMs, 0);
      setTimeout(() => {
        if (requestId === latestRequestId) {
          setFormatProcessing(false);
        }
      }, remainingMs);
    }
  }
}

function scheduleRefresh() {
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(refresh, 250);
}

function formatDateForFilename(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 1600);
}

controls.forEach((control) => {
  control.addEventListener("change", () => {
    syncHtmlOptions(control.dataset.action);
    syncSubOptions();
    scheduleRefresh();
  });
});
linkCleanupModes.forEach((mode) => mode.addEventListener("change", scheduleRefresh));
imageCleanupModes.forEach((mode) => mode.addEventListener("change", scheduleRefresh));
inputMarkdown.addEventListener("input", scheduleRefresh);
formatButton.addEventListener("click", refresh);

document.querySelector("#resetOptions").addEventListener("click", () => {
  applyDefaultActions();
  refresh();
});

document.querySelector("#clearAll").addEventListener("click", () => {
  inputMarkdown.value = "";
  refresh();
  inputMarkdown.focus();
});

document.querySelector("#copyOutput").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(outputMarkdown.textContent);
    showToast("Copied");
  } catch {
    showToast("Copy unavailable");
  }
});

document.querySelector("#downloadOutput").addEventListener("click", () => {
  const file = new Blob([outputMarkdown.textContent], { type: "text/markdown" });
  const link = document.createElement("a");
  const today = formatDateForFilename(new Date());
  link.href = URL.createObjectURL(file);
  link.download = `markdownscrubbr-output-${today}.md`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Downloaded");
});

inputMarkdown.value = initialMarkdown;
applyDefaultActions();
syncSubOptions();
refresh();
