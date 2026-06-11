<template>
	<div class="work-session-page">
		<div v-if="loading" class="text-muted">{{ __("Loading...") }}</div>

		<template v-else>
			<FinishSession
				v-if="session && session.session_status === 'Finished'"
				:session="session"
				@submitted="onSubmitted"
			/>
			<ActiveSession
				v-else-if="session && session.session_status === 'Started'"
				:session="session"
				@finished="onFinished"
				@updated="onUpdated"
			/>
			<StartSession
				v-else
				@started="onStarted"
			/>
		</template>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import StartSession from "./components/StartSession.vue";
import ActiveSession from "./components/ActiveSession.vue";
import FinishSession from "./components/FinishSession.vue";
import { getCurrentSession } from "./api.js";

const loading = ref(true);
const session = ref(null);

async function refresh() {
	loading.value = true;
	try {
		session.value = await getCurrentSession();
	} finally {
		loading.value = false;
	}
}

function onStarted(newSession) {
	session.value = newSession;
}

function onFinished(finishedSession) {
	session.value = finishedSession;
}

function onUpdated(updatedSession) {
	session.value = updatedSession;
}

function onSubmitted() {
	session.value = null;
}

onMounted(refresh);
</script>

<style scoped>
.work-session-page {
	max-width: 640px;
	margin: 0 auto;
	padding: var(--padding-md, 15px) 0;
}
</style>
