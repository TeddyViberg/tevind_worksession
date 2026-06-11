<template>
	<div class="frappe-card p-4">
		<div class="d-flex justify-content-between align-items-center mb-3">
			<h4 class="mb-0">{{ __("Work session in progress") }}</h4>
			<span class="indicator-pill green">{{ __("Started") }}</span>
		</div>

		<div class="elapsed-timer mb-3">
			<div class="text-muted small">{{ __("Elapsed") }}</div>
			<div class="elapsed-value">{{ elapsedLabel }}</div>
		</div>

		<div class="section-label">{{ __("Work Entry") }}</div>

		<div class="form-group">
			<label>{{ __("Motivation Level") }}</label>
			<span class="field-hint">{{ __("→ Work Entry") }}</span>
			<select v-model="motivationLevel" class="form-control" @change="saveWorkEntryFields">
				<option value="">{{ __("Not set") }}</option>
				<option v-for="m in MOTIVATION_LEVELS" :key="m" :value="m">{{ m }}</option>
			</select>
		</div>

		<div class="form-group">
			<label>{{ __("Today's Goals") }}</label>
			<span class="field-hint">{{ __("→ Work Entry") }}</span>
			<textarea
				v-model="todaysGoals"
				class="form-control"
				rows="2"
				@blur="saveWorkEntryFields"
			/>
		</div>

		<div class="section-label">{{ __("Task Entry") }}</div>

		<div v-for="t in taskRows" :key="t.task" class="task-row mb-2">
			<div class="task-row-head">
				<strong>{{ t.task_name || t.task }}</strong>
			</div>
			<label class="small text-muted mb-1">{{ __("Comments") }} → {{ __("Task Entry") }}</label>
			<textarea
				v-model="t.comments"
				class="form-control"
				rows="2"
				:placeholder="__('What did you do on this task?')"
				@blur="saveTasks"
			/>
		</div>

		<div v-if="availableToAdd.length" class="form-group mt-3">
			<label>{{ __("Add task") }}</label>
			<div class="d-flex gap-2">
				<select v-model="taskToAdd" class="form-control">
					<option value="" disabled>{{ __("Select a task") }}</option>
					<option v-for="t in availableToAdd" :key="t.name" :value="t.name">
						{{ t.task_name }}
					</option>
				</select>
				<button
					class="btn btn-default"
					:disabled="!taskToAdd || saving"
					@click="addTask"
				>
					{{ __("Add") }}
				</button>
			</div>
		</div>

		<p v-if="saving" class="text-muted small mb-2">{{ __("Saving...") }}</p>

		<button class="btn btn-primary mt-3" :disabled="finishing" @click="finish">
			{{ finishing ? __("Finishing...") : __("Finish session") }}
		</button>
	</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { MOTIVATION_LEVELS } from "../schema.js";
import { getStartableTasks, updateActiveSession, finishSession } from "../api.js";

const props = defineProps({
	session: { type: Object, required: true },
});
const emit = defineEmits(["finished", "updated"]);

const elapsedSeconds = ref(props.session.elapsed_seconds || 0);
const motivationLevel = ref(props.session.motivation_level || "");
const todaysGoals = ref(props.session.todays_goals || "");
const taskRows = ref(
	(props.session.tasks || []).map((t) => ({
		task: t.task,
		task_name: t.task_name,
		comments: t.comments || "",
	})),
);
const allStartableTasks = ref([]);
const taskToAdd = ref("");
const saving = ref(false);
const finishing = ref(false);

let timer = null;

const availableToAdd = computed(() => {
	const inSession = new Set(taskRows.value.map((t) => t.task));
	return allStartableTasks.value.filter((t) => !inSession.has(t.name));
});

const elapsedLabel = computed(() => {
	const total = elapsedSeconds.value;
	const h = Math.floor(total / 3600);
	const m = Math.floor((total % 3600) / 60);
	const s = total % 60;
	const pad = (n) => String(n).padStart(2, "0");
	return `${pad(h)}:${pad(m)}:${pad(s)}`;
});

function tasksPayload() {
	return taskRows.value.map((t) => ({
		task: t.task,
		comments: t.comments,
	}));
}

async function saveWorkEntryFields() {
	saving.value = true;
	try {
		const updated = await updateActiveSession(props.session.name, {
			motivation_level: motivationLevel.value || null,
			todays_goals: todaysGoals.value || null,
		});
		emit("updated", updated);
	} finally {
		saving.value = false;
	}
}

async function saveTasks() {
	saving.value = true;
	try {
		const updated = await updateActiveSession(props.session.name, {
			tasks: tasksPayload(),
		});
		syncFromSession(updated);
		emit("updated", updated);
	} finally {
		saving.value = false;
	}
}

async function addTask() {
	if (!taskToAdd.value) return;
	const meta = allStartableTasks.value.find((t) => t.name === taskToAdd.value);
	taskRows.value.push({
		task: taskToAdd.value,
		task_name: meta?.task_name || taskToAdd.value,
		comments: "",
	});
	taskToAdd.value = "";
	await saveTasks();
}

function syncFromSession(session) {
	taskRows.value = (session.tasks || []).map((t) => ({
		task: t.task,
		task_name: t.task_name,
		comments: t.comments || "",
	}));
}

async function finish() {
	finishing.value = true;
	try {
		const equalPct = taskRows.value.length ? 100 / taskRows.value.length : 100;
		const payload = {
			end_time: frappe.datetime.now_datetime(),
			total_minutes: Math.max(0, Math.round(elapsedSeconds.value / 60)),
			tokens_used: 0,
			work_location: props.session.work_location,
			motivation_level: motivationLevel.value || null,
			todays_goals: todaysGoals.value || null,
			tasks: taskRows.value.map((t) => ({
				task: t.task,
				percentage: equalPct,
				comments: t.comments,
			})),
		};
		const finished = await finishSession(props.session.name, payload);
		emit("finished", finished);
	} finally {
		finishing.value = false;
	}
}

onMounted(async () => {
	allStartableTasks.value = await getStartableTasks();
	timer = setInterval(() => (elapsedSeconds.value += 1), 1000);
});

onUnmounted(() => {
	if (timer) clearInterval(timer);
});
</script>

<style scoped>
.elapsed-value {
	font-size: 2rem;
	font-weight: 600;
	font-variant-numeric: tabular-nums;
}
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
	margin-bottom: 4px;
}
.gap-2 {
	gap: 8px;
}
</style>
