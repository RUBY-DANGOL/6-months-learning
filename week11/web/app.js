const toggleButton = document.getElementById("toggleDetails");
const detailsPanel = document.getElementById("detailsPanel");

toggleButton?.addEventListener("click", () => {
  const hidden = detailsPanel.classList.toggle("hidden");
  toggleButton.textContent = hidden ? "Show rollout checklist" : "Hide rollout checklist";
});
