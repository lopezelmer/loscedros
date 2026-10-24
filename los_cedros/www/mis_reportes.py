import json

import frappe
from frappe.utils.html_utils import sanitize_html

from los_cedros.api import obtener_ticket
from los_cedros.utils import contexto_portal, estado_info, fecha_txt, titulo_residente

no_cache = 1


def get_context(context):
    contexto_portal(context, "/mis-reportes", "mis")
    user, email = frappe.session.user, context.email
    caso = frappe.form_dict.get("caso")

    if caso:
        t = obtener_ticket(caso, user, email)
        mensajes = [{
            "de": "tu",
            "autor": "Tú",
            "fecha": fecha_txt(t.opening_date or t.creation),
            "html": sanitize_html(t.description or ""),
        }]
        comms = frappe.get_all(
            "Communication",
            filters={"reference_doctype": "HD Ticket", "reference_name": t.name,
                     "communication_type": "Communication"},
            fields=["content", "sent_or_received", "creation"],
            order_by="creation asc",
        )
        for c in comms:
            propio = c.sent_or_received == "Received"
            mensajes.append({
                "de": "tu" if propio else "admin",
                "autor": "Tú" if propio else "Administración",
                "fecha": fecha_txt(c.creation),
                "html": sanitize_html(c.content or ""),
            })
        context.update({
            "title": f"Caso #{t.name} · Condominio Los Cedros",
            "caso": frappe._dict(
                numero=t.name,
                asunto=titulo_residente(t.subject, t.get("ticket_type")),
                categoria=t.get("ticket_type") or "",
                abierto_el=fecha_txt(t.opening_date or t.creation),
                estado=estado_info(t.status),
                cerrado=t.status == "Closed",
                fotos=frappe.db.count("File", {"attached_to_doctype": "HD Ticket", "attached_to_name": t.name}),
            ),
            "mensajes": mensajes,
        })
    else:
        filas = frappe.get_all(
            "HD Ticket",
            or_filters={"raised_by": email, "owner": user},
            fields=["name", "subject", "status", "ticket_type", "creation", "modified"],
            order_by="modified desc",
            limit_page_length=100,
        )
        casos = []
        for r in filas:
            casos.append(frappe._dict(
                numero=r.name,
                asunto=titulo_residente(r.subject, r.ticket_type),
                categoria=r.ticket_type or "",
                fecha=fecha_txt(r.creation),
                actualizado=fecha_txt(r.modified),
                estado=estado_info(r.status),
            ))
        context.update({
            "caso": None,
            "title": "Mis reportes · Condominio Los Cedros",
            "abiertos": [c for c in casos if c.estado.abierto],
            "cerrados": [c for c in casos if not c.estado.abierto],
        })

    context.data_json = json.dumps({"csrf": context.csrf_token, "caso": caso or None},
                                   ensure_ascii=False).replace("</", "<\\/")
    return context
