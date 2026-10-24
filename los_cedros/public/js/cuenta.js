/* Los Cedros · /update-password: Spanish labels. Runs after Frappe's own page script. */
(function () {
  "use strict";
  var conEnlace = /[?&]key=/.test(window.location.search);

  function text(sel, value) { document.querySelectorAll(sel).forEach(function (el) { el.textContent = value; }); }
  function ph(sel, value) { var el = document.querySelector(sel); if (el) el.setAttribute("placeholder", value); }

  function apply() {
    var head = document.querySelector(".for-reset-password .page-card-head");
    text(".reset-password-heading", conEnlace ? "Crear contraseña nueva" : "Cambiar contraseña");
    if (head && !head.querySelector(".lc-sub")) {
      head.insertAdjacentHTML("beforeend", '<p class="lc-sub">' + (conEnlace
        ? "Escribe tu contraseña nueva dos veces para confirmarla."
        : "Escribe tu contraseña actual y luego la nueva dos veces.") + "</p>");
    }
    ph("#old_password", "Contraseña actual");
    ph("#new_password", "Contraseña nueva");
    ph("#confirm_password", "Confirmar contraseña nueva");
    text(".btn-update", "Guardar contraseña");

    // Frappe's success message and redirect stay as they are; translate its fixed texts
    var MSG = {
      "Passwords do not match": "Las contraseñas no coinciden",
      "New password cannot be same as old password": "La contraseña nueva no puede ser igual a la actual",
      "Success! You are good to go 👍": "¡Listo! Contraseña segura.",
      "Status Updated": "Contraseña guardada",
      "Invalid Password": "Contraseña incorrecta",
      "Invalid Link": "Enlace no válido o vencido",
    };
    var watch = document.querySelectorAll(".password-mismatch-message, .password-strength-message, .reset-password-heading");
    if (window.MutationObserver) {
      var obs = new MutationObserver(function () {
        watch.forEach(function (el) {
          var t = (el.textContent || "").trim();
          if (MSG[t]) { obs.disconnect(); el.textContent = MSG[t]; obs.observe(document.body, { childList: true, subtree: true, characterData: true }); }
        });
      });
      obs.observe(document.body, { childList: true, subtree: true, characterData: true });
    }
  }

  if (window.frappe && typeof frappe.ready === "function") frappe.ready(apply);
  else document.addEventListener("DOMContentLoaded", apply);
})();
