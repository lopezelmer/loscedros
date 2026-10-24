import frappe


def execute():
    """v1.2: quitar «Login with Email Link».

    Con la opcion apagada, Frappe tampoco envia enlaces aunque alguien llame
    directamente a frappe.www.login.send_login_link.
    """
    if frappe.db.get_single_value("System Settings", "login_with_email_link"):
        frappe.db.set_single_value("System Settings", "login_with_email_link", 0)
        frappe.clear_cache()
