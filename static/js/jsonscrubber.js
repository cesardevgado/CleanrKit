const app = document.querySelector(".app");
const jsonUrl = app.dataset.jsonUrl;
const inputJson = document.querySelector("#inputJson");
const outputJson = document.querySelector("#outputJson");
const formatButton = document.querySelector("#formatNow");
const controls = Array.from(document.querySelectorAll("[data-action]"));
const selectedCount = document.querySelector("#selectedCount");
const jsonStatus = document.querySelector("#jsonStatus");
const jsonStatusText = document.querySelector("#jsonStatusText");
const inputCharacterCount = document.querySelector("#inputCharacterCount");
const inputLineCount = document.querySelector("#inputLineCount");
const outputCharacterCount = document.querySelector("#outputCharacterCount");
const outputLineCount = document.querySelector("#outputLineCount");
const inputLineNumbers = document.querySelector("#inputLineNumbers");
const outputLineNumbers = document.querySelector("#outputLineNumbers");
const inputErrorLine = document.querySelector("#inputErrorLine");
const initialJson = inputJson.value;
const configuredDefaultActions = (app.dataset.defaultActions || "")
  .split(",")
  .filter(Boolean);
const defaultActions = new Set(
  configuredDefaultActions.length
    ? configuredDefaultActions
    : ["prettyPrintJson", "validateJson", "sortKeys", "removeDuplicateKeys"],
);
const minimumProcessingMs = 350;
let toastTimer;
let refreshTimer;
let latestRequestId = 0;
let inputErrorLineNumber = null;

const statisticNodes = {
  objects: document.querySelector("#jsonObjects"),
  arrays: document.querySelector("#jsonArrays"),
  keys: document.querySelector("#jsonKeys"),
  nodes: document.querySelector("#jsonNodes"),
  max_depth: document.querySelector("#jsonDepth"),
  duplicate_keys: document.querySelector("#jsonDuplicates"),
  nulls: document.querySelector("#jsonNulls"),
  strings: document.querySelector("#jsonStrings"),
  numbers: document.querySelector("#jsonNumbers"),
  booleans: document.querySelector("#jsonBooleans")
};

function selectedActions() {
  return controls.filter((control) => control.checked).map((control) => control.dataset.action);
}

function applyDefaultActions() {
  controls.forEach((control) => {
    control.checked = defaultActions.has(control.dataset.action);
  });
}

