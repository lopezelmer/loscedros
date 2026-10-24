import json

import frappe

from los_cedros.utils import categorias_publicas, contexto_portal

no_cache = 1


def get_context(context):
    contexto_portal(context, "/reportar", "reportar")
    cats = categorias_publicas()
    res = frappe.db.get_value(
        "Residente", frappe.session.user,
        ["edificio", "apartamento", "telefono", "contacto_preferido", "verificado"], as_dict=True,
    ) or {}

    pedida = (frappe.form_dict.get("categoria") or "").strip()
    inicial = next((i for i, c in enumerate(cats) if c.nombre == pedida), -1)

    data = {
        "csrf": context.csrf_token,
        "inicial": inicial,
        "categorias": [
            {"n": c.nombre, "t": c.titulo, "p": c.tiempo, "a": c.aviso, "l": c.sugerencias,
             "i": c.icono_svg, "campos": c.campos}
            for c in cats
        ],
        "residente": {
            "edificio": res.get("edificio") or "",
            "apartamento": res.get("apartamento") or "",
            "telefono": res.get("telefono") or "",
            "contacto": res.get("contacto_preferido") or "Correo",
            "verificado": bool(res.get("verificado")),
        },
    }
    context.update({
        "title": "Reportar una situación · Condominio Los Cedros",
        "categorias": cats,
        "data_json": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
    })
    return context
