// Static metadata for the Work Session page.

const API_ROOT = "tevind_work_session.api.work_session";

export const METHODS = {
	getStartableTasks: `${API_ROOT}.get_startable_tasks`,
	getCurrentSession: `${API_ROOT}.get_current_session`,
	startSession: `${API_ROOT}.start_session`,
	updateActiveSession: `${API_ROOT}.update_active_session`,
	finishSession: `${API_ROOT}.finish_session`,
	submitSession: `${API_ROOT}.submit_session`,
};

export const WORK_LOCATIONS = ["IN HOUSE", "DEPLOYED", "REMOTE"];
export const MOTIVATION_LEVELS = ["Self-forcing", "Mid", "Motivated", "Excited"];
export const WORK_SATISFACTIONS = ["Unsatisfied", "Neutral", "Satisfied"];
