// Thin wrappers around frappe.call for the Work Session endpoints.

import { METHODS } from "./schema.js";

function call(method, args = {}) {
	return frappe.call({ method, args, type: "POST" }).then((r) => r.message);
}

export function getStartableTasks() {
	return call(METHODS.getStartableTasks);
}

export function getCurrentSession() {
	return call(METHODS.getCurrentSession);
}

export function startSession(tasks, work_location, motivation_level, todays_goals) {
	return call(METHODS.startSession, {
		tasks: JSON.stringify(tasks),
		work_location,
		motivation_level: motivation_level || null,
		todays_goals: todays_goals || null,
	});
}

export function updateActiveSession(session, payload) {
	return call(METHODS.updateActiveSession, { session, payload: JSON.stringify(payload) });
}

export function finishSession(session, payload) {
	return call(METHODS.finishSession, { session, payload: JSON.stringify(payload) });
}

export function submitSession(session, payload) {
	return call(METHODS.submitSession, { session, payload: JSON.stringify(payload) });
}
