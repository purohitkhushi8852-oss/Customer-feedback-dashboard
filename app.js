const state = {
  rows: [],
  filteredRows: [],
  columns: [],
  selectedRegions: [],
  ratingRange: [1, 5],
  dateRange: { start: null, end: null },
  selectedSentiments: ["Positive", "Neutral", "Negative"],
  sourceLabel: "sample data",
};

const chartInstances = {};
const sentimentColors = {
  Positive: "#16a34a",
  Neutral: "#64748b",
  Negative: "#dc2626",
};

function normalizeHeader(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
}

function detectColumn(columns, candidates) {
  return candidates.find((candidate) => columns.includes(candidate)) || null;
}

function parseDateValue(value) {
  if (!value) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function deriveSentiment(text) {
  if (typeof text !== "string") return "Neutral";
  const normalized = text.toLowerCase();
  const positiveWords = ["love", "great", "excellent", "satisfied", "amazing", "helpful", "kind", "fast", "good", "happy"];
  const negativeWords = ["disappointed", "terrible", "rude", "unhelpful", "late", "damaged", "regret", "waste", "broke", "bad"];
  const positiveScore = positiveWords.reduce((score, word) => score + Number(normalized.includes(word)), 0);
  const negativeScore = negativeWords.reduce((score, word) => score + Number(normalized.includes(word)), 0);
  if (positiveScore > negativeScore) return "Positive";
  if (negativeScore > positiveScore) return "Negative";
  return "Neutral";
}

function hydrateRows(rawRows) {
  const columns = rawRows.length ? Object.keys(rawRows[0]) : [];
  const normalizedColumns = columns.map(normalizeHeader);
  const mapped = rawRows.map((row) => {
    const mappedRow = {};
    columns.forEach((column, index) => {
      mappedRow[normalizedColumns[index]] = row[column];
    });
    return mappedRow;
  });

  const dateColumn = detectColumn(normalizedColumns, ["date", "created_at", "review_date", "timestamp"]);
  const ratingColumn = detectColumn(normalizedColumns, ["rating", "score", "stars"]);
  const regionColumn = detectColumn(normalizedColumns, ["region", "location", "state", "city"]);
  const textColumn = detectColumn(normalizedColumns, ["feedback_text", "review", "review_text", "comment", "feedback", "text"]);

  const rows = mapped.map((row) => {
    const rating = Number(row[ratingColumn] ?? 0);
    const parsedDate = parseDateValue(row[dateColumn]);
    return {
      ...row,
      date: parsedDate,
      month: parsedDate ? parsedDate.toISOString().slice(0, 7) : "",
      rating: Number.isFinite(rating) ? rating : 0,
      region: row[regionColumn] || "Unknown",
      feedback_text: row[textColumn] || "",
      sentiment: deriveSentiment(row[textColumn]),
    };
  }).filter((row) => row.date);

  return { rows, columns: normalizedColumns, dateColumn, ratingColumn, regionColumn, textColumn };
}

function setStatus(message) {
  document.getElementById("statusText").textContent = message;
}

function populateFilters(rows) {
  const regions = [...new Set(rows.map((row) => row.region).filter(Boolean))].sort();
  const regionFilter = document.getElementById("regionFilter");
  regionFilter.innerHTML = regions.map((region) => `<option value="${region}" selected>${region}</option>`).join("");
  state.selectedRegions = regions;

  const sentimentFilters = document.getElementById("sentimentFilters");
  sentimentFilters.innerHTML = ["Positive", "Neutral", "Negative"].map((sentiment) => `
    <label>
      <input type="checkbox" value="${sentiment}" checked />
      <span>${sentiment}</span>
    </label>
  `).join("");

  const minRating = Math.min(...rows.map((row) => row.rating), 1);
  const maxRating = Math.max(...rows.map((row) => row.rating), 5);
  const ratingMin = document.getElementById("ratingMin");
  const ratingMax = document.getElementById("ratingMax");
  ratingMin.min = String(minRating);
  ratingMax.min = String(minRating);
  ratingMin.max = String(maxRating);
  ratingMax.max = String(maxRating);
  ratingMin.value = String(minRating);
  ratingMax.value = String(maxRating);
  state.ratingRange = [minRating, maxRating];
  document.getElementById("ratingMinLabel").textContent = String(minRating);
  document.getElementById("ratingMaxLabel").textContent = String(maxRating);

  const dates = rows.map((row) => row.date).filter(Boolean);
  const startDate = dates.length ? dates[0].toISOString().slice(0, 10) : "";
  const endDate = dates.length ? dates[dates.length - 1].toISOString().slice(0, 10) : "";
  document.getElementById("startDate").value = startDate;
  document.getElementById("endDate").value = endDate;
  state.dateRange = { start: startDate || null, end: endDate || null };
}

function getFilteredRows() {
  const regionFilter = document.getElementById("regionFilter");
  const selectedRegions = Array.from(regionFilter.selectedOptions).map((option) => option.value);

  const ratingMin = Number(document.getElementById("ratingMin").value);
  const ratingMax = Number(document.getElementById("ratingMax").value);
  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;
  const selectedSentiments = Array.from(document.querySelectorAll("#sentimentFilters input:checked"))
    .map((input) => input.value);

  const filtered = state.rows.filter((row) => {
    const inRegion = selectedRegions.length === 0 || selectedRegions.includes(row.region);
    const inRating = row.rating >= ratingMin && row.rating <= ratingMax;
    const inSentiment = selectedSentiments.includes(row.sentiment);
    const inStart = !startDate || row.date >= new Date(`${startDate}T00:00:00`);
    const inEnd = !endDate || row.date <= new Date(`${endDate}T23:59:59`);
    return inRegion && inRating && inSentiment && inStart && inEnd;
  });

  return filtered;
}

function updateMetrics(rows) {
  const metricsGrid = document.getElementById("metricsGrid");
  const avgRating = rows.length ? (rows.reduce((sum, row) => sum + row.rating, 0) / rows.length).toFixed(2) : "0.00";
  const positivePct = rows.length ? ((rows.filter((row) => row.sentiment === "Positive").length / rows.length) * 100).toFixed(1) : "0.0";
  const negativePct = rows.length ? ((rows.filter((row) => row.sentiment === "Negative").length / rows.length) * 100).toFixed(1) : "0.0";

  metricsGrid.innerHTML = `
    <article class="metric-card">
      <div class="label">Total feedback</div>
      <div class="value">${rows.length}</div>
    </article>
    <article class="metric-card">
      <div class="label">Average rating</div>
      <div class="value">${avgRating} ★</div>
    </article>
    <article class="metric-card">
      <div class="label">Positive sentiment</div>
      <div class="value">${positivePct}%</div>
    </article>
    <article class="metric-card">
      <div class="label">Negative sentiment</div>
      <div class="value">${negativePct}%</div>
    </article>
  `;
}

function buildChartConfig(type, data, options = {}) {
  return { type, data, options: { responsive: true, maintainAspectRatio: false, ...options } };
}

function renderCharts(rows) {
  const ratingCounts = [1, 2, 3, 4, 5].map((value) => rows.filter((row) => row.rating === value).length);
  const ratingLabels = ["1", "2", "3", "4", "5"];
  const regionMap = new Map();
  rows.forEach((row) => regionMap.set(row.region, (regionMap.get(row.region) || 0) + 1));
  const regionLabels = [...regionMap.keys()];
  const regionValues = regionLabels.map((label) => regionMap.get(label));
  const sentimentCounts = ["Positive", "Neutral", "Negative"].map((label) => rows.filter((row) => row.sentiment === label).length);
  const monthlyMap = new Map();
  rows.forEach((row) => {
    const key = row.month || "Unknown";
    if (!monthlyMap.has(key)) monthlyMap.set(key, { month: key, count: 0, rating: 0, polarity: 0 });
    const bucket = monthlyMap.get(key);
    bucket.count += 1;
    bucket.rating += row.rating;
    bucket.polarity += row.rating > 3 ? 1 : row.rating < 3 ? -1 : 0;
  });
  const monthlyEntries = [...monthlyMap.values()].sort((a, b) => a.month.localeCompare(b.month));
  const monthlyLabels = monthlyEntries.map((entry) => entry.month);
  const monthlyRatings = monthlyEntries.map((entry) => (entry.count ? (entry.rating / entry.count).toFixed(2) : 0));

  if (chartInstances.ratingChart) chartInstances.ratingChart.destroy();
  if (chartInstances.ratingPieChart) chartInstances.ratingPieChart.destroy();
  if (chartInstances.regionChart) chartInstances.regionChart.destroy();
  if (chartInstances.sentimentChart) chartInstances.sentimentChart.destroy();
  if (chartInstances.monthlyChart) chartInstances.monthlyChart.destroy();

  chartInstances.ratingChart = new Chart(document.getElementById("ratingChart"), buildChartConfig("bar", {
    labels: ratingLabels,
    datasets: [{ label: "Count", data: ratingCounts, backgroundColor: "#2563eb" }],
  }, { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }));

  chartInstances.ratingPieChart = new Chart(document.getElementById("ratingPieChart"), buildChartConfig("pie", {
    labels: ratingLabels,
    datasets: [{ data: ratingCounts, backgroundColor: ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"] }],
  }));

  chartInstances.regionChart = new Chart(document.getElementById("regionChart"), buildChartConfig("bar", {
    labels: regionLabels,
    datasets: [{ label: "Feedback count", data: regionValues, backgroundColor: "#0f766e" }],
  }, { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }));

  chartInstances.sentimentChart = new Chart(document.getElementById("sentimentChart"), buildChartConfig("doughnut", {
    labels: ["Positive", "Neutral", "Negative"],
    datasets: [{ data: sentimentCounts, backgroundColor: [sentimentColors.Positive, sentimentColors.Neutral, sentimentColors.Negative] }],
  }));

  chartInstances.monthlyChart = new Chart(document.getElementById("monthlyChart"), buildChartConfig("line", {
    labels: monthlyLabels,
    datasets: [{ label: "Average rating", data: monthlyRatings, borderColor: "#2563eb", backgroundColor: "rgba(37, 99, 235, 0.2)", tension: 0.25, fill: true }],
  }, { scales: { y: { beginAtZero: true, max: 5 } } }));
}

function renderTable(rows) {
  const tableHead = document.querySelector("#feedbackTable thead");
  const tableBody = document.querySelector("#feedbackTable tbody");
  const columns = ["date", "region", "rating", "sentiment", "feedback_text"];
  tableHead.innerHTML = `<tr>${columns.map((column) => `<th>${column}</th>`).join("")}</tr>`;
  tableBody.innerHTML = rows.slice(0, 50).map((row) => `<tr>${columns.map((column) => `<td>${column === "date" ? row.date.toLocaleDateString() : row[column] ?? ""}</td>`).join("")}</tr>`).join("");
}

function renderDashboard() {
  const rows = getFilteredRows();
  state.filteredRows = rows;
  updateMetrics(rows);
  renderCharts(rows);
  renderTable(rows);
}

function loadCsvText(csvText, sourceLabel) {
  const parsed = Papa.parse(csvText, { header: true, skipEmptyLines: true });
  const { rows, columns } = hydrateRows(parsed.data);
  state.rows = rows;
  state.columns = columns;
  state.sourceLabel = sourceLabel;
  setStatus(`Loaded ${rows.length} rows from ${sourceLabel}`);
  populateFilters(rows);
  renderDashboard();
}

function loadSampleData() {
  fetch("./data/sample_feedback.csv")
    .then((response) => response.text())
    .then((text) => loadCsvText(text, "sample_feedback.csv"))
    .catch((error) => {
      console.error(error);
      setStatus("Unable to load sample data");
    });
}

function attachEvents() {
  document.getElementById("csvFile").addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => loadCsvText(String(reader.result), file.name);
    reader.readAsText(file);
  });

  document.getElementById("regionFilter").addEventListener("change", renderDashboard);
  document.getElementById("ratingMin").addEventListener("input", () => {
    document.getElementById("ratingMinLabel").textContent = document.getElementById("ratingMin").value;
    if (Number(document.getElementById("ratingMin").value) > Number(document.getElementById("ratingMax").value)) {
      document.getElementById("ratingMax").value = document.getElementById("ratingMin").value;
      document.getElementById("ratingMaxLabel").textContent = document.getElementById("ratingMin").value;
    }
    renderDashboard();
  });
  document.getElementById("ratingMax").addEventListener("input", () => {
    document.getElementById("ratingMaxLabel").textContent = document.getElementById("ratingMax").value;
    if (Number(document.getElementById("ratingMax").value) < Number(document.getElementById("ratingMin").value)) {
      document.getElementById("ratingMin").value = document.getElementById("ratingMax").value;
      document.getElementById("ratingMinLabel").textContent = document.getElementById("ratingMax").value;
    }
    renderDashboard();
  });
  document.getElementById("startDate").addEventListener("change", renderDashboard);
  document.getElementById("endDate").addEventListener("change", renderDashboard);
  document.getElementById("sentimentFilters").addEventListener("change", renderDashboard);

  document.getElementById("downloadCsv").addEventListener("click", () => {
    const rows = state.filteredRows;
    const header = ["date", "region", "rating", "sentiment", "feedback_text"];
    const csvRows = [header.join(",")];
    rows.forEach((row) => {
      const values = header.map((column) => {
        const value = column === "date" ? row.date.toISOString().slice(0, 10) : row[column] ?? "";
        return `"${String(value).replace(/"/g, '""')}"`;
      });
      csvRows.push(values.join(","));
    });
    const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "filtered_feedback.csv";
    link.click();
    URL.revokeObjectURL(url);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  attachEvents();
  loadSampleData();
});
