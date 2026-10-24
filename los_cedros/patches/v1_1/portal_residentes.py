import frappe


def execute():
    """v1.1: el boton Portal de Residentes ahora abre /mis-reportes (antes /helpdesk)."""
    if not frappe.db.exists("DocType", "Configuracion Sitio"):
        return
    actual = frappe.db.get_single_value("Configuracion Sitio", "url_portal")
    if actual in (None, "", "/helpdesk", "/helpdesk/"):
        frappe.db.set_single_value("Configuracion Sitio", "url_portal", "/mis-reportes")
