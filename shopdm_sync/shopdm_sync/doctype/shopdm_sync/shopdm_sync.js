// Copyright (c) 2024, Jeriel Francis and contributors
// For license information, please see license.txt

frappe.ui.form.on("ShopDM Sync", {
    refresh: function(frm) {
        load_table_visibility(frm);        
        sync_table_visibility(frm);      
    },
    
    after_save: function(frm) {
        is_table_loaded(frm);
    } 
});

function load_table_visibility(frm) {
    if(frm.doc.shopdm_csv && !frm.doc.is_table_loaded) {
        add_load_table_button(frm);
        frm.remove_custom_button('Sync Table');

    } else {
        frm.remove_custom_button('Load Table');
    }
}

function sync_table_visibility(frm) {
    if(frm.doc.shopdm_csv && frm.doc.is_table_loaded) {
        frm.remove_custom_button('Load Table');
        add_sync_table_button(frm);
        
    } else {
        frm.remove_custom_button('Sync Table');
    }
}

function add_load_table_button(frm) {
    frm.add_custom_button(__("Load Table"), function() {
        frappe.call({
            method: "shopdm_sync.api.load_item_update_table",
            freeze: true,
            freeze_message: __('Loading Table...'),
            callback: function() {
                is_table_loaded(frm);
            }
        })
    });
}

function add_sync_table_button(frm) {
    frm.add_custom_button(__("Sync Table"), function() {
        frappe.call({
            method: "shopdm_sync.api.sync_item_update_table",
            freeze: true,
            freeze_message: __('Syncing Table...'),
            callback: function(r) {
                setTimeout(() => {location.reload(); }, 500);
            }
        })
    });
}

function is_table_loaded(frm) {
    frappe.call({
        method: 'shopdm_sync.api.is_table_loaded',
        freeze: true,
        freeze_message: __('Reloading...'),
        callback: function() {
            location.reload();
        }
    }); 
    // if(frm.doc.item_update_table.length > 0) {
    // }
}