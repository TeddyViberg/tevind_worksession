<template>
	<div class="frappe-card p-4">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h4 class="mb-0">{{ __("Review and submit") }}</h4>
			<span class="indicator-pill orange">{{ __("Finished") }}</span>
		</div>

		<div class="row">
			<div class="form-group col-sm-6">
				<label>{{ __("Total Minutes") }}</label>
				<input v-model.number="totalMinutes" type="number" min="0" class="form-control" />
			</div>
			<div class="form-group col-sm-6">
				<label>{{ __("Tokens Used") }}</label>
				<span class="field-hint">{{ __("→ Work Entry") }}</span>
				<input v-model.number="tokensUsed" type="number" min="0" class="form-control" />
			</div>
		</div>

		<div class="form-group">
			<label>{{ __("Work Location") }}</label>
			<span class="field-hint">{{ __("→ Work Entry") }}</span>
			<select v-model="workLocation" class="form-control">
				<option v-for="loc in WORK_LOCATIONS" :key="loc" :value="loc">{{ loc }}</option>
			</select>
		</div>

		<div class="section-label">{{ __("Task Entry") }}</div>

		<div class="form-group">
			<div class="d-flex justify-content-between align-items-center">
				<label class="mb-0">{{ __("Task allocation") }}</label>
				<span :class="['small', percentValid ? 'text-muted' : 'text-danger']">
					{{ __("Total") }}: {{ percentTotal }}%
				</span>
			</div>
			<div v-for="(t, i) in tasks" :key="t.task" class="task-row mt-2">
				<div class="task-row-head">
					<span>
						{{ t.task_name || t.task }}
						<span v-if="t.task_status" class="text-muted small">({{ t.task_status }})</span>
					</span>
					<div class="pct-input">
						<input v-model.number="t.percentage" type="number" min="0" max="100" class="form-control" />
						<span class="pct-sign">%</span>
					</div>
				</div>
				<label class="small text-muted mb-1">{{ __("Comments") }} → {{ __("Task Entry") }}</label>
				<textarea
					v-model="t.comments"
					class="form-control"
					:placeholder="__('What did you do on this task?')"
				/>
				<div v-if="!t.is_forever_task" class="checkbox mt-2">
					<label>
						<input type="checkbox" v-model="t.mark_completed" />
						{{ __("Mark task as completed") }}
						<span class="field-hint d-inline">→ {{ __("Task") }}</span>
					</label>
				</div>
				<p v-else class="text-muted small mt-2 mb-0">
					{{ __("Forever tasks cannot be marked completed.") }}
				</p>
				<div class="text-muted small mt-1">
					{{ allocatedMinutes(i) }} {{ __("min") }} · {{ allocatedTokens(i) }} {{ __("tokens") }}
				</div>
			</div>
		</div>

		<div class="section-label">{{ __("Work Entry") }}</div>

		<div class="row">
			<div class="form-group col-sm-6">
				<label>{{ __("Motivation Level") }}</label>
				<span class="field-hint">{{ __("→ Work Entry") }}</span>
				<select v-model="motivationLevel" class="form-control">
					<option value="">{{ __("Not set") }}</option>
					<option v-for="m in MOTIVATION_LEVELS" :key="m" :value="m">{{ m }}</option>
				</select>
			</div>
			<div class="form-group col-sm-6">
				<label>{{ __("Satisfaction with Today's Work") }}</label>
				<span class="field-hint">{{ __("→ Work Entry") }}</span>
				<select v-model="workSatisfaction" class="form-control">
					<option value="">{{ __("Not set") }}</option>
					<option v-for="s in WORK_SATISFACTIONS" :key="s" :value="s">{{ s }}</option>
				</select>
			</div>
		</div>

		<div class="form-group">
			<label>{{ __("Today's Goals") }}</label>
			<span class="field-hint">{{ __("→ Work Entry") }}</span>
			<textarea v-model="todaysGoals" class="form-control" rows="2" />
		</div>

		<div class="form-group">
			<label>{{ __("Self Evaluation") }}</label>
			<span class="field-hint">{{ __("→ Work Entry") }}</span>
			<textarea v-model="selfEvaluation" class="form-control" rows="2" />
		</div>

		<button
			class="btn btn-primary"
			:disabled="!percentValid || submitting"
			@click="submit"
		>
			{{ submitting ? __("Submitting...") : __("Submit session") }}
		</button>
	</div>
