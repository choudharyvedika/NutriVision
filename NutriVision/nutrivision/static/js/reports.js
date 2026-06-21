/* ==========================================================================
   Reports & Analytics — daily / weekly / monthly tabs
   ========================================================================== */

(() => {
  const ICONS = {
    flame: '<path d="M12 2.5s5.5 4.5 5.5 10a5.5 5.5 0 1 1-11 0c0-1.6.8-2.7 1.5-3.6.2 1.2 1 1.9 1.8 1.9 1.2 0 1.2-1.4 1-2.4-.3-1.6.2-3.4 1.2-5.9Z"/>',
    activity: '<path d="M22 12h-4l-3 8-6-16-3 8H2"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    scale: '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 16c0-3 2-5 4-5s4 2 4 5"/><circle cx="12" cy="8" r="1.3"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="3"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 5-5"/>',
  };
  function svg(name, color, bg) {
    return `<div class="stat-icon" style="background:${bg};color:${color};"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg></div>`;
  }

  let activeTab = "daily";
  let dailyDate = new Date(TODAY_ISO + "T00:00:00");
  let weeklyAnchor = new Date(TODAY_ISO + "T00:00:00");
  let monthlyDate = new Date(TODAY_ISO + "T00:00:00");

  let reportChart, macroChart;

  const fmt = (d) => d.toISOString().slice(0, 10);
  const fmtShort = (d) => d.toLocaleDateString(undefined, { month: "short", day: "numeric" });

  function statCard(label, value, unit, iconName, color, bg) {
    return `
      <div class="card stat-card hoverable">
        ${svg(iconName, color, bg)}
        <span class="stat-label">${label}</span>
        <div class="stat-value">${value}<small> ${unit}</small></div>
      </div>`;
  }

  // ---------------- Tab + nav wiring ----------------
  document.querySelectorAll(".pill-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".pill-tab").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeTab = btn.getAttribute("data-tab");
      load();
    });
  });

  document.getElementById("periodPrev").addEventListener("click", () => navigate(-1));
  document.getElementById("periodNext").addEventListener("click", () => navigate(1));
  document.getElementById("periodToday").addEventListener("click", () => {
    dailyDate = new Date(TODAY_ISO + "T00:00:00");
    weeklyAnchor = new Date(TODAY_ISO + "T00:00:00");
    monthlyDate = new Date(TODAY_ISO + "T00:00:00");
    load();
  });

  function navigate(dir) {
    if (activeTab === "daily") {
      dailyDate.setDate(dailyDate.getDate() + dir);
    } else if (activeTab === "weekly") {
      weeklyAnchor.setDate(weeklyAnchor.getDate() + dir * 7);
    } else {
      monthlyDate.setMonth(monthlyDate.getMonth() + dir);
    }
    load();
  }

  // ---------------- Data loading ----------------
  async function load() {
    if (activeTab === "daily") {
      const data = await api(`/api/reports/daily?date=${fmt(dailyDate)}`);
      renderDaily(data);
    } else if (activeTab === "weekly") {
      const data = await api(`/api/reports/weekly?start=${fmt(weeklyAnchor)}`);
      renderWeekly(data);
    } else {
      const data = await api(`/api/reports/monthly?year=${monthlyDate.getFullYear()}&month=${monthlyDate.getMonth() + 1}`);
      renderMonthly(data);
    }
  }

  // ---------------- Renderers ----------------
  function renderDaily(d) {
    const isToday = d.date === TODAY_ISO;
    document.getElementById("periodLabel").textContent = isToday ? "Today" : fmtShort(new Date(d.date + "T00:00:00"));

    document.getElementById("metricGrid").innerHTML = [
      statCard("Calories Consumed", Math.round(d.calories_consumed), "kcal", "flame", "#E65100", "#FFF3E0"),
      statCard("Calories Burned", Math.round(d.calories_burned), "kcal", "activity", "#C62828", "#FFEBEE"),
      statCard("Protein", d.protein, "g", "target", "#4527A0", "#EDE7F6"),
      statCard("Carbs", d.carbs, "g", "target", "#E65100", "#FFF3E0"),
      statCard("Fat", d.fat, "g", "target", "#AD1457", "#FCE4EC"),
    ].join("");

    document.getElementById("chartTitle").textContent = "Calories — " + (isToday ? "Today" : fmtShort(new Date(d.date + "T00:00:00")));
    document.getElementById("chartSubtitle").textContent = `Goal: ${d.calorie_goal} kcal`;

    drawBarChart(["Consumed", "Goal", "Burned"], [d.calories_consumed, d.calorie_goal, d.calories_burned], ["#4CAF50", "#81C784", "#E5484D"]);
    drawMacroDoughnut(d.protein, d.carbs, d.fat);
  }

  function renderWeekly(d) {
    document.getElementById("periodLabel").textContent = `${fmtShort(new Date(d.start + "T00:00:00"))} – ${fmtShort(new Date(d.end + "T00:00:00"))}`;

    document.getElementById("metricGrid").innerHTML = [
      statCard("Avg Calories", Math.round(d.avg_calories), "kcal/day", "flame", "#E65100", "#FFF3E0"),
      statCard("Avg Protein", d.avg_protein, "g/day", "target", "#4527A0", "#EDE7F6"),
      statCard("Avg Carbs", d.avg_carbs, "g/day", "target", "#E65100", "#FFF3E0"),
      statCard("Avg Fat", d.avg_fat, "g/day", "target", "#AD1457", "#FCE4EC"),
      statCard("Days Logged", d.days_logged, "/ 7", "calendar", "#1565C0", "#E3F2FD"),
      statCard("Weight Change", d.weight_change !== null ? d.weight_change : "—", "kg", "scale", "#2E7D32", "#EAF6EA"),
    ].join("");

    document.getElementById("chartTitle").textContent = "Daily Calories — This Week";
    document.getElementById("chartSubtitle").textContent = `Goal: ${d.calorie_goal} kcal/day`;

    const labels = d.days.map((day) => new Date(day.date + "T00:00:00").toLocaleDateString(undefined, { weekday: "short" }));
    const values = d.days.map((day) => day.calories_consumed);
    const colors = d.days.map((day) => (!day.logged ? "rgba(20,36,26,0.08)" : day.calories_consumed > d.calorie_goal ? "rgba(229,72,77,0.75)" : "rgba(76,175,80,0.8)"));
    drawTrendChart(labels, values, colors, d.calorie_goal);
    drawMacroDoughnut(d.avg_protein, d.avg_carbs, d.avg_fat);
  }

  function renderMonthly(d) {
    const monthName = new Date(d.start + "T00:00:00").toLocaleDateString(undefined, { month: "long", year: "numeric" });
    document.getElementById("periodLabel").textContent = monthName;

    document.getElementById("metricGrid").innerHTML = [
      statCard("Avg Calories", Math.round(d.avg_calories), "kcal/day", "flame", "#E65100", "#FFF3E0"),
      statCard("Consistency", d.consistency_pct, "%", "calendar", "#1565C0", "#E3F2FD"),
      statCard("Goal Adherence", d.adherence_pct, "%", "check", "#2E7D32", "#EAF6EA"),
      statCard("Days Logged", `${d.days_logged}`, `/ ${d.total_days}`, "calendar", "#4527A0", "#EDE7F6"),
      statCard("Weight Change", d.weight_change !== null ? d.weight_change : "—", "kg", "scale", "#AD1457", "#FCE4EC"),
    ].join("");

    document.getElementById("chartTitle").textContent = "Daily Calories — " + monthName;
    document.getElementById("chartSubtitle").textContent = `Goal: ${d.calorie_goal} kcal/day · ${d.consistency_pct}% consistency`;

    const labels = d.days.map((day) => new Date(day.date + "T00:00:00").getDate().toString());
    const values = d.days.map((day) => day.calories_consumed);
    const colors = d.days.map((day) => (!day.logged ? "rgba(20,36,26,0.08)" : day.calories_consumed > d.calorie_goal ? "rgba(229,72,77,0.75)" : "rgba(76,175,80,0.8)"));
    drawTrendChart(labels, values, colors, d.calorie_goal);
    drawMacroDoughnut(d.avg_protein, d.avg_carbs, d.avg_fat);
  }

  // ---------------- Chart helpers ----------------
  function drawBarChart(labels, values, colors) {
    const ctx = document.getElementById("reportChart").getContext("2d");
    if (reportChart) reportChart.destroy();
    reportChart = new Chart(ctx, {
      type: "bar",
      data: { labels, datasets: [{ data: values, backgroundColor: colors, borderRadius: 8, maxBarThickness: 70 }] },
      options: {
        responsive: true,
        plugins: { legend: { display: false }, tooltip: { backgroundColor: "#14241A", padding: 10, cornerRadius: 8 } },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(20,36,26,0.06)" } },
          x: { grid: { display: false } },
        },
      },
    });
  }

  function drawTrendChart(labels, values, colors, goal) {
    const ctx = document.getElementById("reportChart").getContext("2d");
    if (reportChart) reportChart.destroy();
    reportChart = new Chart(ctx, {
      data: {
        labels,
        datasets: [
          { type: "bar", label: "Calories", data: values, backgroundColor: colors, borderRadius: 5, maxBarThickness: 26 },
          { type: "line", label: "Goal", data: labels.map(() => goal), borderColor: "#2E7D32", borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5 },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false }, tooltip: { backgroundColor: "#14241A", padding: 10, cornerRadius: 8 } },
        scales: {
          y: { beginAtZero: true, grid: { color: "rgba(20,36,26,0.06)" } },
          x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      },
    });
  }

  function drawMacroDoughnut(protein, carbs, fat) {
    const ctx = document.getElementById("macroDoughnut").getContext("2d");
    if (macroChart) macroChart.destroy();

    const pCal = protein * 4, cCal = carbs * 4, fCal = fat * 9;
    const total = pCal + cCal + fCal || 1;

    macroChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Protein", "Carbs", "Fat"],
        datasets: [{ data: [pCal, cCal, fCal], backgroundColor: ["#6C5CE7", "#FF9F43", "#FF6B81"], borderWidth: 0 }],
      },
      options: {
        responsive: true,
        cutout: "68%",
        plugins: { legend: { display: false } },
      },
    });

    document.getElementById("macroChipRow").innerHTML = `
      <div class="macro-chip protein"><div class="mval">${Math.round((pCal / total) * 100)}%</div><div class="mlbl">Protein</div></div>
      <div class="macro-chip carbs"><div class="mval">${Math.round((cCal / total) * 100)}%</div><div class="mlbl">Carbs</div></div>
      <div class="macro-chip fat"><div class="mval">${Math.round((fCal / total) * 100)}%</div><div class="mlbl">Fat</div></div>`;
  }

  // ---------------- Init with server-rendered daily data (no extra fetch on load) ----------------
  document.addEventListener("DOMContentLoaded", () => {
    INITIAL_DAILY.calorie_goal = CALORIE_GOAL;
    renderDaily(INITIAL_DAILY);
  });
})();
