/* ==========================================================================
   Food Log — search, modal add flow, AJAX add/delete with live totals
   ========================================================================== */

(() => {
  const searchInput = document.getElementById("foodSearchInput");
  const resultsBox = document.getElementById("searchResults");
  const modal = document.getElementById("addFoodModal");
  const modalFoodName = document.getElementById("modalFoodName");
  const modalServingSize = document.getElementById("modalServingSize");
  const modalQuantity = document.getElementById("modalQuantity");
  const previewCal = document.getElementById("previewCal");
  const previewProtein = document.getElementById("previewProtein");
  const previewCarbs = document.getElementById("previewCarbs");
  const previewFat = document.getElementById("previewFat");
  const confirmBtn = document.getElementById("confirmAddFood");

  let selectedFood = null;
  let searchTimer = null;

  // ---------------- Live search ----------------
  searchInput?.addEventListener("input", () => {
    clearTimeout(searchTimer);
    const q = searchInput.value.trim();
    if (q.length < 1) {
      resultsBox.classList.remove("open");
      resultsBox.innerHTML = "";
      return;
    }
    searchTimer = setTimeout(() => runSearch(q), 220);
  });

  document.addEventListener("click", (e) => {
    if (!resultsBox.contains(e.target) && e.target !== searchInput) {
      resultsBox.classList.remove("open");
    }
  });

  async function runSearch(q) {
    try {
      const data = await api(`/api/food/search?q=${encodeURIComponent(q)}`);
      renderResults(data.foods);
    } catch (e) {
      showToast(e.message, "error");
    }
  }

  function renderResults(foods) {
    if (!foods.length) {
      resultsBox.innerHTML = `<div class="search-result-item" style="cursor:default;"><span class="search-result-meta">No foods found. Try a different search.</span></div>`;
      resultsBox.classList.add("open");
      return;
    }
    resultsBox.innerHTML = foods
      .map(
        (f) => `
        <div class="search-result-item" data-food='${JSON.stringify(f)}'>
          <div>
            <div class="search-result-name">${f.food_name}</div>
            <div class="search-result-meta">${f.serving_size} · P${f.protein}g C${f.carbs}g F${f.fat}g</div>
          </div>
          <div class="search-result-cal">${Math.round(f.calories)} kcal</div>
        </div>`
      )
      .join("");
    resultsBox.classList.add("open");

    resultsBox.querySelectorAll("[data-food]").forEach((el) => {
      el.addEventListener("click", () => {
        openModal(JSON.parse(el.getAttribute("data-food")));
        resultsBox.classList.remove("open");
        searchInput.value = "";
      });
    });
  }

  // ---------------- Modal ----------------
  function openModal(food) {
    selectedFood = food;
    modalFoodName.textContent = food.food_name;
    modalServingSize.textContent = `Per ${food.serving_size}`;
    modalQuantity.value = 1;
    document.querySelector('input[name="modalMealType"]').checked = true;
    updatePreview();
    modal.classList.add("open");
  }

  function closeModal() {
    modal.classList.remove("open");
    selectedFood = null;
  }

  document.getElementById("closeFoodModal")?.addEventListener("click", closeModal);
  document.getElementById("cancelAddFood")?.addEventListener("click", closeModal);
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });

  function updatePreview() {
    if (!selectedFood) return;
    const qty = parseFloat(modalQuantity.value) || 0;
    previewCal.textContent = Math.round(selectedFood.calories * qty);
    previewProtein.textContent = `${Math.round(selectedFood.protein * qty * 10) / 10}g`;
    previewCarbs.textContent = `${Math.round(selectedFood.carbs * qty * 10) / 10}g`;
    previewFat.textContent = `${Math.round(selectedFood.fat * qty * 10) / 10}g`;
  }
  modalQuantity?.addEventListener("input", updatePreview);

  confirmBtn?.addEventListener("click", async () => {
    if (!selectedFood) return;
    const qty = parseFloat(modalQuantity.value);
    if (!qty || qty <= 0) {
      showToast("Please enter a valid quantity.", "error");
      return;
    }
    const mealType = document.querySelector('input[name="modalMealType"]:checked').value;

    confirmBtn.disabled = true;
    try {
      const data = await api("/api/food/log", {
        method: "POST",
        body: { food_id: selectedFood.id, quantity: qty, meal_type: mealType, date: SELECTED_DATE },
      });
      addRowToDom(data.entry, mealType);
      updateTodayTotals(data.totals);
      showToast(`Added ${selectedFood.food_name} to ${mealType}.`, "success");
      closeModal();
    } catch (e) {
      showToast(e.message, "error");
    } finally {
      confirmBtn.disabled = false;
    }
  });

  // ---------------- DOM helpers ----------------
  function addRowToDom(entry, mealType) {
    const container = document.getElementById(`meal-${mealType}`);
    const card = container.closest(".meal-card");
    const emptyState = card.querySelector(".empty-meal");
    if (emptyState) emptyState.remove();

    const row = document.createElement("div");
    row.className = "list-row";
    row.setAttribute("data-log-id", entry.id);
    row.innerHTML = `
      <div class="list-row-main">
        <div class="list-row-icon">🍽️</div>
        <div>
          <div class="list-row-title">${entry.food_name}</div>
          <div class="list-row-sub">${entry.quantity}× ${entry.serving_size} · P${entry.protein}g C${entry.carbs}g F${entry.fat}g</div>
        </div>
      </div>
      <div class="list-row-meta">
        <span class="list-row-cal">${Math.round(entry.calories)} kcal</span>
        <button class="row-delete" data-delete-food-log="${entry.id}" aria-label="Remove">
          <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
        </button>
      </div>`;
    container.appendChild(row);
    attachDeleteHandler(row.querySelector("[data-delete-food-log]"));
    updateMealTotal(mealType);
  }

  function updateMealTotal(mealType) {
    const container = document.getElementById(`meal-${mealType}`);
    const card = container.closest(".meal-card");
    const rows = container.querySelectorAll(".list-row-cal");
    let total = 0;
    rows.forEach((r) => (total += parseFloat(r.textContent) || 0));
    card.querySelector(`[data-meal-total="${mealType}"]`).textContent = `${Math.round(total)} kcal`;

    if (rows.length === 0 && !card.querySelector(".empty-meal")) {
      const label = card.querySelector("h3").textContent;
      const div = document.createElement("div");
      div.className = "empty-state empty-meal";
      div.style.padding = "26px 10px";
      div.innerHTML = `<p class="text-sm">No items logged for ${label.toLowerCase()} yet.</p>`;
      card.appendChild(div);
    }
  }

  function updateTodayTotals(totals) {
    const pct = Math.max(0, Math.min((totals.calories / CALORIE_GOAL) * 100, 100));
    document.querySelector(".progress-fill").style.width = `${pct}%`;
    document.querySelectorAll(".card-solid .text-sm")[0].textContent = `${Math.round(totals.calories)} kcal`;
    const chips = document.querySelectorAll("#modalMacroPreview, .macro-chip-row");
    const totalsChipRow = document.querySelectorAll(".macro-chip-row")[0];
    if (totalsChipRow) {
      totalsChipRow.querySelector(".protein .mval").textContent = `${totals.protein}g`;
      totalsChipRow.querySelector(".carbs .mval").textContent = `${totals.carbs}g`;
      totalsChipRow.querySelector(".fat .mval").textContent = `${totals.fat}g`;
    }
  }

  function attachDeleteHandler(btn) {
    btn.addEventListener("click", async () => {
      const logId = btn.getAttribute("data-delete-food-log");
      const row = btn.closest(".list-row");
      const mealType = row.closest(".meal-card").getAttribute("data-meal");
      try {
        const data = await api(`/api/food/log/${logId}`, { method: "DELETE" });
        row.remove();
        updateMealTotal(mealType);
        updateTodayTotals(data.totals);
        showToast("Removed from log.", "info");
      } catch (e) {
        showToast(e.message, "error");
      }
    });
  }

  document.querySelectorAll("[data-delete-food-log]").forEach(attachDeleteHandler);
})();
