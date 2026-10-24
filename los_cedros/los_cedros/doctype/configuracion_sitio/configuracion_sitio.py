# Copyright (c) 2026, Condominio Los Cedros

import frappe
from frappe.model.document import Document


class ConfiguracionSitio(Document):
	def validate(self):
		for campo in ("dia_vencimiento", "dia_limite"):
			if not 1 <= (self.get(campo) or 0) <= 28:
				frappe.throw("Los dias de cuota deben estar entre 1 y 28.")
		if self.dia_limite < self.dia_vencimiento:
			frappe.throw("El dia limite sin recargo debe ser igual o despues del dia de vencimiento.")
		for r in self.horario_oficina:
			if r.desde and r.hasta and str(r.hasta) <= str(r.desde):
				frappe.throw(f"Horario de {r.dia}: la hora final debe ser despues de la inicial.")
