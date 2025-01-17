import frappe
# from frappe import _
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from textile.fabric_printing.doctype.print_order.print_order import validate_transaction_against_print_order
from textile.fabric_pretreatment.doctype.pretreatment_order.pretreatment_order import validate_transaction_against_pretreatment_order


class SalesOrderDP(SalesOrder):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.force_item_fields += ["fabric_item", "fabric_item_name", "textile_item_type"]

	def validate_with_previous_doc(self):
		super().validate_with_previous_doc()
		validate_transaction_against_pretreatment_order(self)
		validate_transaction_against_print_order(self)

	def update_previous_doc_status(self):
		super().update_previous_doc_status()

		pretreatment_orders = set([d.pretreatment_order for d in self.items if d.get('pretreatment_order')])
		if not frappe.flags.skip_pretreatment_order_status_update:
			for name in pretreatment_orders:
				doc = frappe.get_doc("Pretreatment Order", name)
				doc.set_sales_order_status(update=True)
				doc.set_production_packing_status(update=True)
				doc.validate_ordered_qty(from_doctype=self.doctype)
				doc.set_status(update=True)
				doc.notify_update()

		print_orders = []
		if not frappe.flags.skip_print_order_status_update:
			print_orders = set([d.print_order for d in self.items if d.get('print_order')])
			print_order_row_names = [d.print_order_item for d in self.items if d.get('print_order_item')]

		for name in print_orders:
			doc = frappe.get_doc("Print Order", name)
			doc.set_sales_order_status(update=True)
			doc.set_production_packing_status(update=True)
			doc.validate_ordered_qty(from_doctype=self.doctype, row_names=print_order_row_names)
			doc.set_status(update=True)
			doc.notify_update()

	def update_status(self, status):
		super().update_status(status)

		pretreatment_orders = set([d.pretreatment_order for d in self.items if d.get('pretreatment_order')])
		for name in pretreatment_orders:
			doc = frappe.get_doc("Pretreatment Order", name)
			doc.run_method("update_status", None)

		print_orders = set([d.print_order for d in self.items if d.get('print_order')])
		for name in print_orders:
			doc = frappe.get_doc("Print Order", name)
			doc.run_method("update_status", None)

	def get_sales_order_item_bom(self, row):
		if row.get('pretreatment_order'):
			return frappe.db.get_value("Pretreatment Order", row.pretreatment_order, "ready_fabric_bom", cache=1)
		if row.get('print_order_item'):
			return frappe.db.get_value("Print Order Item", row.print_order_item, "design_bom", cache=1)

		return super().get_sales_order_item_bom(row)

	def get_skip_delivery_note(self, row):
		if row.get("pretreatment_order"):
			delivery_required = frappe.db.get_value("Pretreatment Order", row.pretreatment_order, "delivery_required", cache=1)
			if not delivery_required:
				return True

		return super().get_skip_delivery_note(row)


def override_sales_order_dashboard(data):
	from textile.utils import override_sales_transaction_dashboard
	return override_sales_transaction_dashboard(data)


def update_sales_order_mapper(mapper, target_doctype):
	if not mapper.get("Sales Order Item"):
		return

	field_map = mapper["Sales Order Item"]["field_map"]

	field_map["pretreatment_order"] = "pretreatment_order"

	field_map["print_order"] = "print_order"
	field_map["print_order_item"] = "print_order_item"


def sales_order_autoname(doc, method):
	print_orders = set()
	pretreatment_orders = set()

	for d in doc.get("items"):
		if d.get("pretreatment_order"):
			pretreatment_orders.add(d.pretreatment_order)
		if d.get("print_order"):
			print_orders.add(d.print_order)

	name = None
	if len(print_orders) == 1:
		name = list(print_orders)[0]
	elif len(pretreatment_orders) == 1:
		name = list(pretreatment_orders)[0]

	if name and not frappe.db.exists("Sales Order", name):
		doc.name = name
