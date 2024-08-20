import frappe
from frappe import _
from .sync_table import update_table 

@frappe.whitelist()
def sync_table():
    shopdm_settings = frappe.get_doc("ShopDM Sync", "ShopDM Sync")

    min_quantity = shopdm_settings.min_quantity
    price_list = shopdm_settings.price_list
    warehouse = shopdm_settings.warehouse

    update_table(min_quantity, price_list, warehouse)
