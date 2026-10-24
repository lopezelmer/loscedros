# Copyright (c) 2026, Condominio Los Cedros

import frappe
from frappe.model.document import Document


class AvisoComunidad(Document):
	def validate(self):
		if self.mostrar_hasta and self.fecha and str(self.mostrar_hasta) < str(self.fecha):
			frappe.throw("'Mostrar hasta' no puede ser antes de la fecha del aviso.")