function setupTaskOptions() {
  const taskAction = app.dataset.taskAction;
  const primaryOption = document.querySelector(".task-primary-option");

  if (!taskAction || !primaryOption) {
    return;
  }

  const taskControl = controls.find(
    (control) => control.dataset.action === taskAction,
  );
  const taskRow = taskControl?.closest(".option-row");

  if (taskRow) {
    primaryOption.append(taskRow);
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

function lineHeightFor(element) {
  const lineHeight = Number.parseFloat(getComputedStyle(element).lineHeight);
  return Number.isFinite(lineHeight) ? lineHeight : 24;
}

function updateErrorLinePosition() {
  if (!inputErrorLineNumber) {
    inputErrorLine.classList.remove("is-visible");
    return;
  }

  const lineHeight = lineHeightFor(inputJson);
  const top = 22 + (inputErrorLineNumber - 1) * lineHeight - inputJson.scrollTop;
  inputErrorLine.style.setProperty("--error-line-top", `${top}px`);
  inputErrorLine.style.setProperty("--error-line-height", `${lineHeight}px`);
  inputErrorLine.classList.add("is-visible");
}

function setInputErrorLine(lineNumber) {
  inputErrorLineNumber = Number.isFinite(Number(lineNumber)) ? Number(lineNumber) : null;
  updateErrorLinePosition();
}

function updateLineNumbers() {
  inputLineNumbers.textContent = lineNumbersFor(inputJson.value);
  outputLineNumbers.textContent = lineNumbersFor(outputJson.textContent);
  syncLineNumberScroll(inputJson, inputLineNumbers);
  syncLineNumberScroll(outputJson, outputLineNumbers);
  updateErrorLinePosition();
}

function updateTextStats() {
  inputCharacterCount.textContent = formatNumber(inputJson.value.length);
  inputLineCount.textContent = formatNumber(lineCount(inputJson.value));
  outputCharacterCount.textContent = formatNumber(outputJson.textContent.length);
  outputLineCount.textContent = formatNumber(lineCount(outputJson.textContent));
  updateLineNumbers();
}

function updateSelectedCount() {
  const selected = controls.filter((control) => control.checked).length;
  selectedCount.textContent = `${selected} selected`;
}

function updateJsonStats(statistics) {
  Object.entries(statisticNodes).forEach(([key, node]) => {
    node.textContent = formatNumber(statistics?.[key]);
  });
}

function setValidationState(isValid, message) {
  jsonStatus.classList.toggle("is-invalid", !isValid);
  jsonStatusText.textContent = message;
}

function setFormatProcessing(isProcessing) {
  formatButton.disabled = isProcessing;
  formatButton.classList.toggle("is-processing", isProcessing);
}

function syncFormatMode() {
  const prettyPrint = document.querySelector('[data-action="prettyPrintJson"]');
  const minify = document.querySelector('[data-action="minifyJson"]');

  if (!prettyPrint.checked && !minify.checked) {
    prettyPrint.checked = true;
  }
}

async function refresh() {
  clearTimeout(refreshTimer);
  const requestId = ++latestRequestId;
  const processingStartedAt = performance.now();

  updateSelectedCount();
  updateTextStats();
  setFormatProcessing(true);

  try {
    const response = await fetch(jsonUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputJson.value, actions: selectedActions() })
    });
    const data = await response.json();

    if (requestId !== latestRequestId) {
      return;
    }

    if (!response.ok) {
      throw new Error();
    }

    if (data.valid) {
      outputJson.textContent = data.output;
      setValidationState(true, "Valid JSON");
      setInputErrorLine(null);
      updateJsonStats(data.statistics);
    } else {
      outputJson.textContent = data.error;
      setValidationState(false, data.error);
      setInputErrorLine(data.error_line);
      updateJsonStats({});
    }
  } catch {
    if (requestId === latestRequestId) {
      outputJson.textContent = "";
      setValidationState(false, "Unable to format JSON");
      setInputErrorLine(null);
      showToast("Unable to format JSON");
      updateJsonStats({});
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
    syncFormatMode();
    scheduleRefresh();
  });
});

inputJson.addEventListener("input", () => {
  setInputErrorLine(null);
  updateLineNumbers();
  scheduleRefresh();
});
inputJson.addEventListener("scroll", () => {
  syncLineNumberScroll(inputJson, inputLineNumbers);
  updateErrorLinePosition();
});
outputJson.addEventListener("scroll", () => syncLineNumberScroll(outputJson, outputLineNumbers));
formatButton.addEventListener("click", refresh);

document.querySelector("#resetOptions").addEventListener("click", () => {
  applyDefaultActions();
  syncFormatMode();
  refresh();
});

document.querySelector("#clearAll").addEventListener("click", () => {
  inputJson.value = "";
  refresh();
  inputJson.focus();
});

document.querySelector("#copyOutput").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(outputJson.textContent);
    showToast("Copied");
  } catch {
    showToast("Copy unavailable");
  }
});

document.querySelector("#downloadOutput").addEventListener("click", () => {
  const file = new Blob([outputJson.textContent], { type: "application/json" });
  const link = document.createElement("a");
  const today = formatDateForFilename(new Date());
  link.href = URL.createObjectURL(file);
  link.download = `jsonscrubber-output-${today}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Downloaded");
});

inputJson.value = initialJson;
setupTaskOptions();
applyDefaultActions();
syncFormatMode();
refresh();
