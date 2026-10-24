# Copyright (c) 2026, Condominio Los Cedros
"""/login con el diseño de Los Cedros.

Reutiliza el controlador de Frappe (redirecciones, 2FA, LDAP, recuperar contraseña)
y solo cambia la marca y quita «Login with Email Link».
"""

import frappe
from frappe.www.login import get_context as frappe_login_context

no_cache = True


def get_context(context):
    frappe_login_context(context)  # si ya hay sesion, redirige como siempre

    cfg = frappe.get_single("Configuracion Sitio")
    context.update({
        "title": "Iniciar sesión · Condominio Los Cedros",
        "body_class": "lc-login-page",
        "logo": "/assets/los_cedros/images/icono.svg",
        "app_name": "Los Cedros",
        "login_with_email_link": False,  # opcion eliminada en este sitio
        "lc_cfg": cfg,
    })
    return context
