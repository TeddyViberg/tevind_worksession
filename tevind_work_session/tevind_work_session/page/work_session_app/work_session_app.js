frappe.pages["work-session-app"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Work Session"),
		single_column: true,
	});

	// hot reload in development
	if (frappe.boot.developer_mode) {
		frappe.hot_update = frappe.hot_update || [];
		frappe.hot_update.push(() => load_work_session(wrapper));
	}
};

frappe.pages["work-session-app"].on_page_show = function (wrapper) {
	load_work_session(wrapper);
};

function load_work_session(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("work_session.bundle.js").then(() => {
		frappe.work_session = new frappe.ui.WorkSession({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}
