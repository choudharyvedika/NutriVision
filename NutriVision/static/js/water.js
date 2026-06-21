/* ==========================================================================
   Water Tracker — quick add, custom amount, goal update, AJAX add/delete
   ========================================================================== */

(() => {
  const RING_CIRCUMFERENCE = 540.35;
  const ringProgress = document.getElementById("waterRingProgress");
  const totalLabel = document.getElementById("waterTotalLabel");
  const goalLabelEls = document.querySelectorAll("#goalLabel, .ring-label");

  function updateRing(total, goal) {
    const pct = Math.max(0, Math.min((total / goal) * 100, 100));
    const offset = RING_CIRCUMFERENCE * (1 - pct / 100);
    ringProgress.style.strokeDashoffset = offset;
    totalLabel.textContent = total;
    document.querySelector(".ring-label").textContent = `of ${goal} ml`;
  }

  async function addWater(amount) {
    try {
      const data = await api("/api/water/log", {
        method: "POST",
        body: { amount, date: SELECTED_DATE },
      });
      updateRing(data.total, data.goal);
      prependLogRow(data.entry);
      document.getElementById("waterEmptyState")?.remove();
      showToast(`Added ${amount}ml of water.`, "success");
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  document.querySelectorAll(".quick-add-btn").forEach((btn) => {
    btn.addEventListener("click", () => addWater(parseInt(btn.getAttribute("data-amount"), 10)));
  });

  document.getElementById("addCustomAmount")?.addEventListener("click", () => {
    const input = document.getElementById("customAmount");
    const amount = parseInt(input.value, 10);
    if (!amount || amount <= 0) {
      showToast("Please enter a valid amount.", "error");
      return;
    }
    addWater(amount);
    input.value = "";
  });

  document.getElementById("goalForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const goal = parseInt(document.getElementById("goalInput").value, 10);
    if (!goal || goal < 500) {
      showToast("Goal must be at least 500ml.", "error");
      return;
    }
    try {
      await api("/api/water/goal", { method: "POST", body: { goal } });
      WATER_GOAL = goal;
      document.getElementById("goalLabel").textContent = goal;
      const totalNow = parseInt(totalLabel.textContent, 10) || 0;
      updateRing(totalNow, goal);
      showToast("Water goal updated.", "success");
    } catch (e) {
      showToast(e.message, "error");
    }
  });

  function prependLogRow(entry) {
    const list = document.getElementById("waterList");
    const row = document.createElement("div");
    row.className = "list-row";
    row.setAttribute("data-log-id", entry.id);
    const time = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    row.innerHTML = `
      <div class="list-row-main">
        <div class="list-row-icon" style="background:#E3F2FD;color:var(--water);">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5s7 7.5 7 12.2a7 7 0 1 1-14 0c0-4.7 7-12.2 7-12.2Z"/></svg>
        </div>
        <div>
          <div class="list-row-title">${entry.amount} ml</div>
          <div class="list-row-sub">${time}</div>
        </div>
      </div>
      <button class="row-delete" data-delete-water-log="${entry.id}" aria-label="Remove">
        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
      </button>`;
    list.prepend(row);
    attachDelete(row.querySelector("[data-delete-water-log]"));
  }

  function attachDelete(btn) {
    btn.addEventListener("click", async () => {
      const logId = btn.getAttribute("data-delete-water-log");
      const row = btn.closest(".list-row");
      try {
        const data = await api(`/api/water/log/${logId}`, { method: "DELETE" });
        row.remove();
        updateRing(data.total, WATER_GOAL);
        if (!document.querySelector("#waterList .list-row")) {
          const list = document.getElementById("waterList");
          const empty = document.createElement("div");
          empty.className = "empty-state";
          empty.id = "waterEmptyState";
          empty.innerHTML = `<div class="empty-icon"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5s7 7.5 7 12.2a7 7 0 1 1-14 0c0-4.7 7-12.2 7-12.2Z"/></svg></div><h4>No water logged yet</h4><p>Use the quick-add buttons to start tracking your hydration.</p>`;
          list.parentElement.appendChild(empty);
        }
        showToast("Entry removed.", "info");
      } catch (e) {
        showToast(e.message, "error");
      }
    });
  }

  document.querySelectorAll("[data-delete-water-log]").forEach(attachDelete);
})();
