# Copyright (c) 2026, Condominio Los Cedros

import frappe
from frappe.model.document import Document


class CategoriaReporte(Document):
	def validate(self):
		for c in self.campos:
			if c.tipo == "Opciones" and not (c.opciones or "").strip():
				frappe.throw(f"El campo «{c.etiqueta}» necesita al menos una opción.")

	def on_update(self):
		from los_cedros.install import sincronizar_tipo

		sincronizar_tipo(self)
