const app = document.querySelector(".app");
const formatUrl = app.dataset.formatUrl;
const inputText = document.querySelector("#inputText");
const outputText = document.querySelector("#outputText");
const inputCharacterCount = document.querySelector("#inputCharacterCount");
const inputWordCount = document.querySelector("#inputWordCount");
const inputLineCount = document.querySelector("#inputLineCount");
const outputCharacterCount = document.querySelector("#outputCharacterCount");
const outputWordCount = document.querySelector("#outputWordCount");
const outputLineCount = document.querySelector("#outputLineCount");
const charactersRemovedCount = document.querySelector(
  "#charactersRemovedCount",
);
const percentReduced = document.querySelector("#percentReduced");
const selectedCount = document.querySelector("#selectedCount");
const formatButton = document.querySelector("#formatNow");
const checkboxes = Array.from(document.querySelectorAll("[data-action]"));
const subOptionGroups = Array.from(
  document.querySelectorAll("[data-parent-action]"),
);
const configuredDefaultActions = (app.dataset.defaultActions || "")
  .split(",")
  .filter(Boolean);
const defaultActions = new Set(
  configuredDefaultActions.length
    ? configuredDefaultActions
    : [
        "removeLineBreaks",
        "replaceLineBreaksWithWhitespace",
        "removeBlankLines",
        "collapseSpaces",
        "trimWhitespace",
      ],
);
const initialText = inputText.value;
const minimumProcessingMs = 500;
const formatErrorMessage = "Unable to format text.\nPlease try again.";
let toastTimer;
let refreshTimer;
let latestRequestId = 0;

function selectedActions() {
  syncSubOptions();

  return checkboxes
    .filter((box) => box.checked && !box.disabled)
    .map((box) => box.dataset.action);
}

function syncSubOptions() {
  subOptionGroups.forEach((group) => {
    const parent = document.querySelector(
      `[data-action="${group.dataset.parentAction}"]`,
    );
    const enabled = parent?.checked ?? false;
    group.classList.toggle("is-disabled", !enabled);
    group.querySelectorAll("input").forEach((box) => {
      if (!enabled) {
        box.checked = false;
      }
      box.disabled = !enabled;
    });
  });
}

function applyDefaultActions() {
  checkboxes.forEach((box) => {
    box.checked = defaultActions.has(box.dataset.action);
  });
}

function setupTaskOptions() {
  const taskAction = app.dataset.taskAction;
  const primaryOption = document.querySelector(".task-primary-option");

  if (!taskAction || !primaryOption) {
    return;
  }

  const taskCheckbox = checkboxes.find(
    (box) => box.dataset.action === taskAction,
  );
  const taskRow = taskCheckbox?.closest(".option-row");

  if (taskRow) {
    primaryOption.append(taskRow);
  }
}

function updateSelectedCount() {
  syncSubOptions();
  const selectedRemoveActions = checkboxes.filter((box) => {
    return (
      box.checked &&
      !box.disabled &&
      box.closest(".option").textContent.trim().startsWith("Remove")
    );
  }).length;
  selectedCount.textContent = `${selectedRemoveActions} selected`;
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function formatDateForFilename(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function updateStats(target, statistics) {
  const stats = statistics || {};
  target.characters.textContent = formatNumber(stats.num_characters);
  target.words.textContent = formatNumber(stats.num_words);
  target.lines.textContent = formatNumber(stats.num_lines);
}

function updateReductionStats(statistics) {
  const stats = statistics || {};
  charactersRemovedCount.textContent = formatNumber(stats.characters_removed);
  percentReduced.textContent = `↓ ${formatNumber(stats.percent_reduced)}%`;
}

function updateResult(data) {
  outputText.textContent = data.output;
  updateStats(
    {
      characters: inputCharacterCount,
      words: inputWordCount,
      lines: inputLineCount,
    },
    data.input_statistics,
  );
  updateStats(
    {
      characters: outputCharacterCount,
      words: outputWordCount,
      lines: outputLineCount,
    },
    data.output_statistics,
  );
  updateReductionStats(data.reduction_statistics);
}

function setFormatProcessing(isProcessing) {
  formatButton.disabled = isProcessing;
  formatButton.classList.toggle("is-processing", isProcessing);
}

async function refresh() {
  clearTimeout(refreshTimer);
  const actions = selectedActions();
  const requestId = ++latestRequestId;
  const processingStartedAt = performance.now();

  updateSelectedCount();
  setFormatProcessing(true);

  try {
    const response = await fetch(formatUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: inputText.value, actions }),
    });

    if (!response.ok) {
      if (requestId === latestRequestId) {
        showToast(formatErrorMessage);
      }
      return;
    }

    const data = await response.json();
    if (requestId !== latestRequestId) {
      return;
    }

    if (typeof data.output === "string") {
      updateResult(data);
    } else {
      showToast(formatErrorMessage);
    }
  } catch {
    if (requestId === latestRequestId) {
      showToast(formatErrorMessage);
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

function showToast(message) {
  const toast = document.querySelector("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 1600);
}

checkboxes.forEach((box) => {
  box.addEventListener("change", () => {
    syncSubOptions();
    scheduleRefresh();
  });
});

inputText.addEventListener("input", scheduleRefresh);
formatButton.addEventListener("click", refresh);

document.querySelector("#resetOptions").addEventListener("click", () => {
  applyDefaultActions();
  syncSubOptions();
  refresh();
});

document.querySelector("#clearAll").addEventListener("click", () => {
  inputText.value = "";
  refresh();
  inputText.focus();
});

document.querySelector("#copyOutput").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(outputText.textContent);
    showToast("Copied");
  } catch {
    showToast("Copy unavailable");
  }
});

document.querySelector("#downloadOutput").addEventListener("click", () => {
  const file = new Blob([outputText.textContent], { type: "text/plain" });
  const link = document.createElement("a");
  const today = formatDateForFilename(new Date());
  link.href = URL.createObjectURL(file);
  link.download = `TextCleanr-output-${today}.txt`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Downloaded");
});

inputText.value = initialText;
setupTaskOptions();
applyDefaultActions();
syncSubOptions();
refresh();
