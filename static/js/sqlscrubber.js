const sqlUrl = document.querySelector(".app").dataset.sqlUrl;
const inputSql = document.querySelector("#inputSql");
const outputSql = document.querySelector("#outputSql");
const formatButton = document.querySelector("#formatNow");
const controls = Array.from(document.querySelectorAll("[data-action]"));
const subOptionGroups = Array.from(
  document.querySelectorAll("[data-parent-action]"),
);
const selectedCount = document.querySelector("#selectedCount");
const sqlStatus = document.querySelector("#sqlStatus");
const sqlStatusText = document.querySelector("#sqlStatusText");
const inputCharacterCount = document.querySelector("#inputCharacterCount");
const inputLineCount = document.querySelector("#inputLineCount");
const outputCharacterCount = document.querySelector("#outputCharacterCount");
const outputLineCount = document.querySelector("#outputLineCount");
const inputLineNumbers = document.querySelector("#inputLineNumbers");
const outputLineNumbers = document.querySelector("#outputLineNumbers");
const initialSql = inputSql.value;
const defaultActions = new Set(["formatSql", "normalizeWhitespace"]);
const minimumProcessingMs = 350;
let toastTimer;
let refreshTimer;
let latestRequestId = 0;

const statisticNodes = {
  lines: document.querySelector("#sqlLines"),
  characters: document.querySelector("#sqlCharacters"),
  tables_used: document.querySelector("#sqlTables"),
  joins: document.querySelector("#sqlJoins"),
  where_clauses: document.querySelector("#sqlWhere"),
  subqueries: document.querySelector("#sqlSubqueries"),
  complexity: document.querySelector("#sqlComplexity"),
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
  document.querySelector('[name="keywordCase"][value="upper"]').checked = true;
  document.querySelector('[name="indentSize"][value="4"]').checked = true;
  document.querySelector('[name="formatMode"][value="expanded"]').checked =
    true;
}

function syncSubOptions() {
  subOptionGroups.forEach((group) => {
    const parent = document.querySelector(
      `[data-action="${group.dataset.parentAction}"]`,
    );
    const keywordCasing = document.querySelector(
      '[data-action="keywordCasing"]',
    );
    const enabled =
      (parent?.checked ?? false) ||
      (group.dataset.parentAction === "formatSql" && keywordCasing?.checked);
    group.classList.toggle("is-disabled", !enabled);
    group.querySelectorAll("input").forEach((input) => {
      input.disabled = !enabled;
    });
  });
}

function formatNumber(value) {
  return typeof value === "number" ? value.toLocaleString() : value || "0";
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
  inputLineNumbers.textContent = lineNumbersFor(inputSql.value);
  outputLineNumbers.textContent = lineNumbersFor(outputSql.textContent);
  syncLineNumberScroll(inputSql, inputLineNumbers);
  syncLineNumberScroll(outputSql, outputLineNumbers);
}

function updateTextStats() {
  inputCharacterCount.textContent = formatNumber(inputSql.value.length);
  inputLineCount.textContent = formatNumber(lineCount(inputSql.value));
  outputCharacterCount.textContent = formatNumber(outputSql.textContent.length);
  outputLineCount.textContent = formatNumber(lineCount(outputSql.textContent));
  updateLineNumbers();
}

function updateSelectedCount() {
  syncSubOptions();
  const selected = controls.filter((control) => control.checked).length;
  selectedCount.textContent = `${selected} selected`;
}

function updateSqlStats(statistics) {
  Object.entries(statisticNodes).forEach(([key, node]) => {
    node.textContent = formatNumber(statistics?.[key]);
  });
}

function setValidationState(isValid, message) {
  sqlStatus.classList.toggle("is-invalid", !isValid);
  sqlStatusText.textContent = message;
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
    const response = await fetch(sqlUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputSql.value,
        actions: selectedActions(),
        keywordCase: selectedRadioValue("keywordCase", "upper"),
        indentSize: Number(selectedRadioValue("indentSize", "4")),
        formatMode: selectedRadioValue("formatMode", "expanded"),
      }),
    });
    const data = await response.json();

    if (requestId !== latestRequestId) {
      return;
    }

    if (!response.ok) {
      throw new Error();
    }

    outputSql.textContent = data.output;
    setValidationState(data.valid, data.validation_message);
    updateSqlStats(data.statistics);
  } catch {
    if (requestId === latestRequestId) {
      showToast("Unable to format SQL");
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
    syncSubOptions();
    scheduleRefresh();
  });
});
document
  .querySelectorAll(
    '[name="keywordCase"], [name="indentSize"], [name="formatMode"]',
  )
  .forEach((control) => {
    control.addEventListener("change", scheduleRefresh);
  });
inputSql.addEventListener("input", () => {
  updateLineNumbers();
  scheduleRefresh();
});
inputSql.addEventListener("scroll", () =>
  syncLineNumberScroll(inputSql, inputLineNumbers),
);
outputSql.addEventListener("scroll", () =>
  syncLineNumberScroll(outputSql, outputLineNumbers),
);
formatButton.addEventListener("click", refresh);

document.querySelector("#resetOptions").addEventListener("click", () => {
  applyDefaultActions();
  syncSubOptions();
  refresh();
});

document.querySelector("#clearAll").addEventListener("click", () => {
  inputSql.value = "";
  refresh();
  inputSql.focus();
});

document.querySelector("#copyOutput").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(outputSql.textContent);
    showToast("Copied");
  } catch {
    showToast("Copy unavailable");
  }
});

document.querySelector("#downloadOutput").addEventListener("click", () => {
  const file = new Blob([outputSql.textContent], { type: "application/sql" });
  const link = document.createElement("a");
  const today = formatDateForFilename(new Date());
  link.href = URL.createObjectURL(file);
  link.download = `SQLCleanr-output-${today}.sql`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Downloaded");
});

inputSql.value = initialSql;
applyDefaultActions();
syncSubOptions();
refresh();
