(function () {
  const FEEDBACK_URL =
    "https://sambaxp.org/#Registration";
  const STORAGE_KEY = "hb_hide_feedback_fab_v2";

  // Respect prior dismissal
  try { if (localStorage.getItem(STORAGE_KEY) === "1") return; } catch (e) {}

  const fab = document.createElement("div");
  fab.className = "hb-fab";
  fab.innerHTML = `
    <a class="hb-fab__link"
       href="${FEEDBACK_URL}"
       target="_blank" rel="noopener noreferrer">
      <span class="hb-fab__text">📢 Register to join us at sambaXP April 2026!
    </a>
    <button class="hb-fab__close" type="button" aria-label="Hide this message">×</button>
  `;
  document.addEventListener("DOMContentLoaded", () => {
    document.body.appendChild(fab);

    // Avoid overlap with Material's back-to-top button (.md-top)
    const adjust = () => {
      const topBtn = document.querySelector(".md-top");
      if (!topBtn) { fab.style.bottom = "1.5rem"; return; }
      const rect = topBtn.getBoundingClientRect();
      const nearCorner =
        window.innerWidth - rect.right < 140 &&
        window.innerHeight - rect.top < 140;
      fab.style.bottom = nearCorner ? "6.5rem" : "1.5rem";
    };
    adjust();
    window.addEventListener("resize", adjust);
    window.addEventListener("scroll", adjust);

    fab.querySelector(".hb-fab__close")?.addEventListener("click", () => {
      fab.remove();
      try { localStorage.setItem(STORAGE_KEY, "1"); } catch (e) {}
    });
  });
})();
