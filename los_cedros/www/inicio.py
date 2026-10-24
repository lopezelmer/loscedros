import json

import frappe

from los_cedros.utils import categorias_publicas
from frappe.utils import add_days, getdate, to_timedelta, today

no_cache = 1

CAT_KEY = {"Obras": "obras", "Administración": "admin", "Comunidad": "comunidad", "Seguridad": "seguridad"}
DIAS_JS = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]  # Date.getDay()
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _horas(t):
    return round(to_timedelta(t).total_seconds() / 3600, 2)


def _hora_txt(h):
    hh, mm = int(h), int(round((h - int(h)) * 60))
    h12 = (hh - 1) % 12 + 1
    return f"{h12}:{mm:02d}" if mm else str(h12)


def get_context(context):
    cfg = frappe.get_single("Configuracion Sitio")
    hoy = getdate(today())

    avisos = frappe.get_all(
        "Aviso Comunidad",
        filters={"publicado": 1},
        or_filters=[["mostrar_hasta", "is", "not set"], ["mostrar_hasta", ">=", hoy]],
        fields=["titulo", "categoria", "fecha", "resumen", "detalle_titulo", "detalle"],
        order_by="fecha desc, creation desc",
        limit_page_length=40,
    )
    for a in avisos:
        a.k = CAT_KEY.get(a.categoria, "comunidad")
        a.fecha_txt = f"{a.fecha.day} {MESES[a.fecha.month - 1]} {a.fecha.year}"

    eventos = frappe.get_all(
        "Evento Comunidad",
        filters={"publicado": 1, "fecha": [">=", add_days(hoy, -14)]},
        fields=["titulo", "fecha", "detalle"],
        order_by="fecha asc",
        limit_page_length=40,
    )

    miembros = frappe.get_all("Miembro Junta", filters={"activo": 1}, fields=["nombre", "cargo"],
                              order_by="orden asc, nombre asc")
    for m in miembros:
        m.iniciales = "".join(p[0] for p in m.nombre.split()[:2]).upper()

    faqs = frappe.get_all("Pregunta Frecuente", filters={"publicado": 1}, fields=["pregunta", "respuesta"],
                          order_by="orden asc, creation asc")

    horario = []
    for r in cfg.horario_oficina:
        if r.dia in DIAS_JS and r.desde and r.hasta:
            horario.append({"d": DIAS_JS.index(r.dia), "a": _horas(r.desde), "b": _horas(r.hasta), "dia": r.dia})
    horario.sort(key=lambda x: ((x["d"] + 6) % 7, x["a"]))
    horario_txt = " · ".join(f"{h['dia'][:3]} {_hora_txt(h['a'])}–{_hora_txt(h['b'])}" for h in horario)
    dias_txt = ", ".join(h["dia"][:3].lower() for h in horario)

    categorias = categorias_publicas()

    data = {
        "categorias": [{"n": c.nombre, "t": c.titulo, "p": c.tiempo, "l": c.sugerencias} for c in categorias],
        "eventos": [{"f": str(e.fecha), "t": e.titulo, "s": e.detalle or ""} for e in eventos],
        "horario": [{"d": h["d"], "a": h["a"], "b": h["b"]} for h in horario],
        "diasPago": dias_txt,
        "venc": cfg.dia_vencimiento or 1,
        "limite": cfg.dia_limite or 16,
    }

    context.update({
        "no_cache": 1,
        "title": "Condominio Los Cedros",
        "cfg": cfg,
        "portal": cfg.url_portal or "/mis-reportes",
        "categorias": categorias,
        "portada": cfg.imagen_portada or "/assets/los_cedros/images/portada.jpg",
        "avisos": avisos,
        "miembros": miembros,
        "faqs": faqs,
        "horario_txt": horario_txt,
        "data_json": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
    })
    return context
