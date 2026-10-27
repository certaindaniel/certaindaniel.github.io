(() => {
  const filters = document.querySelector(".map-filters");
  const index = document.querySelector(".map-index");
  const dialog = document.querySelector(".island-dialog");
  let returnFocus = null;
  if (filters) {
    filters.hidden = false;
    filters.querySelectorAll("[data-filter]").forEach(button => {
      button.addEventListener("click", () => {
        const selected = button.dataset.filter;
        filters.querySelectorAll("[data-filter]").forEach(option => {
          option.setAttribute("aria-pressed", String(option === button));
        });
        document.querySelectorAll("[data-region]").forEach(region => {
          region.hidden = selected !== "all" && region.dataset.region !== selected;
        });
        document.querySelectorAll("[data-index-region]").forEach(group => {
          group.hidden = selected !== "all" && group.dataset.indexRegion !== selected;
        });
        if (index) index.open = false;
      });
    });
  }
  if (!dialog || typeof dialog.showModal !== "function") return;
  document.querySelectorAll("a.island-detail-trigger").forEach(link => {
    link.addEventListener("click", event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      document.getElementById("dialog-title").textContent = link.dataset.name;
      document.getElementById("dialog-status").textContent = link.dataset.status;
      document.getElementById("dialog-description").textContent = link.dataset.description;
      document.getElementById("dialog-icon").src = link.dataset.icon;
      document.getElementById("dialog-link").href = link.href;
      returnFocus = index && index.contains(link) ? index.querySelector("summary") : link;
      if (index) index.open = false;
      dialog.showModal();
    });
  });
  dialog.addEventListener("click", event => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => {
    if (returnFocus) returnFocus.focus();
  });
})();
