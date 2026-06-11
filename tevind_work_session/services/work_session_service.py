# Copyright (c) 2026, Tevind AB and contributors
# For license information, please see license.txt

"""Business logic for managing work sessions.

A work session moves through three stages: ``Started`` (timer running),
``Finished`` (clock stopped and all details captured, still editable) and
``Submitted`` (one Work Entry and one Task Entry per task are created in
tevind_workforce / tevind_project and the session is locked).
"""

import frappe
from frappe import _
from frappe.utils import flt, now_datetime, time_diff_in_seconds, today

STARTABLE_TASK_STATUSES = ["PLANNED", "ONGOING"]

STARTED = "Started"
FINISHED = "Finished"
SUBMITTED = "Submitted"

OPEN_STATUSES = [STARTED, FINISHED]


def get_startable_tasks() -> list[dict]:
	"""Tasks that can be worked on right now."""
	return frappe.get_list(
		"Task",
		filters={"task_status": ["in", STARTABLE_TASK_STATUSES]},
		fields=["name", "task_name", "project", "task_status"],
		order_by="task_name asc",
	)


def get_active_contract(user: str) -> dict | None:
	"""Return the user's active work contract, or None."""
	contracts = frappe.get_list(
		"User Work Contract",
		filters={"user": user, "status": "ACTIVE"},
		fields=["name", "workforce_entity", "contract_type"],
		limit=1,
	)
	return contracts[0] if contracts else None


def _task_row_meta(task_name: str) -> dict:
	"""Task fields needed by the work session UI."""
	status, is_forever = frappe.db.get_value("Task", task_name, ["task_status", "is_forever_task"]) or (
		None,
		0,
	)
	return {
		"task_status": status,
		"is_forever_task": bool(is_forever),
	}


def _serialize_session(doc) -> dict:
	"""Turn a Work Session doc into a dict for the frontend."""
	tasks = []
	for row in doc.tasks:
		meta = _task_row_meta(row.task)
		tasks.append(
			{
				"task": row.task,
				"task_name": frappe.db.get_value("Task", row.task, "task_name"),
				"percentage": flt(row.percentage),
				"comments": row.comments,
				"mark_completed": bool(row.mark_completed),
				"task_status": meta["task_status"],
				"is_forever_task": meta["is_forever_task"],
			}
		)

	return {
		"name": doc.name,
		"session_status": doc.session_status,
		"user_work_contract": doc.user_work_contract,
		"work_location": doc.work_location,
		"start_time": doc.start_time,
		"end_time": doc.end_time,
		"total_minutes": doc.total_minutes,
		"tokens_used": doc.tokens_used,
		"motivation_level": doc.motivation_level,
		"todays_goals": doc.todays_goals,
		"work_satisfaction": doc.work_satisfaction,
		"self_evaluation": doc.self_evaluation,
		"notes": doc.notes,
		"tasks": tasks,
		"elapsed_seconds": int(time_diff_in_seconds(now_datetime(), doc.start_time)),
	}


def get_current_session(user: str) -> dict | None:
	"""Return the user's open (Started or Finished) work session, enriched."""
	sessions = frappe.get_list(
		"Work Session",
		filters={"owner": user, "session_status": ["in", OPEN_STATUSES]},
		pluck="name",
		order_by="creation desc",
		limit=1,
	)
	if not sessions:
		return None

	return _serialize_session(frappe.get_doc("Work Session", sessions[0]))


def _equal_task_percentages(task_count: int) -> float:
	return flt(100) / task_count if task_count else 0


def _set_session_tasks(doc, tasks: list[dict]) -> None:
	if not tasks:
		frappe.throw(_("A session needs at least one task."))
	task_names = [row.get("task") for row in tasks]
	if len(task_names) != len(set(task_names)):
		frappe.throw(_("Each task can only be added once."))

	default_pct = _equal_task_percentages(len(tasks))
	doc.set("tasks", [])
	for row in tasks:
		doc.append(
			"tasks",
			{
				"task": row.get("task"),
				"percentage": flt(row.get("percentage")) if row.get("percentage") is not None else default_pct,
				"comments": row.get("comments"),
				"mark_completed": 1 if row.get("mark_completed") else 0,
			},
		)


def start_session(
	tasks: list[str],
	work_location: str,
	motivation_level: str | None = None,
	todays_goals: str | None = None,
) -> dict:
	"""Create a Started work session for the current user."""
	user = frappe.session.user

	if not tasks:
		frappe.throw(_("Pick at least one task to work on."), title=_("Cannot start session"))

	contract = get_active_contract(user)
	if not contract:
		frappe.throw(_("You have no active work contract."), title=_("Cannot start session"))

	if get_current_session(user):
		frappe.throw(_("You already have an open work session."), title=_("Cannot start session"))

	session = frappe.get_doc(
		{
			"doctype": "Work Session",
			"user_work_contract": contract["name"],
			"work_location": work_location,
			"start_time": now_datetime(),
			"session_status": STARTED,
			"motivation_level": motivation_level,
			"todays_goals": todays_goals,
			"tasks": [
				{"task": task, "percentage": _equal_task_percentages(len(tasks))} for task in tasks
			],
		}
	)
	session.insert()
	return _serialize_session(session)


