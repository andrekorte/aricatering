/* Ari Thai Catering — progressive enhancement only.
   Without JS the enquiry form is a single long form that still submits;
   this turns it into a 3-step flow and drives the mobile nav. */
(function () {
  "use strict";

  /* ---- Mobile navigation ------------------------------------------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        toggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        toggle.focus();
      }
    });
  }

  /* ---- Multi-step enquiry form -------------------------------------- */
  var form = document.getElementById("enquiry-form");
  if (!form) return;

  var steps = Array.prototype.slice.call(form.querySelectorAll(".fieldset"));
  var progress = Array.prototype.slice.call(document.querySelectorAll(".progress li"));
  if (steps.length < 2) return;

  var last = steps.length - 1;
  var current = 0;

  /* Each step carries its own Back / Continue / Send buttons so the form
     still reads correctly with JS off — so show/hide them per step. */
  function render() {
    steps.forEach(function (step, i) {
      step.hidden = i !== current;

      var back = step.querySelector('[data-nav="back"]');
      var next = step.querySelector('[data-nav="next"]');
      var send = step.querySelector('[data-nav="submit"]');
      if (back) back.hidden = i === 0;
      if (next) next.hidden = i === last;
      if (send) send.hidden = i !== last;
    });

    progress.forEach(function (item, i) {
      item.classList.toggle("is-done", i < current);
      if (i === current) {
        item.setAttribute("aria-current", "step");
      } else {
        item.removeAttribute("aria-current");
      }
    });
  }

  /* Native validation, scoped to one step at a time. */
  function firstInvalid(step) {
    var fields = step.querySelectorAll("input, select, textarea");
    for (var i = 0; i < fields.length; i++) {
      if (!fields[i].checkValidity()) return fields[i];
    }
    return null;
  }

  function go(delta) {
    if (delta > 0) {
      var bad = firstInvalid(steps[current]);
      if (bad) {
        bad.reportValidity();
        return;
      }
    }
    current = Math.min(Math.max(current + delta, 0), last);
    render();

    var legend = steps[current].querySelector("legend");
    if (legend) {
      legend.setAttribute("tabindex", "-1");
      legend.focus({ preventScroll: true });
    }
    form.scrollIntoView({ block: "start", behavior: "smooth" });
  }

  /* Delegated so every step's buttons work, not just the first step's. */
  form.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-nav]");
    if (!btn || btn.dataset.nav === "submit") return;
    e.preventDefault();
    go(btn.dataset.nav === "next" ? 1 : -1);
  });

  /* Enter advances instead of submitting a half-filled form. */
  form.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && e.target.tagName !== "TEXTAREA" && current < last) {
      e.preventDefault();
      go(1);
    }
  });

  /* A hidden step can't be validated by the browser — check them all. */
  form.addEventListener("submit", function (e) {
    for (var i = 0; i < steps.length; i++) {
      var bad = firstInvalid(steps[i]);
      if (bad) {
        e.preventDefault();
        current = i;
        render();
        bad.reportValidity();
        return;
      }
    }
  });

  form.classList.add("is-stepped");
  render();
})();
