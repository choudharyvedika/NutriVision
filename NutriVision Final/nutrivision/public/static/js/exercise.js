/* ==========================================================================
   Exercise Log — live calorie preview (mirrors server-side MET formula)
   and AJAX add/delete.
   ========================================================================== */

(() => {
  const MET = {
    walking: 3.8,
    running: 9.8,
    cycling: 7.5,
    gym_workout: 6.0,
    yoga: 2.5,
  };

  const LABELS = {
    walking: "Walking",
    running: "Running",
    cycling: "Cycling",
    gym_workout: "Gym Workout",
    yoga: "Yoga",
  };

  const ICONS = {
    walking: '<path d="M5 16c1.5 0 2.5-1 2.5-2.5S6 9 6 7a2 2 0 0 1 4 0c0 2-1 3-1 6.5S10.5 19 8 19a3 3 0 0 1-3-3Z"/><path d="M14.5 21c1.5 0 2.5-1 2.5-2.5s-1.5-4.5-1.5-6.5a2 2 0 0 0-4 0c0 2 1 3 1 6.5S17 24 14.5 24"/>',
    running: '<path d="M22 12h-4l-3 8-6-16-3 8H2"/>',
    cycling: '<circle cx="6" cy="17" r="3.5"/><circle cx="18" cy="17" r="3.5"/><path d="M6 17 10 8h5l3 9"/><path d="M10 8 8.5 5h2.5"/><path d="m12 17 2-5"/>',
    gym_workout: '<path d="M4 9v6"/><path d="M2 10v4"/><path d="M20 9v6"/><path d="M22 10v4"/><path d="M7 7v10"/><path d="M17 7v10"/><path d="M7 12h10"/>',
    yoga: '<path d="M5 21c8 0 14-6 14-14V4h-3C8 4 3 9 3 16v5Z"/><path d="M5 21c4-4 7-7 11-11"/>',
  };

  function svgIcon(type) {
    return `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${ICONS[type] || ""}</svg>`;
  }

  const durationInput = document.getElementById("exerciseDuration");
  const estimateEl = document.getElementById("estimatedCalories");
  const addBtn = document.getElementById("addExerciseBtn");

  function currentType() {
    const checked = document.querySelector('input[name="exerciseType"]:checked');
    return checked ? checked.value : "walking";
  }

  function estimate() {
    const type = currentType();
    const duration = parseFloat(durationInput.value) || 0;
    const met = MET[type] || 5;
    const calories = met * USER_WEIGHT_KG * (duration / 60);
    estimateEl.textContent = `${Math.round(calories)} kcal`;
    return Math.round(calories);
  }

  document.querySelectorAll('input[name="exerciseType"]').forEach((el) => el.addEventListener("change", estimate));
  durationInput?.addEventListener("input", estimate);
  estimate();

  addBtn?.addEventListener("click", async () => {
    const type = currentType();
    const duration = parseInt(durationInput.value, 10);
    if (!duration || duration <= 0) {
      showToast("Please enter a valid duration.", "error");
      return;
    }

    addBtn.disabled = true;
    try {
      const data = await api("/api/exercise/log", {
        method: "POST",
        body: { exercise_type: type, duration, date: SELECTED_DATE },
      });
      addRow(data.entry);
      document.getElementById("totalBurnedLabel").textContent = Math.round(data.total_burned);
      showToast(`Logged ${LABELS[type]} — ${Math.round(data.entry.calories_burned)} kcal burned.`, "success");
    } catch (e) {
      showToast(e.message, "error");
    } finally {
      addBtn.disabled = false;
    }
  });

  function addRow(entry) {
    document.getElementById("exerciseEmptyState")?.remove();
    const list = document.getElementById("exerciseList");
    const row = document.createElement("div");
    row.className = "list-row";
    row.setAttribute("data-log-id", entry.id);
    row.innerHTML = `
      <div class="list-row-main">
        <div class="list-row-icon">${svgIcon(entry.exercise_type)}</div>
        <div>
          <div class="list-row-title">${entry.exercise_label}</div>
          <div class="list-row-sub">${entry.duration} minutes</div>
        </div>
      </div>
      <div class="list-row-meta">
        <span class="list-row-cal">${Math.round(entry.calories_burned)} kcal</span>
        <button class="row-delete" data-delete-exercise-log="${entry.id}" aria-label="Remove">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
        </button>
      </div>`;
    list.appendChild(row);
    attachDelete(row.querySelector("[data-delete-exercise-log]"));
  }

  function attachDelete(btn) {
    btn.addEventListener("click", async () => {
      const logId = btn.getAttribute("data-delete-exercise-log");
      const row = btn.closest(".list-row");
      try {
        const data = await api(`/api/exercise/log/${logId}`, { method: "DELETE" });
        row.remove();
        document.getElementById("totalBurnedLabel").textContent = Math.round(data.total_burned);
        if (!document.querySelector("#exerciseList .list-row")) {
          const list = document.getElementById("exerciseList");
          const empty = document.createElement("div");
          empty.className = "empty-state";
          empty.id = "exerciseEmptyState";
          empty.innerHTML = `<div class="empty-icon">${svgIcon("running")}</div><h4>No workouts logged yet</h4><p>Log a walk, run, ride or gym session to see it added to your calorie balance.</p>`;
          list.parentElement.appendChild(empty);
        }
        showToast("Workout removed.", "info");
      } catch (e) {
        showToast(e.message, "error");
      }
    });
  }

  document.querySelectorAll("[data-delete-exercise-log]").forEach(attachDelete);
})();
