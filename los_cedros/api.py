# Copyright (c) 2026, Condominio Los Cedros
"""Portal de Residentes: crea y responde casos de Helpdesk (HD Ticket) desde el sitio.

Cada funcion exige sesion iniciada (no allow_guest) y verifica en el servidor
que el residente solo vea y responda sus propios casos.
"""

import json
import re

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, escape_html

MAX_FOTOS = 3
MAX_BYTES = 8 * 1024 * 1024
CONTACTOS = ("Correo", "Teléfono")


# ---------------------------------------------------------------- ayudas
def usuario_actual():
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Inicia sesión para continuar."), frappe.PermissionError)
    email = frappe.db.get_value("User", user, "email") or user
    return user, email


def es_dueno(ticket, user, email):
    return ticket.owner == user or (ticket.raised_by or "").strip().lower() == (email or "").lower()


def obtener_ticket(caso, user, email):
    """El ticket del residente, o 'no encontrado' (sin revelar si existe)."""
    n = cint(caso)
    if n > 0 and frappe.db.exists("HD Ticket", n):
        t = frappe.get_doc("HD Ticket", n)
        if es_dueno(t, user, email):
            return t
    frappe.throw(_("No encontramos ese caso."), frappe.DoesNotExistError)


def _txt(valor, maximo):
    return ("" if valor is None else str(valor)).strip()[:maximo]


def _html_parrafos(texto):
    return "<p>" + escape_html(texto).replace("\n", "<br>") + "</p>"


def _tipo_imagen(data):
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[4:8] == b"ftyp" and data[8:12] in (b"heic", b"heix", b"mif1", b"msf1", b"hevc"):
        return "heic"
    return None


def _fotos_recibidas():
    req = getattr(frappe, "request", None)
    archivos = req.files.getlist("fotos") if req is not None and req.files else []
    if len(archivos) > MAX_FOTOS:
        frappe.throw(_("Puedes adjuntar hasta {0} fotos.").format(MAX_FOTOS))
    fotos = []
    for a in archivos:
        data = a.stream.read(MAX_BYTES + 1)
        if not data:
            continue
        if len(data) > MAX_BYTES:
            frappe.throw(_("Cada foto debe pesar menos de 8 MB."))
        ext = _tipo_imagen(data)
        if not ext:
            frappe.throw(_("Solo se aceptan fotos JPG, PNG, WEBP o HEIC."))
        fotos.append((data, ext))
    return fotos


def _guardar_residente(user, edificio, apartamento, telefono, contacto, verificado):
    if frappe.db.exists("Residente", user):
        r = frappe.get_doc("Residente", user)
    else:
        r = frappe.new_doc("Residente")
        r.usuario = user
    if not verificado:
        r.edificio, r.apartamento = edificio, apartamento
    if telefono:
        r.telefono = telefono
    r.contacto_preferido = contacto
    r.flags.ignore_permissions = True
    r.save(ignore_permissions=True)


