const htmlUrl = document.querySelector(".app").dataset.htmlUrl;
const inputHtml = document.querySelector("#inputHtml");
const outputHtml = document.querySelector("#outputHtml");
const formatButton = document.querySelector("#formatNow");
const controls = Array.from(document.querySelectorAll("[data-action]"));
const subOptionGroups = Array.from(
  document.querySelectorAll("[data-parent-action]"),
);
const selectedCount = document.querySelector("#selectedCount");
const inputCharacterCount = document.querySelector("#inputCharacterCount");
const inputLineCount = document.querySelector("#inputLineCount");
const outputCharacterCount = document.querySelector("#outputCharacterCount");
const outputLineCount = document.querySelector("#outputLineCount");
const inputLineNumbers = document.querySelector("#inputLineNumbers");
const outputLineNumbers = document.querySelector("#outputLineNumbers");
const initialHtml = inputHtml.value;
const defaultActions = new Set([
  "formatHtml",
  "removeComments",
  "removeScriptsStyles",
]);
const minimumProcessingMs = 350;
let toastTimer;
let refreshTimer;
let latestRequestId = 0;

const statisticNodes = {
  elements: document.querySelector("#htmlElements"),
  unique_tags: document.querySelector("#htmlUniqueTags"),
  comments: document.querySelector("#htmlComments"),
  scripts: document.querySelector("#htmlScripts"),
  styles: document.querySelector("#htmlStyles"),
  links: document.querySelector("#htmlLinks"),
  images: document.querySelector("#htmlImages"),
};

function selectedActions() {
  return controls
    .filter((control) => control.checked)
    .map((control) => control.dataset.action);
}

function selectedRadioValue(name, fallback) {
  return document.querySelector(`[name="${name}"]:checked`)?.value || fallback;
}

function applyDefaultActions() {
  controls.forEach((control) => {
    control.checked = defaultActions.has(control.dataset.action);
  });
  document.querySelector('[name="formatMode"][value="format"]').checked = true;
  document.querySelector('[name="indentSize"][value="2"]').checked = true;
  document.querySelector('[name="entityMode"][value="none"]').checked = true;
}

function syncSubOptions() {
  subOptionGroups.forEach((group) => {
    const parent = document.querySelector(
      `[data-action="${group.dataset.parentAction}"]`,
    );
    const enabled = parent?.checked ?? false;
    group.classList.toggle("is-disabled", !enabled);
    group.querySelectorAll("input").forEach((input) => {
      input.disabled = !enabled;
    });
  });
}

function syncExclusiveActions(changedAction) {
  const formatHtml = document.querySelector('[data-action="formatHtml"]');
  const plainText = document.querySelector('[data-action="plainText"]');

  if (changedAction === "plainText" && plainText.checked) {
    formatHtml.checked = false;
  }

  if (changedAction === "formatHtml" && formatHtml.checked) {
    plainText.checked = false;
  }
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function lineCount(text) {
  return text ? text.split(/\r\n|\r|\n/).length : 0;
}

function lineNumbersFor(text) {
  const count = Math.max(text.split(/\r\n|\r|\n/).length, 1);
  return Array.from({ length: count }, (_line, index) => index + 1).join("\n");
}

function syncLineNumberScroll(source, gutter) {
  gutter.scrollTop = source.scrollTop;
}

function updateLineNumbers() {
  inputLineNumbers.textContent = lineNumbersFor(inputHtml.value);
  outputLineNumbers.textContent = lineNumbersFor(outputHtml.textContent);
  syncLineNumberScroll(inputHtml, inputLineNumbers);
  syncLineNumberScroll(outputHtml, outputLineNumbers);
}

function updateTextStats() {
  inputCharacterCount.textContent = formatNumber(inputHtml.value.length);
  inputLineCount.textContent = formatNumber(lineCount(inputHtml.value));
  outputCharacterCount.textContent = formatNumber(
    outputHtml.textContent.length,
  );
  outputLineCount.textContent = formatNumber(lineCount(outputHtml.textContent));
  updateLineNumbers();
}

function updateSelectedCount() {
  syncSubOptions();
  const selected = controls.filter((control) => control.checked).length;
  selectedCount.textContent = `${selected} selected`;
}

function updateHtmlStats(statistics) {
  Object.entries(statisticNodes).forEach(([key, node]) => {
    node.textContent = formatNumber(statistics?.[key]);
  });
}

function setFormatProcessing(isProcessing) {
  formatButton.disabled = isProcessing;
  formatButton.classList.toggle("is-processing", isProcessing);
}

async function refresh() {
  clearTimeout(refreshTimer);
  const requestId = ++latestRequestId;
  const processingStartedAt = performance.now();

  updateSelectedCount();
  updateTextStats();
  setFormatProcessing(true);

  try {
    const response = await fetch(htmlUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputHtml.value,
        actions: selectedActions(),
        formatMode: selectedRadioValue("formatMode", "format"),
        entityMode: selectedRadioValue("entityMode", "none"),
        indentSize: Number(selectedRadioValue("indentSize", "2")),
      }),
    });
    const data = await response.json();

    if (requestId !== latestRequestId) {
      return;
    }

    if (!response.ok) {
      throw new Error();
    }

    outputHtml.textContent = data.output;
    updateHtmlStats(data.output_statistics);
  } catch {
    if (requestId === latestRequestId) {
      showToast("Unable to clean HTML");
    }
  } finally {
    if (requestId === latestRequestId) {
      updateTextStats();
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
    syncExclusiveActions(control.dataset.action);
    syncSubOptions();
    scheduleRefresh();
  });
});
document
  .querySelectorAll(
    '[name="formatMode"], [name="indentSize"], [name="entityMode"]',
  )
  .forEach((control) => {
    control.addEventListener("change", scheduleRefresh);
  });
inputHtml.addEventListener("input", () => {
  updateLineNumbers();
  scheduleRefresh();
});
inputHtml.addEventListener("scroll", () =>
  syncLineNumberScroll(inputHtml, inputLineNumbers),
);
outputHtml.addEventListener("scroll", () =>
  syncLineNumberScroll(outputHtml, outputLineNumbers),
);
formatButton.addEventListener("click", refresh);

document.querySelector("#resetOptions").addEventListener("click", () => {
  applyDefaultActions();
  syncSubOptions();
  refresh();
});

document.querySelector("#clearAll").addEventListener("click", () => {
  inputHtml.value = "";
  refresh();
  inputHtml.focus();
});

document.querySelector("#copyOutput").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(outputHtml.textContent);
    showToast("Copied");
  } catch {
    showToast("Copy unavailable");
  }
});

document.querySelector("#downloadOutput").addEventListener("click", () => {
  const file = new Blob([outputHtml.textContent], { type: "text/html" });
  const link = document.createElement("a");
  const today = formatDateForFilename(new Date());
  link.href = URL.createObjectURL(file);
  link.download = `HTMLCleanr-output-${today}.html`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Downloaded");
});

inputHtml.value = initialHtml;
applyDefaultActions();
syncSubOptions();
refresh();
