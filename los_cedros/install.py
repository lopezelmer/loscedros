import frappe
from frappe.utils import add_days, today


def before_install():
    if not frappe.db.exists("Role", "Editor Sitio"):
        frappe.get_doc({"doctype": "Role", "role_name": "Editor Sitio", "desk_access": 1}).insert(
            ignore_permissions=True
        )


def after_install():
    seed()
    preparar_portal()


def after_migrate():
    preparar_portal()


def seed():
    """Contenido inicial de ejemplo. Solo se crea si las tablas estan vacias."""
    cfg = frappe.get_single("Configuracion Sitio")
    if not cfg.telefono:
        cfg.update({
            "boletin_periodo": "Octubre – Diciembre 2026",
            "aviso_estado": "Obras: instalación Teleentry en el portón",
            "url_portal": "/mis-reportes",
            "mensaje_titulo": "Gracias por un trimestre de mucho trabajo",
            "mensaje_junta": "Este año trajo apagones, una temporada de huracanes activa y varias obras "
                             "en el complejo. Como comunidad las hemos asumido con paciencia. Sigamos "
                             "siendo considerados los unos con los otros.",
            "mensaje_firma": "Junta de Directores",
            "telefono": "787-555-0142",
            "correo": "administracion@loscedros.example",
            "dia_vencimiento": 1,
            "dia_limite": 16,
        })
        cfg.set("horario_oficina", [])
        for dia, desde, hasta in (("Martes", "08:00:00", "12:00:00"),
                                  ("Miércoles", "12:00:00", "16:00:00"),
                                  ("Jueves", "08:00:00", "12:00:00")):
            cfg.append("horario_oficina", {"dia": dia, "desde": desde, "hasta": hasta})
        cfg.save(ignore_permissions=True)

    hoy = today()
    if not frappe.db.count("Aviso Comunidad"):
        avisos = [
            ("Obras", -4, "Nuevo sistema Teleentry en el portón",
             "Ya está instalado el intercomunicador en la entrada. Las visitas marcan tu número de "
             "apartamento y abres el portón desde tu teléfono.",
             "Cómo registrarte",
             "Pasa por la Oficina con tu número de teléfono. Cada apartamento puede registrar hasta dos números."),
            ("Obras", -8, "Sellado de techos, edificios C y D",
             "El contratista trabajará en los techos de 8:00 a.m. a 4:00 p.m. Habrá materiales en el "
             "estacionamiento posterior.",
             "Qué debes hacer",
             "Cierra las ventanas de los pisos superiores durante el trabajo y no estaciones frente a la "
             "escalera posterior de esos edificios."),
            ("Administración", -11, "Renovación de la póliza de seguro",
             "La póliza del condominio cubre las áreas comunes generales y limitadas. Cada titular es "
             "responsable de asegurar su apartamento y contenido.",
             "Más detalles",
             "La Junta presentará las cotizaciones en la próxima asamblea de titulares."),
            ("Comunidad", -14, "Mantenimiento de áreas verdes",
             "Terminó la siembra de plantas y la colocación de piedra decorativa en la entrada. El corte "
             "de grama sigue los martes cada dos semanas.",
             "Pedido de la Junta",
             "No dejes bicicletas ni macetas sobre la grama los días de corte para evitar daños."),
            ("Comunidad", -18, "Control de palomas",
             "El problema de palomas se ha reducido bastante y la compañía garantiza su trabajo. Si ves "
             "palomas en tu alero, repórtalo en el Portal con fotos.",
             "Cómo reportarlo",
             "Usa la categoría «Palomas / Plagas», indica edificio y piso, y adjunta una foto del alero."),
            ("Seguridad", -26, "Portón y visitantes",
             "No abras el portón peatonal a personas que no conoces. Las entregas se reciben en la caseta "
             "o se coordinan por Teleentry.",
             "Recordatorio",
             "Reporta cualquier daño en el portón o las luces del perímetro en el Portal de Residentes."),
        ]
        for cat, dias, titulo, resumen, dt, det in avisos:
            frappe.get_doc({"doctype": "Aviso Comunidad", "categoria": cat, "fecha": add_days(hoy, dias),
                            "titulo": titulo, "resumen": resumen, "detalle_titulo": dt, "detalle": det,
                            "publicado": 1}).insert(ignore_permissions=True)

    if not frappe.db.count("Evento Comunidad"):
        for dias, titulo, detalle in (
            (4, "Fumigación de áreas comunes", "Pasillos y cuarto de basura · 9:00 a.m."),
            (15, "Último día de registro Teleentry", "En la Oficina"),
            (17, "Inicia sellado de techos C y D", "Dos semanas, de 8:00 a.m. a 4:00 p.m."),
            (22, "Prueba del generador", "Corte breve de 10 minutos · 10:00 a.m."),
            (34, "Asamblea anual de titulares", "Salón de actividades · 7:00 p.m."),
            (50, "Limpieza de cisternas", "Sin agua de 9:00 a.m. a 1:00 p.m."),
            (57, "Encendido navideño", "Área de la entrada · 6:30 p.m."),
        ):
            frappe.get_doc({"doctype": "Evento Comunidad", "fecha": add_days(hoy, dias), "titulo": titulo,
                            "detalle": detalle, "publicado": 1}).insert(ignore_permissions=True)

    if not frappe.db.count("Miembro Junta"):
        for orden, nombre, cargo in ((1, "Ana Rivera", "Presidenta"), (2, "Luis Torres", "Tesorero"),
                                     (3, "Marta Santiago", "Secretaria"),
                                     (9, "Oficina de Administración", "Lun–Vie 8:00–4:00")):
            frappe.get_doc({"doctype": "Miembro Junta", "nombre": nombre, "cargo": cargo, "orden": orden,
                            "activo": 1}).insert(ignore_permissions=True)

    if not frappe.db.count("Pregunta Frecuente"):
        for orden, p, r in (
            (1, "¿Cómo sé si mi reporte fue recibido?",
             "Al crear el boleto en el Portal recibes un número de caso. Puedes ver el estado (abierto, en "
             "progreso, resuelto) entrando con tu usuario."),
            (2, "No tengo usuario para el Portal. ¿Qué hago?",
             "Solicítalo en la Oficina con tu número de apartamento y un correo electrónico."),
            (3, "¿Puedo reportar algo dentro de mi apartamento?",
             "Sí, cuando afecta a otras unidades o a áreas comunes, como una filtración que viene del piso "
             "de arriba. Las reparaciones privadas son responsabilidad del titular."),
            (4, "¿Dónde veo los boletines anteriores?",
             "La Oficina tiene copia de cada boletín trimestral. Este sitio muestra siempre los avisos vigentes."),
        ):
            frappe.get_doc({"doctype": "Pregunta Frecuente", "pregunta": p, "respuesta": r, "orden": orden,
                            "publicado": 1}).insert(ignore_permissions=True)

    frappe.db.commit()


