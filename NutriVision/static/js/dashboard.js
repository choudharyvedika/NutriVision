/* ==========================================================================
   Dashboard — 7-day calorie trend chart
   `trendLabels`, `trendCalories`, `calorieGoalLine` are injected inline
   by dashboard.html before this script runs.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("trendChart");
  if (!canvas || typeof Chart === "undefined") return;

  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels: trendLabels,
      datasets: [
        {
          label: "Calories",
          data: trendCalories,
          backgroundColor: trendCalories.map((v) =>
            v > calorieGoalLine ? "rgba(229, 72, 77, 0.75)" : "rgba(76, 175, 80, 0.8)"
          ),
          borderRadius: 6,
          maxBarThickness: 28,
        },
        {
          label: "Goal",
          data: trendLabels.map(() => calorieGoalLine),
          type: "line",
          borderColor: "#2E7D32",
          borderDash: [5, 4],
          pointRadius: 0,
          borderWidth: 1.5,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#14241A",
          padding: 10,
          cornerRadius: 8,
          titleFont: { family: "Inter" },
          bodyFont: { family: "Inter" },
        },
      },
      scales: {
        y: { beginAtZero: true, grid: { color: "rgba(20,36,26,0.06)" }, ticks: { font: { family: "Inter", size: 11 } } },
        x: { grid: { display: false }, ticks: { font: { family: "Inter", size: 11 } } },
      },
    },
  });
});
