(function () {
  "use strict";

  function emitEvent(name) {
    if (typeof window.gtag === "function") {
      window.gtag("event", name, { event_category: "homepage" });
    }
  }

  function setupCopyButton(root) {
    var button = root.querySelector("[data-hb-copy]");
    if (!button) return;

    var label = button.querySelector("[data-hb-copy-label]");
    var command = root.querySelector(".hb-command code");
    button.addEventListener("click", function () {
      if (!command || !navigator.clipboard) return;
      navigator.clipboard.writeText(command.textContent.trim()).then(function () {
        label.textContent = "Copied";
        button.setAttribute("aria-label", "Installation command copied");
        emitEvent("home_install_copy");
        window.setTimeout(function () {
          label.textContent = "Copy";
          button.setAttribute("aria-label", "Copy installation command");
        }, 1800);
      });
    });
  }

  function activateFrame(scene, index) {
    var frames = Array.prototype.slice.call(scene.querySelectorAll("[data-hb-frame]"));
    frames.forEach(function (frame, frameIndex) {
      var active = frameIndex === index;
      frame.classList.toggle("is-active", active);
      frame.setAttribute("aria-hidden", active ? "false" : "true");
    });
  }

  function activateStep(scene, step) {
    scene.querySelectorAll("[data-hb-step]").forEach(function (candidate) {
      candidate.classList.toggle("is-active", candidate === step);
    });
  }

  function setupScenes(root) {
    var motionQuery = window.matchMedia("(min-width: 901px) and (prefers-reduced-motion: no-preference)");
    if (!motionQuery.matches || !("IntersectionObserver" in window)) return;

    document.documentElement.classList.add("hb-motion");
    var scenes = Array.prototype.slice.call(root.querySelectorAll("[data-hb-scene]"));

    scenes.forEach(function (scene) {
      activateFrame(scene, 0);
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) activateStep(scene, entry.target);
        });
      }, { rootMargin: "-35% 0px -50% 0px", threshold: 0 });
      scene.querySelectorAll("[data-hb-step]").forEach(function (step) {
        observer.observe(step);
      });
    });

    var ticking = false;
    function updateScenes() {
      scenes.forEach(function (scene) {
        var frames = scene.querySelectorAll("[data-hb-frame]");
        if (frames.length < 2) return;
        var steps = scene.querySelector(".hb-scene__steps");
        var rect = (steps || scene).getBoundingClientRect();
        if (rect.bottom < 0 || rect.top > window.innerHeight) return;
        var focalPoint = window.innerHeight * 0.5;
        var progress = Math.min(1, Math.max(0, (focalPoint - rect.top) / Math.max(1, rect.height)));
        var index = Math.min(frames.length - 1, Math.floor(progress * frames.length));
        activateFrame(scene, index);
      });
      ticking = false;
    }

    function requestUpdate() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(updateScenes);
    }

    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate);
    requestUpdate();
  }

  function setupAnalytics(root) {
    root.querySelectorAll("[data-hb-event]").forEach(function (link) {
      link.addEventListener("click", function () { emitEvent(link.getAttribute("data-hb-event")); });
    });
  }

  function init() {
    var root = document.querySelector(".hb-home");
    if (!root) return;
    setupCopyButton(root);
    setupScenes(root);
    setupAnalytics(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
}());
