# Copyright (c) 2026, Tevind AB and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class WorkSession(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from tevind_work_session.tevind_work_session.doctype.work_session_task.work_session_task import (
			WorkSessionTask,
		)

		end_time: DF.Datetime | None
		motivation_level: DF.Literal["", "Self-forcing", "Mid", "Motivated", "Excited"]
		notes: DF.SmallText | None
		self_evaluation: DF.Text | None
		session_status: DF.Literal["Started", "Finished", "Submitted"]
		start_time: DF.Datetime
		tasks: DF.Table[WorkSessionTask]
		todays_goals: DF.Text | None
		tokens_used: DF.Int
		total_minutes: DF.Int
		user_work_contract: DF.Link
		work_entry: DF.Link | None
		work_location: DF.Literal["IN HOUSE", "DEPLOYED", "REMOTE"]
		work_satisfaction: DF.Literal["", "Unsatisfied", "Neutral", "Satisfied"]
	# end: auto-generated types

	pass
