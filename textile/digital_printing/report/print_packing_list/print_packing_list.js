// Copyright (c) 2023, ParaLogic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Print Packing List"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			"fieldname":"print_order",
			"label": __("Print Order"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				let filters = {
					company: frappe.query_report.get_filter_value("company")
				}
				customer = frappe.query_report.get_filter_value("customer");
				if (customer) {
					filters.customer = customer;
				}
				return frappe.db.get_link_options('Print Order', txt, filters);
			}
		},
		{
			fieldname: "packing_slip",
			label: __("Package"),
			fieldtype: "Link",
			options: "Packing Slip",
		},
		{
			fieldname: "package_type",
			label: __("Package Type"),
			fieldtype: "Link",
			options: "Package Type",
		},
		{
			fieldname: "process_item",
			label: __("Print Process"),
			fieldtype: "Link",
			options: "Item",
			get_query: function() {
				return {
					query: "erpnext.controllers.queries.item_query",
					filters: {
						'textile_item_type': "Print Process"
					}
				};
			},
		},
		{
			fieldname: "fabric_item",
			label: __("Fabric Item"),
			fieldtype: "Link",
			options: "Item",
			get_query: function() {
				return {
					query: "erpnext.controllers.queries.item_query",
					filters: {
						'textile_item_type': "Ready Fabric"
					}
				};
			},
		},
		{
			fieldname: "fabric_material",
			label: __("Fabric Material"),
			fieldtype: "Link",
			options: "Fabric Material",
		},
		{
			fieldname: "fabric_type",
			label: __("Fabric Type"),
			fieldtype: "Link",
			options: "Fabric Type",
		},
		{
			"fieldname":"show_delivered",
			"label": __("Show Delivered"),
			"fieldtype": "Check"
		},
	]
};