# ------------------------------------------------------------------ Portal de Residentes (v1.1)
PRIORIDADES = ("Low", "Medium", "High", "Urgent")

CATEGORIAS = [
    # (orden, nombre, icono, prioridad, descripcion corta, tiempo, sugerencias, aviso, campos)
    (1, "Mantenimiento", "herramienta", "Medium",
     "Algo roto o que no funciona en áreas comunes",
     "Respuesta típica: 2–3 días laborables",
     ["Edificio y lugar exacto", "Qué pasa y desde cuándo", "Una o dos fotos"], "",
     [("Lugar exacto (pasillo, escalera, estacionamiento…)", "Texto", "", 1)]),
    (2, "Agua y filtraciones", "agua", "High",
     "Filtraciones, presión de agua o cisternas",
     "Prioridad alta: atención el mismo día",
     ["Si el agua está saliendo ahora o es una mancha", "Apartamento de arriba, si aplica", "Fotos del área mojada"], "",
     [("¿El agua sigue saliendo?", "Sí/No", "", 1), ("Apartamento de arriba, si aplica", "Texto", "", 0)]),
    (3, "Electricidad", "rayo", "High",
     "Luces de áreas comunes, generador o paneles",
     "Prioridad alta en pasillos y escaleras",
     ["Ubicación de la luz o equipo", "Hora en que lo notaste"], "",
     [("Alcance", "Opciones", "Todo el edificio\nUn área o pasillo\nUn equipo específico", 1)]),
    (4, "Seguridad y portón", "escudo", "High",
     "Portón, Teleentry, cámaras o cerca perimetral",
     "Prioridad alta: atención el mismo día",
     ["Qué equipo falla", "Hora del incidente", "No incluyas datos personales de otras personas"], "",
     [("Equipo afectado", "Opciones",
       "Portón vehicular\nPortón peatonal\nTeleentry o intercomunicador\nCámaras\nCerca o luces del perímetro\nOtro", 1),
      ("Hora aproximada", "Texto", "", 0)]),
    (5, "Palomas y plagas", "plaga", "Low",
     "Palomas en aleros, abejas, roedores o insectos",
     "Respuesta típica: 3–5 días laborables",
     ["Edificio, piso y lado del edificio", "Fotos, si es seguro tomarlas"], "",
     [("Tipo", "Opciones", "Palomas\nAbejas o avispas\nRoedores\nInsectos\nOtro", 1),
      ("Piso y lado del edificio", "Texto", "", 0)]),
    (6, "Ruido y convivencia", "ruido", "Low",
     "Ruido, mascotas, estacionamiento o basura",
     "La Administración contacta al residente",
     ["Fecha y hora", "Lugar aproximado", "Describe lo que pasó, sin acusaciones"], "",
     [("Fecha y hora", "Texto", "", 1), ("Lugar aproximado", "Texto", "", 0)]),
    (7, "Áreas recreativas", "parque", "Medium",
     "Piscina, salón de actividades, parque, gazebo o cancha",
     "Respuesta típica: 3–5 días laborables",
     ["Qué área y qué equipo", "Si representa un riesgo para niños", "Fotos"], "",
     [("Área", "Opciones",
       "Piscina\nSalón de actividades\nParque infantil\nGazebo\nCancha\nGimnasio\nOtra", 1),
      ("¿Representa un riesgo de seguridad?", "Sí/No", "", 1)]),
    (8, "Administración y cuotas", "factura", "Medium",
     "Pagos, estado de cuenta, recibos y certificaciones",
     "La Oficina responde en 1–2 días laborables",
     ["Mes o pago al que te refieres", "Número de recibo, si lo tienes"],
     "No incluyas números de tarjeta ni de cuenta bancaria.",
     [("Tema", "Opciones",
       "Pago o recibo\nEstado de cuenta\nCertificación de deuda\nPlan de pago\nDocumentos del condominio\nOtro", 1)]),
    (9, "Otros", "otro", "Low",
     "Cualquier otra situación del condominio",
     "Respuesta típica: 2–3 días laborables",
     ["Qué pasa y dónde", "Fotos, si ayudan"], "", []),
]


