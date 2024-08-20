// Copyright (c) 2024, Jeriel Francis and contributors
// For license information, please see license.txt

frappe.ui.form.on("ShopDM Sync", {
	refresh(frm) {
        frm.add_custom_button(__("Sync Table"), function() {
            frappe.call({
                method: "shopdm_sync.api.sync_table",
                freeze: true,
                freeze_message: __('Syncing Table')
            })
        });
	},
});
