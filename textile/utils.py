import frappe
from frappe import _
from frappe.utils import cint, flt
from textile.rotated_image import get_rotated_image  # do not remove import

printing_components = {
	"coating_item": "Coating",
	"softener_item": "Softener",
	"sublimation_paper_item": "Sublimation Paper",
	"protection_paper_item": "Protection Paper",
}

pretreatment_components = {
	"singeing_item": "Singeing",
	"desizing_item": "Desizing",
	"bleaching_item": "Bleaching",
}

process_components = {**printing_components, **pretreatment_components}


def validate_textile_item(item_code, textile_item_type, process_component=None):
	item = frappe.get_cached_doc("Item", item_code)

	if textile_item_type:
		if item.textile_item_type != textile_item_type:
			frappe.throw(_("{0} is not a {1} Item").format(frappe.bold(item_code), textile_item_type))

		if textile_item_type == "Process Component" and process_component:
			if item.process_component != process_component:
				frappe.throw(_("{0} is not a {1} Component Item").format(frappe.bold(item_code), process_component))

	from erpnext.stock.doctype.item.item import validate_end_of_life
	validate_end_of_life(item.name, item.end_of_life, item.disabled)


def gsm_to_grams(gsm, width_inch, length_meter=1):
	width_meter = flt(width_inch) * 0.0254
	return flt(gsm) * width_meter * flt(length_meter)


def is_row_return_fabric(doc, row):
	if row.get("print_order"):
		print_order_fabric = frappe.db.get_value("Print Order", row.print_order, "fabric_item", cache=1)
		return cint(row.item_code == print_order_fabric)
	elif row.get("pretreatment_order"):
		greige_fabric_item = frappe.db.get_value("Pretreatment Order", row.pretreatment_order, "greige_fabric_item", cache=1)
		return cint(row.item_code == greige_fabric_item)
	elif row.get("item_code"):
		item_details = frappe.get_cached_value("Item", row.item_code, ["textile_item_type", "is_customer_provided_item", "customer"], as_dict=1)
		return cint(
			item_details.textile_item_type in ("Greige Fabric", "Ready Fabric")
			and item_details.is_customer_provided_item
			and doc.customer == item_details.customer
		)
	else:
		return 0


@frappe.whitelist()
def get_fabric_item_details(fabric_item):
	out = frappe._dict()

	fabric_doc = frappe.get_cached_doc("Item", fabric_item) if fabric_item else frappe._dict()
	out.fabric_item_name = fabric_doc.item_name
	out.fabric_material = fabric_doc.fabric_material
	out.fabric_type = fabric_doc.fabric_type
	out.fabric_width = fabric_doc.fabric_width
	out.fabric_gsm = fabric_doc.fabric_gsm
	out.fabric_construction = fabric_doc.fabric_construction
	out.fabric_per_pickup = fabric_doc.fabric_per_pickup

	return out


@frappe.whitelist()
def is_internal_customer(customer, company):
	if not customer or not company:
		return 0

	customer_doc = frappe.get_cached_doc("Customer", customer)
	if not customer_doc.is_internal_customer or not customer_doc.represents_company:
		return 0

	return cint(customer_doc.represents_company == company)


def get_combined_fabric_items(fabric_item, combine_greige_ready=True, combine_ready_printed=True):
	out = frappe._dict({
		"textile_item_type": frappe.db.get_value("Item", fabric_item, "textile_item_type", cache=1),
		"greige_fabric_items": [],
		"ready_fabric_items": [],
		"printed_fabric_items": [],
	})

	if out.textile_item_type == "Greige Fabric":
		out.greige_fabric_items = [fabric_item]

		if combine_greige_ready:
			out.ready_fabric_items = frappe.get_all("Item", filters={
				"fabric_item": fabric_item, "textile_item_type": "Ready Fabric"
			}, pluck="name")

	elif out.textile_item_type == "Ready Fabric":
		out.ready_fabric_items = [fabric_item]

		if combine_greige_ready:
			out.greige_fabric_item = frappe.db.get_value("Item", fabric_item, "fabric_item", cache=1)
			if out.greige_fabric_item:
				out.greige_fabric_items = [out.greige_fabric_item]

	if out.ready_fabric_items and combine_ready_printed:
		out.printed_fabric_items = frappe.get_all("Item", filters={
			"textile_item_type": "Printed Design", "fabric_item": ("in", out.ready_fabric_items)
		}, pluck="name")

	out.fabric_item_codes = list(set(out.greige_fabric_items + out.ready_fabric_items + out.printed_fabric_items))
	return out


def get_yard_to_meter():
	return get_textile_conversion_factors()["yard_to_meter"]


def get_textile_conversion_factors():
	return {
		"inch_to_meter": flt(frappe.db.get_default("inch_to_meter")) or 0.0254,
		"yard_to_meter": flt(frappe.db.get_default("yard_to_meter")) or 0.9144,
		"meter_to_meter": 1
	}


def update_conversion_factor_global_defaults():
	from erpnext.setup.doctype.uom_conversion_factor.uom_conversion_factor import get_uom_conv_factor
	inch_to_meter = get_uom_conv_factor("Inch", "Meter")
	yard_to_meter = get_uom_conv_factor("Yard", "Meter")

	frappe.db.set_default("inch_to_meter", inch_to_meter)
	frappe.db.set_default("yard_to_meter", yard_to_meter)


def override_sales_transaction_dashboard(data):
	data["internal_links"]["Pretreatment Order"] = ["items", "pretreatment_order"]
	data["internal_links"]["Print Order"] = ["items", "print_order"]

	textile_items = ["Pretreatment Order", "Print Order"]

	ref_section = [d for d in data["transactions"] if d["label"] == _("Textile")]
	if ref_section:
		ref_section = ref_section[0]
		ref_section["items"] = textile_items + ref_section["items"]
	else:
		data["transactions"].append({
			"label": _("Textile"),
			"items": textile_items
		})

	return data
