# Copyright (c) 2026, Condominio Los Cedros
"""Paginas de mensaje de Frappe (respond_as_web_page) con el diseño de Los Cedros.

Incluye «Logged Out» (/?cmd=web_logout), «Not Permitted», enlaces vencidos, etc.
"""

import frappe
from frappe.www.message import get_context as frappe_message_context

no_cache = 1

# Titulos y mensajes comunes de Frappe -> espanol (si el sitio ya esta en espanol, no se tocan)
TITULOS = {
    "Logged Out": "Sesión cerrada",
    "Not Permitted": "Acceso no permitido",
    "Invalid Request": "Solicitud no válida",
    "Message": "Mensaje",
    "Password set": "Contraseña guardada",
    "Link Expired": "Enlace vencido",
    "Session Expired": "Sesión vencida",
}
MENSAJES = {
    "You have been successfully logged out": "Cerraste sesión correctamente. Gracias por usar el Portal de Residentes.",
    "You need to be logged in to access this page": "Necesitas iniciar sesión para ver esta página.",
}
SALIDA = {"Logged Out", "Sesión cerrada"}


def get_context(context):
    datos = frappe._dict(frappe_message_context(context) or {})

    titulo_original = (datos.get("title") or context.get("title") or "").strip()
    titulo = TITULOS.get(titulo_original, titulo_original)
    mensaje = datos.get("message") or context.get("message") or ""
    mensaje = MENSAJES.get(str(mensaje).strip(), mensaje)

    color = context.get("indicator_color") or "blue"
    tono = "ok" if color == "green" else ("bad" if color in ("red", "orange") else "info")

    datos.update({
        "title": titulo or "Mensaje",
        "message": mensaje,
        "body_class": "lc-login-page lc-msg-page",
        "lc_tono": tono,
        "lc_salida": titulo_original in SALIDA,
        "lc_boton": "Ir al inicio" if context.get("primary_label") in (None, "", "Home") else context.get("primary_label"),
    })
    return datos