def update_active_session(session: str, payload: dict) -> dict:
	"""Update an in-progress (Started) session: work-entry fields, tasks, task comments."""
	doc = frappe.get_doc("Work Session", session)
	if doc.session_status != STARTED:
		frappe.throw(_("Only a started session can be updated this way."))

	if doc.owner != frappe.session.user:
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	if "motivation_level" in payload:
		doc.motivation_level = payload.get("motivation_level")
	if "todays_goals" in payload:
		doc.todays_goals = payload.get("todays_goals")
	if payload.get("tasks") is not None:
		_set_session_tasks(doc, payload["tasks"])

	doc.save()
	return _serialize_session(doc)


def _validate_percentages(tasks: list[dict]) -> None:
	if not tasks:
		frappe.throw(_("A session needs at least one task."))
	total = sum(flt(row.get("percentage")) for row in tasks)
	if round(total, 2) != 100:
		frappe.throw(_("Task percentages must add up to 100 (currently {0}).").format(round(total, 2)))


def _apply_payload(doc, payload: dict) -> None:
	"""Copy editable Finished-stage fields from a payload onto the session doc."""
	doc.end_time = payload.get("end_time") or now_datetime()
	doc.total_minutes = int(payload.get("total_minutes") or 0)
	doc.tokens_used = int(payload.get("tokens_used") or 0)
	doc.work_location = payload.get("work_location") or doc.work_location
	doc.motivation_level = payload.get("motivation_level")
	doc.todays_goals = payload.get("todays_goals")
	doc.work_satisfaction = payload.get("work_satisfaction")
	doc.self_evaluation = payload.get("self_evaluation")

	tasks = payload.get("tasks") or []
	_validate_percentages(tasks)
	doc.set("tasks", [])
	for row in tasks:
		doc.append(
			"tasks",
			{
				"task": row.get("task"),
				"percentage": flt(row.get("percentage")),
				"comments": row.get("comments"),
				"mark_completed": 1 if row.get("mark_completed") else 0,
			},
		)


def _complete_marked_tasks(session_tasks) -> list[str]:
	"""Set Task.task_status to COMPLETED for rows flagged in the session."""
	completed: list[str] = []
	for row in session_tasks:
		if not row.mark_completed:
			continue

		task_doc = frappe.get_doc("Task", row.task)
		if task_doc.is_forever_task:
			continue
		if task_doc.task_status == "COMPLETED":
			continue

		task_doc.task_status = "COMPLETED"
		task_doc.save()
		completed.append(row.task)

	return completed


def finish_session(session: str, payload: dict) -> dict:
	"""Stop the clock and capture all details; sets status to Finished.

	No Task Entry or Work Entry is created yet.
	"""
	doc = frappe.get_doc("Work Session", session)
	if doc.session_status == SUBMITTED:
		frappe.throw(_("This work session is already submitted."))

	_apply_payload(doc, payload)
	doc.session_status = FINISHED
	doc.save()
	return _serialize_session(doc)


def submit_session(session: str, payload: dict | None = None) -> dict:
	"""Persist any edits, then create the Work Entry and Task Entries.

	The whole call runs in one request transaction, so if any entry fails
	to insert nothing is committed.
	"""
	doc = frappe.get_doc("Work Session", session)
	if doc.session_status == SUBMITTED:
		frappe.throw(_("This work session is already submitted."))

	if payload:
		_apply_payload(doc, payload)
	else:
		_validate_percentages([{"percentage": row.percentage} for row in doc.tasks])

	if not doc.end_time:
		doc.end_time = now_datetime()

	total_minutes = int(doc.total_minutes or 0)
	total_tokens = int(doc.tokens_used or 0)

	work_entry = frappe.get_doc(
		{
			"doctype": "Work Entry",
			"user_work_contract": doc.user_work_contract,
			"start_time": doc.start_time,
			"end_time": doc.end_time,
			"tokens_used": total_tokens,
			"work_location": doc.work_location,
			"motivation_level": doc.motivation_level,
			"todays_goals": doc.todays_goals,
			"work_satisfaction": doc.work_satisfaction,
			"self_evaluation": doc.self_evaluation,
		}
	)
	work_entry.insert()

	task_entries = []
	minutes_left = total_minutes
	tokens_left = total_tokens
	rows = doc.tasks
	for index, row in enumerate(rows):
		is_last = index == len(rows) - 1
		if is_last:
			minutes = minutes_left
			tokens = tokens_left
		else:
			minutes = round(total_minutes * flt(row.percentage) / 100)
			tokens = round(total_tokens * flt(row.percentage) / 100)
			minutes_left -= minutes
			tokens_left -= tokens

		task_entry = frappe.get_doc(
			{
				"doctype": "Task Entry",
				"task": row.task,
				"entry_date": today(),
				"minutes": minutes,
				"tokens": tokens,
				"comments": row.comments,
			}
		)
		task_entry.insert()
		task_entries.append(task_entry.name)

	completed_tasks = _complete_marked_tasks(doc.tasks)

	doc.work_entry = work_entry.name
	doc.session_status = SUBMITTED
	doc.save()

	return {
		"work_session": doc.name,
		"work_entry": work_entry.name,
		"task_entries": task_entries,
		"completed_tasks": completed_tasks,
	}