# ---------------------------------------------------------------- crear reporte
@frappe.whitelist(methods=["POST"])
@rate_limit(limit=10, seconds=60 * 60)
def crear_reporte(categoria, descripcion, edificio=None, apartamento=None, extras=None,
                  contacto=None, telefono=None):
    user, email = usuario_actual()

    categoria = _txt(categoria, 140)
    if not categoria or not frappe.db.exists("Categoria Reporte", {"name": categoria, "activo": 1}):
        frappe.throw(_("Escoge una categoría válida."))
    cat = frappe.get_doc("Categoria Reporte", categoria)

    descripcion = _txt(descripcion, 4000)
    if len(descripcion) < 10:
        frappe.throw(_("Describe la situación con al menos 10 caracteres."))

    contacto = contacto if contacto in CONTACTOS else "Correo"
    telefono = _txt(telefono, 30)
    if contacto == "Teléfono" and len(re.sub(r"\D", "", telefono)) < 7:
        frappe.throw(_("Escribe un teléfono válido para que la Administración te llame."))

    # Edificio y apartamento: si la Administracion los verifico, se usan los suyos.
    res = frappe.db.get_value("Residente", user, ["edificio", "apartamento", "verificado"], as_dict=True)
    verificado = bool(res and res.verificado)
    if verificado:
        edificio, apartamento = res.edificio or "", res.apartamento or ""
    else:
        edificio, apartamento = _txt(edificio, 20), _txt(apartamento, 20)
        if not edificio or not apartamento:
            frappe.throw(_("Indica tu edificio y apartamento."))

    # Campos propios de la categoria: las etiquetas salen de la configuracion, no del navegador.
    try:
        valores = json.loads(extras or "[]")
    except (TypeError, ValueError):
        valores = []
    if not isinstance(valores, list):
        valores = []
    filas = []
    for i, campo in enumerate(cat.campos):
        v = _txt(valores[i] if i < len(valores) else "", 300)
        if campo.tipo == "Sí/No":
            v = v if v in ("Sí", "No") else ""
        elif campo.tipo == "Opciones":
            v = v if v in [o.strip() for o in (campo.opciones or "").splitlines() if o.strip()] else ""
        if campo.obligatorio and not v:
            frappe.throw(_("Completa el campo: {0}").format(campo.etiqueta))
        if v:
            filas.append((campo.etiqueta, v))

    fotos = _fotos_recibidas()

    def fila(k, v):
        return f"<tr><td><b>{escape_html(k)}</b></td><td>{escape_html(v)}</td></tr>"

    tabla = [fila("Categoría", cat.name), fila("Edificio", edificio), fila("Apartamento", apartamento)]
    tabla += [fila(k, v) for k, v in filas]
    tabla.append(fila("Contacto preferido", contacto))
    if telefono:
        tabla.append(fila("Teléfono", telefono))
    descripcion_html = (
        _html_parrafos(descripcion)
        + "<table>" + "".join(tabla) + "</table>"
        + f"<p><small>Enviado desde el sitio web de Los Cedros · {len(fotos)} foto(s)</small></p>"
    )
    resumen = re.sub(r"\s+", " ", descripcion)
    asunto = f"{cat.name} · Edif. {edificio}, Apt. {apartamento}: {resumen}"
    asunto = asunto if len(asunto) <= 140 else asunto[:139] + "…"

    meta = frappe.get_meta("HD Ticket")
    datos = {
        "subject": asunto,
        "description": descripcion_html,
        "raised_by": email,
        "ticket_type": cat.name,
        "priority": cat.prioridad,
        "agent_group": cat.equipo,
        "via_customer_portal": 1,
    }
    datos = {k: v for k, v in datos.items() if v and meta.has_field(k)}
    ticket = frappe.get_doc({"doctype": "HD Ticket", **datos})
    ticket.flags.ignore_permissions = True
    ticket.insert(ignore_permissions=True)

    for n, (data, ext) in enumerate(fotos, 1):
        frappe.get_doc({
            "doctype": "File",
            "file_name": f"reporte-{ticket.name}-{n}.{ext}",
            "attached_to_doctype": "HD Ticket",
            "attached_to_name": ticket.name,
            "is_private": 1,
            "content": data,
        }).insert(ignore_permissions=True)

    _guardar_residente(user, edificio, apartamento, telefono, contacto, verificado)
    return {"caso": ticket.name}


# ---------------------------------------------------------------- responder
@frappe.whitelist(methods=["POST"])
@rate_limit(limit=30, seconds=60 * 60)
def responder(caso, mensaje):
    user, email = usuario_actual()
    ticket = obtener_ticket(caso, user, email)
    if ticket.status == "Closed":
        frappe.throw(_("Este caso está cerrado. Crea un reporte nuevo si necesitas ayuda."))

    mensaje = _txt(mensaje, 4000)
    if len(mensaje) < 2:
        frappe.throw(_("Escribe tu mensaje."))
    html = _html_parrafos(mensaje)

    ticket.flags.ignore_permissions = True
    metodo = getattr(ticket, "create_communication_via_contact", None)
    if callable(metodo):
        metodo(html)  # metodo de Helpdesk: guarda la respuesta y reabre el caso
    else:
        _respuesta_manual(ticket, html, email)
    return {"ok": True}


def _respuesta_manual(ticket, html, email):
    """Respaldo por si una version de Helpdesk no tiene create_communication_via_contact."""
    frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "sent_or_received": "Received",
        "subject": ticket.subject,
        "content": html,
        "sender": email,
        "sender_full_name": frappe.utils.get_fullname(frappe.session.user),
        "recipients": email,
        "reference_doctype": "HD Ticket",
        "reference_name": ticket.name,
    }).insert(ignore_permissions=True)
    if ticket.status in ("Replied", "Resolved"):
        ticket.status = "Open"
        ticket.save(ignore_permissions=True)
