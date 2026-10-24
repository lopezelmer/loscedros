# Copyright (c) 2026, Condominio Los Cedros
"""/update-password con el diseño de Los Cedros (cambiar o crear contraseña).

La logica sigue siendo la de Frappe (frappe.core.doctype.user.user.update_password).
"""

import frappe
from frappe.www.update_password import get_context as frappe_update_password_context

no_cache = 1


def get_context(context):
    con_enlace = bool(frappe.form_dict.get("key"))

    # Sin enlace de recuperacion hace falta la contrasena actual: primero iniciar sesion.
    if not con_enlace and frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/update-password"
        raise frappe.Redirect

    frappe_update_password_context(context)
    context.update({
        "title": "Cambiar contraseña · Condominio Los Cedros",
        "body_class": "lc-login-page lc-pass-page",
        "lc_con_enlace": con_enlace,
        "disable_signup": 1,  # no mostrar «Sign up» en esta pagina
    })
    return context
