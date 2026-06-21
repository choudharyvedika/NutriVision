/* ==========================================================================
   Weight Tracker — Chart.js line chart + AJAX add/delete
   ========================================================================== */

(() => {
  let chart;

  function buildChart(logs) {
    const ctx = document.getElementById("weightChart").getContext("2d");
    const labels = logs.map((l) => new Date(l.date + "T00:00:00").toLocaleDateString(undefined, { month: "short", day: "numeric" }));
    const weights = logs.map((l) => l.weight);

    const datasets = [
      {
        label: "Weight (kg)",
        data: weights,
        borderColor: "#4CAF50",
        backgroundColor: "rgba(76, 175, 80, 0.12)",
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointBackgroundColor: "#2E7D32",
        pointHoverRadius: 6,
      },
    ];

    if (GOAL_WEIGHT) {
      datasets.push({
        label: "Goal",
        data: labels.map(() => GOAL_WEIGHT),
        borderColor: "#81C784",
        borderDash: [6, 4],
        pointRadius: 0,
        borderWidth: 1.5,
        fill: false,
      });
    }

    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: "line",
      data: { labels, datasets },
      options: {
        responsive: true,
        plugins: {
          legend: { display: !!GOAL_WEIGHT, position: "top", labels: { boxWidth: 12, font: { family: "Inter", size: 11 } } },
          tooltip: { backgroundColor: "#14241A", padding: 10, cornerRadius: 8 },
        },
        scales: {
          y: { grid: { color: "rgba(20,36,26,0.06)" }, ticks: { font: { family: "Inter", size: 11 } } },
          x: { grid: { display: false }, ticks: { font: { family: "Inter", size: 11 } } },
        },
      },
    });
  }

  function rebuildHistoryList(logs) {
    const list = document.getElementById("weightHistoryList");
    const reversed = [...logs].reverse();
    if (reversed.length === 0) {
      list.innerHTML = "";
      if (!document.getElementById("weightEmptyState")) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.id = "weightEmptyState";
        empty.innerHTML = `<div class="empty-icon"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="4"/></svg></div><h4>No entries yet</h4><p>Log your weight to start building your progression chart.</p>`;
        list.parentElement.appendChild(empty);
      }
      return;
    }
    document.getElementById("weightEmptyState")?.remove();
    list.innerHTML = reversed
      .map(
        (l) => `
      <div class="list-row" data-log-id="${l.id}">
        <div class="list-row-main">
          <div class="list-row-icon">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 16c0-3 2-5 4-5s4 2 4 5"/><circle cx="12" cy="8" r="1.3"/></svg>
          </div>
          <div>
            <div class="list-row-title">${l.weight} kg</div>
            <div class="list-row-sub">${new Date(l.date + "T00:00:00").toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</div>
          </div>
        </div>
        <button class="row-delete" data-delete-weight-log="${l.id}" aria-label="Remove">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
        </button>
      </div>`
      )
      .join("");
    list.querySelectorAll("[data-delete-weight-log]").forEach(attachDelete);
  }

  function updateStatCards(logs) {
    const cards = document.querySelectorAll(".stat-grid .stat-card .stat-value");
    if (logs.length === 0) return;
    const starting = logs[0].weight;
    const current = logs[logs.length - 1].weight;
    const change = Math.round((current - starting) * 10) / 10;

    cards[0].innerHTML = `${starting}<small> kg</small>`;
    cards[1].innerHTML = `${current}<small> kg</small>`;
    const trendEl = document.querySelector(".stat-trend");
    if (trendEl) {
      const icon =
        change < 0
          ? '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 17-8.5-8.5-5 5L2 7"/><path d="M16 17h6v-6"/></svg>'
          : '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m2 7 8.5 8.5 5-5L22 17"/><path d="M16 7h6v6"/></svg>';
      trendEl.innerHTML = `${icon} ${change} kg`;
    }
  }

  function refresh(logs) {
    buildChart(logs);
    rebuildHistoryList(logs);
    updateStatCards(logs);
  }

  document.getElementById("weightForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const weight = parseFloat(document.getElementById("weightInput").value);
    const date = document.getElementById("weightDate").value;
    if (!weight || weight < 30) {
      showToast("Please enter a valid weight.", "error");
      return;
    }
    try {
      const data = await api("/api/weight/log", { method: "POST", body: { weight, date } });
      refresh(data.logs);
      document.getElementById("weightInput").value = "";
      showToast("Weight logged.", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  });

  function attachDelete(btn) {
    btn.addEventListener("click", async () => {
      const logId = btn.getAttribute("data-delete-weight-log");
      try {
        const data = await api(`/api/weight/log/${logId}`, { method: "DELETE" });
        refresh(data.logs);
        showToast("Entry removed.", "info");
      } catch (err) {
        showToast(err.message, "error");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    buildChart(CHART_LOGS);
    document.querySelectorAll("[data-delete-weight-log]").forEach(attachDelete);
  });
})();
