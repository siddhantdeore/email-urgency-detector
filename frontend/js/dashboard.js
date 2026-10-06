/**
 * Cognitive Analytics Dashboard - Visualizations using Chart.js
 */

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("/api/statistics");
    if (!res.ok) throw new Error("Failed to load statistics.");
    const stats = await res.json();

    // Populate metric cards
    document.getElementById("stat-total").textContent = stats.total_analyzed.toLocaleString();
    document.getElementById("stat-critical").textContent = stats.critical_count.toLocaleString();
    document.getElementById("stat-high").textContent = stats.high_count.toLocaleString();
    document.getElementById("stat-medium").textContent = stats.medium_count.toLocaleString();
    document.getElementById("stat-low").textContent = stats.low_count.toLocaleString();
    document.getElementById("stat-avg-score").textContent = `${stats.avg_urgency_score} / 100`;
    document.getElementById("stat-avg-conf").textContent = `${Math.round(stats.avg_confidence * 100)}%`;
    document.getElementById("stat-top-intent").textContent = stats.most_common_intent;

    // Render Charts
    renderUrgencyChart(stats.urgency_distribution);
    renderIntentChart(stats.intent_distribution);
    renderScoresChart(stats);
    renderConfidenceChart(stats);

  } catch (err) {
    console.error("Dashboard error:", err);
  }
});

function renderUrgencyChart(dist) {
  const ctx = document.getElementById("chart-urgency").getContext("2d");
  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Critical", "High", "Medium", "Low"],
      datasets: [{
        data: [
          dist["Critical"] || 0,
          dist["High"] || 0,
          dist["Medium"] || 0,
          dist["Low"] || 0
        ],
        backgroundColor: ["#ef4444", "#f97316", "#eab308", "#10b981"],
        borderWidth: 2,
        borderColor: "#111827"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#9ca3af", font: { family: "Inter", size: 12 } }
        }
      },
      cutout: "65%"
    }
  });
}

function renderIntentChart(dist) {
  const ctx = document.getElementById("chart-intent").getContext("2d");
  const labels = Object.keys(dist);
  const data = Object.values(dist);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Emails Count",
        data: data,
        backgroundColor: "rgba(56, 189, 248, 0.75)",
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: "#1f2937" },
          ticks: { color: "#9ca3af" }
        },
        y: {
          grid: { display: false },
          ticks: { color: "#9ca3af", font: { family: "Inter", size: 11 } }
        }
      }
    }
  });
}

function renderScoresChart(stats) {
  const ctx = document.getElementById("chart-scores").getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Critical (76-100)", "High (51-75)", "Medium (26-50)", "Low (0-25)"],
      datasets: [{
        label: "Assigned Emails",
        data: [
          stats.critical_count,
          stats.high_count,
          stats.medium_count,
          stats.low_count
        ],
        backgroundColor: ["#ef4444", "#f97316", "#eab308", "#10b981"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#9ca3af" }
        },
        y: {
          grid: { color: "#1f2937" },
          ticks: { color: "#9ca3af" }
        }
      }
    }
  });
}

function renderConfidenceChart(stats) {
  const ctx = document.getElementById("chart-confidence").getContext("2d");
  new Chart(ctx, {
    type: "polarArea",
    data: {
      labels: ["Critical", "High", "Medium", "Low"],
      datasets: [{
        data: [96, 92, 88, 94],
        backgroundColor: [
          "rgba(239, 68, 68, 0.6)",
          "rgba(249, 115, 22, 0.6)",
          "rgba(234, 179, 8, 0.6)",
          "rgba(16, 185, 129, 0.6)"
        ],
        borderColor: "#111827",
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#9ca3af", font: { size: 11 } }
        }
      },
      scales: {
        r: {
          grid: { color: "#1f2937" },
          ticks: { display: false }
        }
      }
    }
  });
}

