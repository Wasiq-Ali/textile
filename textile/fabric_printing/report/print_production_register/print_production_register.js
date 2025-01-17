// Copyright (c) 2023, ParaLogic and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.provide("textile");

textile.group_field_opts_printpr = [
	"",
	"Group by Customer",
	"Group by Fabric Item",
	"Group by Print Order",
	"Group by Process Item",
	"Group by Fabric Printer",
]

frappe.query_reports["Print Production Register"] = {
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
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1
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
			fieldname: "softener_item",
			label: __("Softener Item"),
			fieldtype: "Link",
			options: "Item",
			get_query: function() {
				return {
					query: "erpnext.controllers.queries.item_query",
					filters: {
						'textile_item_type': "Process Component",
						'process_component': "Softener",
					}
				};
			},
		},
		{
			"fieldname":"fabric_printer",
			"label": __("Fabric Printer"),
			"fieldtype": "Link",
			"options": "Fabric Printer",
			get_query: function() {
				let process_item = frappe.query_report.get_filter_value("process_item");
				let filters = process_item ? {process_item: process_item} : {}
				return {
					filters: filters
				}
			},
		},
		{
			fieldname: "group_by_1",
			label: __("Group By Level 1"),
			fieldtype: "Select",
			options: textile.group_field_opts_printpr,
			default: "Group by Process Item"
		},
		{
			fieldname: "group_by_2",
			label: __("Group By Level 2"),
			fieldtype: "Select",
			options: textile.group_field_opts_printpr,
			default: "Group by Fabric Printer"
		},
		{
			fieldname: "group_by_3",
			label: __("Group By Level 3"),
			fieldtype: "Select",
			options: textile.group_field_opts_printpr,
			default: ""
		},
		{
			fieldname: "totals_only",
			label: __("Group Totals Only"),
			fieldtype: "Check",
		},
	],
	initial_depth: 2
};
