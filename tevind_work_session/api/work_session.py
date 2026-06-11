# Copyright (c) 2026, Tevind AB and contributors
# For license information, please see license.txt

"""Whitelisted endpoints for the Work Session desk page.

These are thin wrappers only; the actual logic lives in
``tevind_work_session.services.work_session_service``.
"""

import frappe

from tevind_work_session.services import work_session_service as service


@frappe.whitelist()
def get_startable_tasks() -> list[dict]:
	"""Tasks that can currently be worked on."""
	return service.get_startable_tasks()


@frappe.whitelist()
def get_current_session() -> dict | None:
	"""The current user's open work session, if any."""
	return service.get_current_session(frappe.session.user)


@frappe.whitelist()
def start_session(
	tasks: str,
	work_location: str,
	motivation_level: str | None = None,
	todays_goals: str | None = None,
) -> dict:
	"""Start a new work session for the current user."""
	return service.start_session(
		frappe.parse_json(tasks),
		work_location,
		motivation_level,
		todays_goals,
	)


@frappe.whitelist()
def update_active_session(session: str, payload: str) -> dict:
	"""Update a started session (work-entry fields, tasks, task comments)."""
	return service.update_active_session(session, frappe.parse_json(payload))


@frappe.whitelist()
def finish_session(session: str, payload: str) -> dict:
	"""Stop the clock and capture all details (status -> Finished)."""
	return service.finish_session(session, frappe.parse_json(payload))


@frappe.whitelist()
def submit_session(session: str, payload: str | None = None) -> dict:
	"""Create the Work Entry and Task Entries (status -> Submitted)."""
	return service.submit_session(session, frappe.parse_json(payload) if payload else None)
