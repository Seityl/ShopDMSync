import frappe
from frappe import _
from .sync_table import sync_table, load_table 

@frappe.whitelist()
def load_item_update_table():
    load_table()
    
@frappe.whitelist()
def sync_item_update_table():
    shopdm_settings = frappe.get_doc("ShopDM Sync", "ShopDM Sync")

    min_quantity = int(shopdm_settings.min_quantity)
    price_list = shopdm_settings.price_list
    warehouse = shopdm_settings.warehouse

    if min_quantity and price_list and warehouse:
        sync_table(min_quantity, warehouse, price_list)

@frappe.whitelist()
def is_table_loaded():
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')
    item_update_table = shopdm_doc.item_update_table   

    if shopdm_doc.shopdm_csv and item_update_table:
        shopdm_doc.is_table_loaded = True
        shopdm_doc.save()
        frappe.db.commit()

    elif not shopdm_doc.shopdm_csv or not item_update_table:    
        shopdm_doc.is_table_loaded = False
        shopdm_doc.save()
        frappe.db.commit()