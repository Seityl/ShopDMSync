import io
import csv
import json
import frappe
import requests
from frappe import _
from frappe.model.document import Document
from erpnext.stock.utils import get_bin
from frappe.utils import cint
from datetime import datetime

def load_table():
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')
    shopdm_csv = get_shopdm_csv()

    if shopdm_csv:      
        item_data = get_item_data_from_csv(shopdm_csv)

        for item in item_data:
            shopdm_doc.append('item_update_table', {
                'item_no': item['ITEM_NO'],
                'description': item['DESCRIPTION'],
                'category': item['CATEGORY'],
                'price': item['PRICE'],
                'quantity': item['QUANTITY']
            })

    shopdm_doc.save()
    frappe.db.commit()

def sync_table(min_quantity, warehouse, price_list):
    update_item_quantities(warehouse, min_quantity) 
    update_item_prices(price_list)
    create_updated_table_csv()

def get_current_date():
    now = datetime.now()    
    current_date = now.strftime("%d_%m_%Y")
    
    return current_date

def get_item_price_from_price_list(price_list, item):
    if price_list and item:
        item_code = item['item_no']
        if is_item_exists(item_code) and is_item_price_exists(item_code, price_list):
            values = {
            'item_code': item_code,
            'price_list': price_list
            }

            if values:
                item_price = frappe.db.sql("""
                    SELECT
                        `price_list_rate`
                    FROM `tabItem Price`
                    WHERE `item_code` = %(item_code)s
                        AND `price_list` = %(price_list)s
                """, values=values, as_dict=1)[0]['price_list_rate']
                    
                if item_price:
                    return item_price
                else:
                    return

def get_quantity_from_warehouse(warehouse, item, min_quantity):
    if warehouse and item:
        item_code = item['item_no']

        if is_item_exists(item_code):
            bin = get_bin(item_code, warehouse)
            actual_qty = bin.actual_qty
            reserved_qty = bin.reserved_qty
            qty = cint(actual_qty - reserved_qty)

            if qty > min_quantity:
                return qty
            
            else:
                return 0

def get_item_update_table_data():
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')
    item_update_table = shopdm_doc.item_update_table    

    item_update_table_data = []

    for item in item_update_table:
        item_data = {
            'item_no': item.item_no,
            'description': item.description,
            'category': item.category,
            'price': item.price,
            'quantity': item.quantity
        }

        item_update_table_data.append(item_data)
    
    return item_update_table_data

def get_item_data_from_csv(csv):
    csv_url = csv['file_url']
    full_path = get_absolute_path(csv_url)
    item_data = csv_to_json(full_path)

    return item_data

#TODO: Fix private file location
def get_absolute_path(file_name):
	if(file_name.startswith('/files/')):
		file_path = f'{frappe.utils.get_bench_path()}/sites/{frappe.utils.get_site_base_path()[2:]}/public{file_name}'

	if(file_name.startswith('/private/')):
		file_path = f'{frappe.utils.get_bench_path()}/sites/{frappe.utils.get_site_base_path()[2:]}{file_name}'

	return file_path

def get_shopdm_csv():    
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')

    if shopdm_doc.shopdm_csv:
        shopdm_csv = frappe.get_all('File', 
            filters={
            'attached_to_doctype': 'ShopDM Sync', 
            'attached_to_name': 'ShopDM Sync'
            }, 
            fields=[
                'file_url',
                'file_name',
                'file_type'
            ]
        )[0]

        if shopdm_csv['file_type'] == 'CSV':
            return shopdm_csv

        else:
            frappe.msgprint("ERROR: Invalid File Type. Attatch CSV File")

    else:
        frappe.msgprint("ERROR: No File Attached. Attatch CSV File.")

def create_csv_file(file_content, file_name, file_url):
    file_doc = frappe.get_doc({
	"doctype": "File",
	"file_name": file_name,
    "file_url": file_url,
	"attached_to_doctype": 'ShopDM Sync',
	"attached_to_name": 'ShopDM Sync',
	"content": file_content,
	"folder": "Home"
    })
    
    file_doc.save()
    frappe.db.commit()

def create_updated_table_csv():
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')
    item_update_table = shopdm_doc.item_update_table[0].as_dict()

    filters = ['item_no','description','category','price','quantity']

    # Create CSV file content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Get headers from filters
    headers = [field.upper() for field in item_update_table if field in filters]
    writer.writerow(headers)

    # Write CSV rows
    for row in shopdm_doc.item_update_table:
        row_data = [row.get(field.lower()) for field in headers]
        writer.writerow(row_data)
    
    # Get CSV file content
    csv_content = output.getvalue()
    output.close()
    
    # Save CSV to a file
    file_name = f'shopdm_items_{get_current_date()}.csv'
    file_url = f"/files/{file_name}"

    create_csv_file(csv_content, file_name, file_url)

def update_item_prices(price_list):
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')

    item_update_table_data = get_item_update_table_data()
    item_update_table = shopdm_doc.item_update_table

    if item_update_table_data:
        for item in item_update_table_data:
            price = get_item_price_from_price_list(price_list, item)
            item_item_no = item['item_no']

            for row in item_update_table:
                row_item_no = row.get('item_no')

                if row_item_no == item_item_no:
                    row.price = price

    shopdm_doc.save()
    frappe.db.commit()

def update_item_quantities(warehouse, min_quantity):
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')

    item_update_table_data = get_item_update_table_data()
    item_update_table = shopdm_doc.item_update_table

    if item_update_table_data:
        for item in item_update_table_data:
            qty = get_quantity_from_warehouse(warehouse, item, min_quantity)
            item_item_no = item['item_no']

            for row in item_update_table:
                row_item_no = row.get('item_no')

                if row_item_no == item_item_no:
                    row.quantity = qty


    shopdm_doc.save()
    frappe.db.commit()
    
def is_item_exists(item_code):
    result = frappe.get_all('Item', filters={'item_code': item_code}, fields=['name'])

    return len(result) > 0

def is_item_price_exists(item_code, price_list):
    result = frappe.get_all('Item Price', filters={'item_code': item_code, 'price_list': price_list}, fields=['name'])

    return len(result) > 0

def csv_to_json(csv_file_path):
    json_array = []

    with open(csv_file_path, encoding='latin-1') as csvf:
        csvReader = csv.DictReader(csvf, delimiter=",")

        for row in csvReader:
            frappe.errprint(row)
            json_array.append(row)  
    
    return json_array