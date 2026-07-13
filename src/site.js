/* Accordion, deep links, and copy-link buttons.
   No dependencies. Everything degrades gracefully without JS:
   content is in the page either way. */
(function () {
  "use strict";

  var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function setOpen(item, open) {
    var btn = item.querySelector(".item-toggle");
    if (!btn) return;
    item.classList.toggle("open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  // Toggle on click; multiple sections may be open at once and siblings
  // are never auto-collapsed.
  document.querySelectorAll(".item-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".item");
      setOpen(item, !item.classList.contains("open"));
    });
  });

  // Deep links: arriving at #slug (or clicking a #slug link in the page)
  // opens that section and scrolls to it.
  function openFromHash() {
    var hash = decodeURIComponent(window.location.hash.replace(/^#/, ""));
    if (!hash) return;
    var target = document.getElementById(hash);
    if (!target) return;
    var item = target.closest ? target.closest(".item") : null;
    if (item) {
      setOpen(item, true);
      window.requestAnimationFrame(function () {
        item.scrollIntoView({
          behavior: reducedMotion.matches ? "auto" : "smooth",
          block: "start"
        });
      });
    }
  }

  window.addEventListener("hashchange", openFromHash);
  openFromHash();

  // Copy-link buttons.
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.left = "-9999px";
      document.body.appendChild(area);
      area.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      document.body.removeChild(area);
      if (ok) { resolve(); } else { reject(new Error("copy failed")); }
    });
  }

  document.querySelectorAll(".copy-link").forEach(function (btn) {
    var label = btn.textContent;
    btn.addEventListener("click", function () {
      var url = window.location.href.split("#")[0] + "#" + btn.dataset.slug;
      copyText(url).then(function () {
        btn.textContent = "Copied";
        btn.classList.add("copied");
        window.setTimeout(function () {
          btn.textContent = label;
          btn.classList.remove("copied");
        }, 1800);
      }).catch(function () {
        // Last resort: show the URL so it can be copied by hand.
        window.prompt("Copy this link:", url);
      });
    });
  });
})();
