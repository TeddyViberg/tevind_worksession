<template>
	<div class="frappe-card p-4">
		<h4 class="mb-3">{{ __("Start a work session") }}</h4>

		<div class="form-group">
			<label>{{ __("Tasks to work on") }}</label>
			<div v-if="!tasks.length" class="text-muted small">{{ __("No startable tasks found.") }}</div>
			<div v-for="t in tasks" :key="t.name" class="checkbox">
				<label>
					<input type="checkbox" :value="t.name" v-model="selected" />
					{{ t.task_name }} <span class="text-muted">({{ t.task_status }})</span>
				</label>
			</div>
		</div>

		<div class="form-group">
			<label>{{ __("Work Location") }}</label>
			<select v-model="workLocation" class="form-control">
				<option v-for="loc in WORK_LOCATIONS" :key="loc" :value="loc">{{ loc }}</option>
			</select>
		</div>

		<div class="section-label">{{ __("Work Entry") }}</div>

		<div class="form-group">
			<label>{{ __("Motivation Level") }}</label>
			<span class="field-hint">{{ __("→ Work Entry") }}</span>
			<select v-model="motivationLevel" class="form-control">
				<option value="">{{ __("Not set") }}</option>
				<option v-for="m in MOTIVATION_LEVELS" :key="m" :value="m">{{ m }}</option>
			</select>
		</div>

		<div class="form-group">
			<label>{{ __("Today's Goals") }}</label>
			<span class="field-hint">{{ __("→ Work Entry") }}</span>
			<textarea v-model="todaysGoals" class="form-control" rows="2" />
		</div>

		<button
			class="btn btn-primary"
			:disabled="!selected.length || starting"
			@click="start"
		>
			{{ starting ? __("Starting...") : __("Start session") }}
		</button>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { WORK_LOCATIONS, MOTIVATION_LEVELS } from "../schema.js";
import { getStartableTasks, startSession } from "../api.js";

const emit = defineEmits(["started"]);

const tasks = ref([]);
const selected = ref([]);
const workLocation = ref(WORK_LOCATIONS[0]);
const motivationLevel = ref("");
const todaysGoals = ref("");
const starting = ref(false);

async function start() {
	starting.value = true;
	try {
		const session = await startSession(
			selected.value,
			workLocation.value,
			motivationLevel.value,
			todaysGoals.value,
		);
		emit("started", session);
	} finally {
		starting.value = false;
	}
}

onMounted(async () => {
	tasks.value = await getStartableTasks();
});
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
</style>
