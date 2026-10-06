/**
 * Model Information & Explainability Dashboard script
 */

document.addEventListener("DOMContentLoaded", async () => {
  try {
    // 1. Fetch Model Metrics
    const res = await fetch("/api/model-info");
    if (!res.ok) throw new Error("Could not load model info.");
    const metrics = await res.json();

    document.getElementById("m-name").textContent = metrics.model_name;
    document.getElementById("m-train").textContent = metrics.training_samples;
    document.getElementById("m-test").textContent = metrics.testing_samples;
    document.getElementById("m-acc").textContent = `${(metrics.accuracy * 100).toFixed(1)}%`;
    document.getElementById("m-prec").textContent = `${(metrics.precision * 100).toFixed(1)}%`;
    document.getElementById("m-rec").textContent = `${(metrics.recall * 100).toFixed(1)}%`;
    document.getElementById("m-f1").textContent = `${(metrics.f1_score * 100).toFixed(1)}%`;
    document.getElementById("m-selection-rationale").textContent = metrics.why_selected;

    // Render Confusion Matrix
    renderConfusionMatrix(metrics.confusion_matrix, metrics.classes);

    // Render Top Features per Class
    renderTopFeatures(metrics.top_features);

    // 2. Fetch Comparison Benchmarks
    const compRes = await fetch("/api/model-comparison");
    if (compRes.ok) {
      const compData = await compRes.json();
      renderComparisonTable(compData.models);
    }
  } catch (err) {
    console.error("Model info loading error:", err);
  }
});

function renderConfusionMatrix(matrix, classes) {
  const container = document.getElementById("cm-container");
  if (!container || !matrix) return;

  let html = `<table class="data-table" style="text-align: center;">
    <thead>
      <tr>
        <th style="text-align: left;">Actual \\ Predicted</th>`;
  classes.forEach(c => {
    html += `<th style="text-align: center;">${c}</th>`;
  });
  html += `</tr></thead><tbody>`;

  matrix.forEach((row, i) => {
    html += `<tr><td style="font-weight: 700; text-align: left;">${classes[i]}</td>`;
    row.forEach((val, j) => {
      const isDiagonal = i === j;
      const bg = isDiagonal ? "rgba(16, 185, 129, 0.2)" : (val > 0 ? "rgba(239, 68, 68, 0.2)" : "transparent");
      const color = isDiagonal ? "#34d399" : (val > 0 ? "#f87171" : "#9ca3af");
      html += `<td style="background: ${bg}; color: ${color}; font-weight: 600;">${val}</td>`;
    });
    html += `</tr>`;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;
}

function renderTopFeatures(featuresByClass) {
  const container = document.getElementById("features-container");
  if (!container || !featuresByClass) return;

  let html = `<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem;">`;
  for (const [cls, items] of Object.entries(featuresByClass)) {
    let badgeColor = "var(--low)";
    if (cls === "Critical") badgeColor = "var(--critical)";
    else if (cls === "High") badgeColor = "var(--high)";
    else if (cls === "Medium") badgeColor = "var(--medium)";

    html += `
      <div style="background: var(--bg-card); padding: 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
        <h4 style="color: ${badgeColor}; font-size: 0.95rem; margin-bottom: 0.75rem;">${cls} Key Weights</h4>
        <div style="display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.82rem;">
    `;
    items.slice(0, 6).forEach(f => {
      html += `
        <div style="display: flex; justify-content: space-between; color: var(--text-muted);">
          <span>"${f.feature}"</span>
          <span style="font-weight: 600; color: #fff;">+${f.weight}</span>
        </div>
      `;
    });
    html += `</div></div>`;
  }
  html += `</div>`;
  container.innerHTML = html;
}

function renderComparisonTable(models) {
  const container = document.getElementById("comparison-table-container");
  if (!container || !models) return;

  let html = `<table class="data-table">
    <thead>
      <tr>
        <th>Algorithm</th>
        <th>Accuracy</th>
        <th>Precision</th>
        <th>Recall</th>
        <th>F1-Score</th>
        <th>Training Time (ms)</th>
      </tr>
    </thead>
    <tbody>`;

  models.forEach(m => {
    const isBest = m.model_name.includes("Logistic");
    const highlightStyle = isBest ? "background: rgba(99, 102, 241, 0.1); font-weight: 600;" : "";
    html += `
      <tr style="${highlightStyle}">
        <td>${m.model_name} ${isBest ? '<span class="brand-badge" style="background: rgba(99,102,241,0.3);">Selected</span>' : ''}</td>
        <td>${(m.accuracy * 100).toFixed(1)}%</td>
        <td>${(m.precision * 100).toFixed(1)}%</td>
        <td>${(m.recall * 100).toFixed(1)}%</td>
        <td>${(m.f1_score * 100).toFixed(1)}%</td>
        <td>${m.training_time_ms} ms</td>
      </tr>
    `;
  });
  html += `</tbody></table>`;
  container.innerHTML = html;
}

