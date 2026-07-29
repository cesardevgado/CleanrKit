const csvUrl = document.querySelector(".app").dataset.csvUrl;
const inputCsv = document.querySelector("#inputCsv");
const outputCsv = document.querySelector("#outputCsv");
const formatButton = document.querySelector("#formatNow");
const controls = Array.from(document.querySelectorAll("[data-action]"));
const nullReplacement = document.querySelector("#nullReplacement");
const selectedCount = document.querySelector("#selectedCount");
const csvStatus = document.querySelector("#csvStatus");
const csvPreviewTable = document.querySelector("#csvPreviewTable");
const columnStats = document.querySelector("#columnStats");
const inputCharacterCount = document.querySelector("#inputCharacterCount");
const inputLineCount = document.querySelector("#inputLineCount");
const outputCharacterCount = document.querySelector("#outputCharacterCount");
const outputLineCount = document.querySelector("#outputLineCount");
const initialCsv = inputCsv.value;
const defaultActions = new Set([
  "removeDuplicateRows",
  "removeEmptyRows",
  "trimCells",
  "normalizeHeaders",
]);
const minimumProcessingMs = 350;
let toastTimer;
let refreshTimer;
let latestRequestId = 0;

const statisticNodes = {
  rows: document.querySelector("#csvRows"),
  columns: document.querySelector("#csvColumns"),
  empty_cells: document.querySelector("#csvEmptyCells"),
  duplicate_rows_removed: document.querySelector("#csvDuplicatesRemoved"),
  empty_rows_removed: document.querySelector("#csvEmptyRowsRemoved"),
  null_values_replaced: document.querySelector("#csvNullsReplaced"),
};

function selectedActions() {
  return controls
    .filter((control) => control.checked)
    .map((control) => control.dataset.action);
}

function applyDefaultActions() {
  controls.forEach((control) => {
    control.checked = defaultActions.has(control.dataset.action);
  });
}

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function lineCount(text) {
  return text ? text.split(/\r\n|\r|\n/).length : 0;
}

function updateTextStats() {
  inputCharacterCount.textContent = formatNumber(inputCsv.value.length);
  inputLineCount.textContent = formatNumber(lineCount(inputCsv.value));
  outputCharacterCount.textContent = formatNumber(outputCsv.textContent.length);
  outputLineCount.textContent = formatNumber(lineCount(outputCsv.textContent));
}

function updateSelectedCount() {
  const selected = controls.filter((control) => control.checked).length;
  selectedCount.textContent = `${selected} selected`;
}

function updateCsvStats(statistics) {
  Object.entries(statisticNodes).forEach(([key, node]) => {
    node.textContent = formatNumber(statistics?.[key]);
  });
  renderColumnStats(statistics?.columns_detail || []);
}

function renderColumnStats(columns) {
  columnStats.innerHTML = "";

  columns.forEach((column) => {
    const item = document.createElement("div");
    item.className = "column-stat";
    item.innerHTML = `
      <strong></strong>
      <span><b>${formatNumber(column.filled)}</b> filled</span>
      <span><b>${formatNumber(column.empty)}</b> empty</span>
      <span><b>${formatNumber(column.unique)}</b> unique</span>
    `;
    item.querySelector("strong").textContent = column.name;
    columnStats.appendChild(item);
  });
}

function renderPreview(rows) {
  csvPreviewTable.innerHTML = "";

  if (!rows?.length) {
    const row = csvPreviewTable.insertRow();
    const cell = row.insertCell();
    cell.textContent = "No rows to preview";
    return;
  }

  rows.forEach((cells, rowIndex) => {
    const row = csvPreviewTable.insertRow();

    cells.forEach((value) => {
      const cell = document.createElement(rowIndex === 0 ? "th" : "td");
      cell.textContent = value;
      row.appendChild(cell);
    });
  });
}

function setCsvStatus(isValid, message) {
  csvStatus.textContent = message;
  csvStatus.classList.toggle("is-invalid", !isValid);
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
    const response = await fetch(csvUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputCsv.value,
        actions: selectedActions(),
        nullReplacement: nullReplacement.value,
      }),
    });
    const data = await response.json();

    if (requestId !== latestRequestId) {
      return;
    }

    if (!response.ok) {
      throw new Error();
    }

    if (data.valid) {
      outputCsv.textContent = data.output;
      setCsvStatus(true, "Ready");
      updateCsvStats(data.statistics);
      renderPreview(data.preview);
    } else {
      outputCsv.textContent = data.error;
      setCsvStatus(false, data.error);
      updateCsvStats({});
      renderPreview([]);
    }
  } catch {
    if (requestId === latestRequestId) {
      outputCsv.textContent = "";
      setCsvStatus(false, "Unable to clean CSV");
      showToast("Unable to clean CSV");
      updateCsvStats({});
      renderPreview([]);
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

controls.forEach((control) =>
  control.addEventListener("change", scheduleRefresh),
);
nullReplacement.addEventListener("input", scheduleRefresh);
inputCsv.addEventListener("input", scheduleRefresh);
formatButton.addEventListener("click", refresh);

document.querySelector("#resetOptions").addEventListener("click", () => {
  applyDefaultActions();
  nullReplacement.value = "";
  refresh();
});

document.querySelector("#clearAll").addEventListener("click", () => {
  inputCsv.value = "";
  refresh();
  inputCsv.focus();
});

document.querySelector("#copyOutput").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(outputCsv.textContent);
    showToast("Copied");
  } catch {
    showToast("Copy unavailable");
  }
});

document.querySelector("#downloadOutput").addEventListener("click", () => {
  const file = new Blob([outputCsv.textContent], { type: "text/csv" });
  const link = document.createElement("a");
  const today = formatDateForFilename(new Date());
  link.href = URL.createObjectURL(file);
  link.download = `CSVCleanr-output-${today}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
  showToast("Exported");
});

inputCsv.value = initialCsv;
applyDefaultActions();
refresh();
