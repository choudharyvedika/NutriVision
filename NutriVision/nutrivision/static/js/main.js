/* ==========================================================================
   NutriVision — shared front-end behaviour (sidebar, flashes, fetch helper)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // ---- Mobile sidebar toggle ----
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  const menuBtn = document.getElementById("menuBtn");

  function openSidebar() {
    sidebar?.classList.add("open");
    backdrop?.classList.add("open");
  }
  function closeSidebar() {
    sidebar?.classList.remove("open");
    backdrop?.classList.remove("open");
  }
  menuBtn?.addEventListener("click", openSidebar);
  backdrop?.addEventListener("click", closeSidebar);

  // ---- Auto-dismiss flash messages ----
  document.querySelectorAll(".flash").forEach((flash, i) => {
    setTimeout(() => {
      flash.style.transition = "opacity .3s ease, transform .3s ease";
      flash.style.opacity = "0";
      flash.style.transform = "translateX(16px)";
      setTimeout(() => flash.remove(), 300);
    }, 5000 + i * 300);
  });
});

/**
 * Small wrapper around fetch() for our JSON API endpoints.
 * Throws an Error with a human-readable message on failure so callers
 * can show it directly in a flash/toast.
 */
async function api(url, options = {}) {
  const opts = {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json" },
  };
  if (options.body) opts.body = JSON.stringify(options.body);

  const res = await fetch(url, opts);
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }
  if (!res.ok) {
    throw new Error((data && data.error) || "Something went wrong. Please try again.");
  }
  return data;
}

/** Show a transient toast without a page reload (mirrors server flash style). */
function showToast(message, category = "success") {
  const stack = document.getElementById("flashStack");
  if (!stack) return;
  const div = document.createElement("div");
  div.className = `flash ${category}`;
  div.innerHTML = `<span>${message}</span><button class="flash-close">&times;</button>`;
  div.querySelector(".flash-close").addEventListener("click", () => div.remove());
  stack.appendChild(div);
  setTimeout(() => {
    div.style.transition = "opacity .3s ease, transform .3s ease";
    div.style.opacity = "0";
    div.style.transform = "translateX(16px)";
    setTimeout(() => div.remove(), 300);
  }, 4500);
}
