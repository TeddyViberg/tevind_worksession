import { createApp } from "vue";
import WorkSessionComponent from "./WorkSession.vue";

class WorkSession {
	constructor({ wrapper, page }) {
		this.$wrapper = $(wrapper);
		this.page = page;
		this.setup_app();
	}

	setup_app() {
		let app = createApp(WorkSessionComponent);
		SetVueGlobals(app);
		this.$app = app.mount(this.$wrapper.get(0));
	}
}

frappe.provide("frappe.ui");
frappe.ui.WorkSession = WorkSession;
export default WorkSession;
