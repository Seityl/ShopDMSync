import io
import csv
import json
import frappe
import requests
from frappe import _
from frappe.model.document import Document

def update_table(min_quantity, price_list, warehouse):
    process_shopdm_csv()        

def get_absolute_path(file_name):
	if(file_name.startswith('/files/')):
		file_path = f'{frappe.utils.get_bench_path()}/sites/{frappe.utils.get_site_base_path()[2:]}/public{file_name}'
	if(file_name.startswith('/private/')):
		file_path = f'{frappe.utils.get_bench_path()}/sites/{frappe.utils.get_site_base_path()[2:]}{file_name}'
	return file_path

def csv_to_json(csvFilePath):
    jsonArray = []
    #read csv file
    with open(csvFilePath, encoding='latin-1') as csvf:
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf,delimiter=",")

        #convert each csv row into python dict
        for row in csvReader:
            frappe.errprint(row)
            #add this python dict to json array
            jsonArray.append(row)  
    #convert python jsonArray to JSON String and write to file
    return jsonArray

def process_shopdm_csv(docname=None):
    shopdm_doc = frappe.get_doc('ShopDM Sync', 'ShopDM Sync')
    
    shopdm_csv = frappe.get_all('File', filters={
        'attached_to_doctype': 'ShopDM Sync', 
        'attached_to_name': 'ShopDM Sync'
    }, fields=['file_url','file_name','file_type'])[0]
    
    if shopdm_csv:
        if shopdm_csv['file_type'] == 'CSV':
            url = shopdm_csv['file_url']
            full_path = get_absolute_path(url)

        item_data = csv_to_json(full_path)

    #     csv_file = io.StringIO(file_content.decode('utf-8'))
    #     csv_reader = csv.DictReader(csv_file)
        
    #     # Clear existing rows in the child table (optional)
    #     shopdm_doc.set('items', [])
        
        # Step 5: Populate the child table with CSV data
        for item in item_data:
            shopdm_doc.append('item_update_table', {
                'item_no': item['ITEM_NO'],
                'description': item['DESCRIPTION'],
                'category': item['CATEGORY'],
                'price': item['PRICE'],
                'quantity': item['DESCRIPTION']
            })

        shopdm_doc.save()
    # # Save the document with the populated child table
    # # doc.save()
    # frappe.msgprint(f"Successfully processed CSV attachment for document {docname}")

    #         # Read the CSV file content
    #         csv_file = io.StringIO(file_content.decode('utf-8'))
    #         csv_reader = csv.DictReader(csv_file)
            
    #         # Clear existing rows (if needed)
    #         doc.set('items', [])
            
    #         # Process CSV rows and populate the child table
    #         for row in csv_reader:

    #         # Save changes to the document
    #         doc.save()
    #         frappe.msgprint(f"Successfully processed CSV file for Sales Invoice {docname}")
    #         return

    # frappe.msgprint(f"No CSV file found in attachments of Sales Invoice {docname}")

# def download_file_content(file_url):
#     # Construct the full URL for the file
#     full_url = frappe.utils.get_url(file_url)
    
#     # Fetch the file content using requests
#     response = requests.get(full_url, headers={'Authorization': 'token {}'.format(frappe.get_conf().api_key)})
    
#     # Ensure the request was successful
#     if response.status_code == 200:
#         return response.content
#     else:
#         frappe.throw(f"Failed to fetch file content. Status code: {response.status_code}")