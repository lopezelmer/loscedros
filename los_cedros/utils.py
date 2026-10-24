# Copyright (c) 2026, Condominio Los Cedros
"""Utilidades compartidas por las paginas del sitio y del Portal de Residentes."""

import frappe
from frappe.sessions import get_csrf_token

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>')
ICONOS = {
    "herramienta": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.2L3 17.8V21h3.2l6.3-6.3a4 4 0 0 0 5.2-5.4l-2.6 2.6-2.4-.4-.4-2.4z"/>',
    "agua": '<path d="M12 2.7s-6 6.6-6 11.3a6 6 0 0 0 12 0c0-4.7-6-11.3-6-11.3Z"/>',
    "rayo": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "escudo": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>',
    "plaga": '<path d="M16 7h.01M3.4 18H12a8 8 0 0 0 8-8V7a4 4 0 0 0-7.3-2.3L2 20M20 7l2 .5-2 .5M10 18v3M14 17.7V21"/>',
    "ruido": '<path d="M11 5 6 9H2v6h4l5 4zM15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14"/>',
    "parque": '<path d="M12 22v-6M7 22h10M12 2a5 5 0 0 0-5 5l.2 1.4A4 4 0 0 0 8 16h8a4 4 0 0 0 .8-7.6L17 7a5 5 0 0 0-5-5Z"/>',
    "factura": '<path d="M5 2h14v20l-3-2-2 2-2-2-2 2-2-2-3 2zM9 7h6M9 11h6M9 15h4"/>',
    "otro": '<circle cx="12" cy="12" r="9"/><path d="M8 12h.01M12 12h.01M16 12h.01"/>',
}

# Estados de HD Ticket -> (texto para el residente, clase de color, abierto?)
ESTADOS = {
    "Open": ("Abierto", "s-open", True),
    "Replied": ("Respondido", "s-replied", True),
    "Paused": ("En pausa", "s-paused", True),
    "Resolved": ("Resuelto", "s-resolved", False),
    "Closed": ("Cerrado", "s-closed", False),
}


def icono_svg(nombre):
    return _SVG.format(ICONOS.get(nombre) or ICONOS["otro"])


def estado_info(status):
    texto, clase, abierto = ESTADOS.get(status, (status or "Abierto", "s-open", True))
    return frappe._dict(texto=texto, clase=clase, abierto=abierto)


def fecha_txt(valor):
    if not valor:
        return ""
    d = frappe.utils.get_datetime(valor)
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def titulo_residente(asunto, categoria):
    """Quita el prefijo «Categoria · Edif. X, Apt. Y: » que el asunto lleva para Helpdesk."""
    asunto = asunto or ""
    if categoria and asunto.startswith(categoria + " · ") and ": " in asunto:
        return asunto.split(": ", 1)[1]
    return asunto


def lineas(texto):
    return [x.strip() for x in (texto or "").splitlines() if x.strip()]


def categorias_publicas():
    """Categorias activas, en orden, con lo que necesitan las paginas."""
    nombres = frappe.get_all("Categoria Reporte", filters={"activo": 1}, pluck="name",
                             order_by="orden asc, name asc")
    salida = []
    for n in nombres:
        c = frappe.get_doc("Categoria Reporte", n)
        salida.append(frappe._dict(
            nombre=c.name,
            titulo=c.titulo or "",
            tiempo=c.tiempo_respuesta or "",
            aviso=c.aviso or "",
            sugerencias=lineas(c.sugerencias),
            icono_svg=icono_svg(c.icono),
            campos=[{"e": f.etiqueta, "tipo": f.tipo, "ops": lineas(f.opciones), "req": bool(f.obligatorio)}
                    for f in c.campos],
        ))
    return salida


def contexto_portal(context, ruta, activo):
    """Comun a /reportar y /mis-reportes: exige sesion y prepara cabecera y pie."""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=" + ruta
        raise frappe.Redirect

    user = frappe.session.user
    info = frappe.db.get_value("User", user, ["email", "full_name", "first_name"], as_dict=True) or {}
    context.update({
        "no_cache": 1,
        "activo": activo,
        "cfg": frappe.get_single("Configuracion Sitio"),
        "email": (info.get("email") or user),
        "nombre_usuario": info.get("first_name") or info.get("full_name") or user,
        "csrf_token": get_csrf_token(),
        "show_sidebar": 0,
    })
    return context
