/* Los Cedros · /login: no email-link login, Spanish labels. Runs after Frappe's login.js. */
(function () {
  "use strict";

  // 1) Login with Email Link is disabled: send that address back to the normal login.
  if (window.login) {
    window.login.login_with_email_link = function () { window.location.replace("#login"); };
  }
  if (window.location.hash === "#login-with-email-link") {
    try { history.replaceState(null, "", "#login"); } catch (e) { window.location.hash = "#login"; }
  }

  // 2) Spanish for the status messages Frappe shows on the button.
  var MSG = {
    "Verifying...": "Verificando…",
    "Success": "Listo",
    "Invalid Login. Try again.": "Correo o contraseña incorrectos.",
    "Oops! Something went wrong.": "Algo salió mal. Intenta de nuevo.",
    "Something went wrong.": "Algo salió mal. Intenta de nuevo.",
    "Too many requests. Please try again later.": "Demasiados intentos. Espera unos minutos.",
    "Instructions Emailed": "Te enviamos las instrucciones por correo",
    "Valid Login id required.": "Escribe tu correo electrónico.",
    "Login": "Entrar",
    "Reset Password": "Enviar instrucciones",
  };
  if (window.login && typeof window.login.set_status === "function") {
    var original = window.login.set_status;
    window.login.set_status = function (message, color) {
      return original.call(this, MSG[message] || message, color);
    };
  }

  function text(sel, value) {
    document.querySelectorAll(sel).forEach(function (el) { el.textContent = value; });
  }
  function attr(sel, name, value) {
    var el = document.querySelector(sel);
    if (el) el.setAttribute(name, value);
  }

  function apply() {
    // remove the email-link section and button entirely
    document.querySelectorAll("section.for-login-with-email-link, .login-with-email-link").forEach(function (n) { n.remove(); });

    // headings
    text(".for-login .page-card-head h4, .for-email-login .page-card-head h4", "Iniciar sesión");
    text(".for-forgot .page-card-head h4", "Recuperar contraseña");
    text(".for-signup .page-card-head h4", "Crear cuenta");
    document.querySelectorAll(".for-login .page-card-head, .for-email-login .page-card-head").forEach(function (h) {
      if (!h.querySelector(".lc-sub")) h.insertAdjacentHTML("beforeend", '<p class="lc-sub">Entra con el correo y la contraseña de tu cuenta de residente.</p>');
    });
    document.querySelectorAll(".for-forgot .page-card-head").forEach(function (h) {
      if (!h.querySelector(".lc-sub")) h.insertAdjacentHTML("beforeend", '<p class="lc-sub">Escribe tu correo y te enviaremos un enlace para crear una contraseña nueva.</p>');
    });

    // login form
    text('label[for="login_email"]', "Correo electrónico");
    text('label[for="login_password"]', "Contraseña");
    attr("#login_email", "placeholder", "tu@correo.com");
    attr("#login_password", "placeholder", "Contraseña");
    text(".forgot-password-message a", "¿Olvidaste tu contraseña?");
    text(".for-login .btn-login:not(.btn-ldap-login), .for-email-login .btn-login:not(.btn-ldap-login)", "Entrar");
    text(".toggle-password", "Mostrar");
    $(".toggle-password").on("click", function () {
      var input = document.querySelector(this.getAttribute("toggle"));
      this.textContent = input && input.type === "password" ? "Mostrar" : "Ocultar";
    });

    // forgot password
    attr("#forgot_email", "placeholder", "tu@correo.com");
    text(".btn-forgot", "Enviar instrucciones");
    text(".for-forgot .sign-up-message a", "Volver a iniciar sesión");

    // sign-up (only visible if signup is enabled in Website Settings)
    text(".for-login .sign-up-message", "");
    document.querySelectorAll(".for-login .sign-up-message").forEach(function (el) {
      el.innerHTML = '¿No tienes cuenta? <a href="#signup">Crear cuenta</a>';
    });
  }

  if (window.frappe && typeof frappe.ready === "function") {
    frappe.ready(apply);
  } else {
    document.addEventListener("DOMContentLoaded", apply);
  }
})();