def preparar_portal():
    """Idempotente: prioridades, categorias de ejemplo y tipos de ticket en Helpdesk."""
    if not frappe.db.exists("DocType", "HD Ticket Type"):
        return
    for p in PRIORIDADES:
        if not frappe.db.exists("HD Ticket Priority", p):
            try:
                frappe.get_doc({"doctype": "HD Ticket Priority"}).insert(ignore_permissions=True, set_name=p)
            except Exception:
                frappe.log_error(title=f"Los Cedros: no se pudo crear la prioridad {p}")

    if not frappe.db.count("Categoria Reporte"):
        for orden, nombre, icono, prio, titulo, tiempo, sug, aviso, campos in CATEGORIAS:
            if not frappe.db.exists("HD Ticket Priority", prio):
                prio = frappe.db.get_value("HD Ticket Priority", {}, "name")
            frappe.get_doc({
                "doctype": "Categoria Reporte", "nombre": nombre, "orden": orden, "activo": 1,
                "icono": icono, "prioridad": prio, "titulo": titulo, "tiempo_respuesta": tiempo,
                "sugerencias": "\n".join(sug), "aviso": aviso,
                "campos": [{"etiqueta": e, "tipo": t, "opciones": o, "obligatorio": q} for e, t, o, q in campos],
            }).insert(ignore_permissions=True)  # on_update crea el tipo de ticket
    else:
        for n in frappe.get_all("Categoria Reporte", pluck="name"):
            sincronizar_tipo(frappe.get_doc("Categoria Reporte", n))
    frappe.db.commit()


def sincronizar_tipo(cat):
    """Cada categoria existe como HD Ticket Type con su prioridad por defecto."""
    if not frappe.db.exists("DocType", "HD Ticket Type"):
        return
    meta = frappe.get_meta("HD Ticket Type")
    valores = {}
    if meta.has_field("priority") and cat.prioridad:
        valores["priority"] = cat.prioridad
    if meta.has_field("description") and cat.titulo:
        valores["description"] = cat.titulo
    if frappe.db.exists("HD Ticket Type", cat.name):
        if valores:
            frappe.db.set_value("HD Ticket Type", cat.name, valores)
    else:
        frappe.get_doc({"doctype": "HD Ticket Type", **valores}).insert(
            ignore_permissions=True, set_name=cat.name)