</template>

<script setup>
import { ref, computed } from "vue";
import { WORK_LOCATIONS, MOTIVATION_LEVELS, WORK_SATISFACTIONS } from "../schema.js";
import { submitSession } from "../api.js";

const props = defineProps({
	session: { type: Object, required: true },
});
const emit = defineEmits(["submitted"]);

const totalMinutes = ref(props.session.total_minutes || 0);
const tokensUsed = ref(props.session.tokens_used || 0);
const workLocation = ref(props.session.work_location || WORK_LOCATIONS[0]);
const motivationLevel = ref(props.session.motivation_level || "");
const workSatisfaction = ref(props.session.work_satisfaction || "");
const todaysGoals = ref(props.session.todays_goals || "");
const selfEvaluation = ref(props.session.self_evaluation || "");
const tasks = ref(
	(props.session.tasks || []).map((t) => ({
		task: t.task,
		task_name: t.task_name,
		percentage: t.percentage,
		comments: t.comments || "",
		mark_completed: Boolean(t.mark_completed),
		task_status: t.task_status,
		is_forever_task: Boolean(t.is_forever_task),
	})),
);
const submitting = ref(false);

const percentTotal = computed(() =>
	Math.round(tasks.value.reduce((sum, t) => sum + (Number(t.percentage) || 0), 0) * 100) / 100,
);
const percentValid = computed(() => percentTotal.value === 100);

function allocatedMinutes(i) {
	return Math.round(((Number(tasks.value[i].percentage) || 0) / 100) * (totalMinutes.value || 0));
}
function allocatedTokens(i) {
	return Math.round(((Number(tasks.value[i].percentage) || 0) / 100) * (tokensUsed.value || 0));
}

async function submit() {
	submitting.value = true;
	try {
		const payload = {
			end_time: props.session.end_time || frappe.datetime.now_datetime(),
			total_minutes: totalMinutes.value || 0,
			tokens_used: tokensUsed.value || 0,
			work_location: workLocation.value,
			motivation_level: motivationLevel.value || null,
			work_satisfaction: workSatisfaction.value || null,
			todays_goals: todaysGoals.value || null,
			self_evaluation: selfEvaluation.value || null,
			tasks: tasks.value.map((t) => ({
				task: t.task,
				percentage: t.percentage,
				comments: t.comments,
				mark_completed: t.mark_completed,
			})),
		};
		const result = await submitSession(props.session.name, payload);
		const completedCount = (result.completed_tasks || []).length;
		frappe.show_alert({
			message: completedCount
				? __("Session submitted. {0} task entries, 1 work entry, {1} task(s) marked completed.", [
						result.task_entries.length,
						completedCount,
					])
				: __("Session submitted. {0} task entries and 1 work entry created.", [
						result.task_entries.length,
					]),
			indicator: "green",
		});
		emit("submitted", result);
	} finally {
		submitting.value = false;
	}
}
</script>

<style scoped>
.section-label {
	font-size: 0.75rem;
	font-weight: 600;
	text-transform: uppercase;
	color: var(--text-muted);
	margin: 1rem 0 0.5rem;
	letter-spacing: 0.04em;
}
.field-hint {
	display: block;
	font-size: 0.75rem;
	color: var(--text-muted);
	margin-bottom: 4px;
}
.task-row {
	border: 1px solid var(--border-color, #e2e2e2);
	border-radius: var(--border-radius, 6px);
	padding: 8px 10px;
}
.task-row-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 10px;
}
.pct-input {
	display: flex;
	align-items: center;
	gap: 4px;
	width: 110px;
}
.pct-sign {
	color: var(--text-muted);
}
.checkbox label {
	margin-bottom: 0;
	font-weight: normal;
}
</style>
