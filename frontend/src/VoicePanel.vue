<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { api } from './api.js'
import { VoiceSession } from './voice.js'

const audio = ref(null)
const current = ref({ state: 'idle', message: '', playbackBlocked: false })
const configured = ref(false), checked = ref(false), duration = ref(300)
let connection
const canStart = computed(() => ['idle', 'closed', 'error'].includes(current.value.state))
const labels = { idle: 'Idle', permission: 'Permission', connecting: 'Connecting', active: 'Active', muted: 'Muted', closing: 'Closing', closed: 'Closed', error: 'Unavailable' }
onMounted(async () => {
  connection = new VoiceSession({ request: api, audio: audio.value, onChange: value => { current.value = value } })
  try { const data = await api('/voice/config'); configured.value = data.configured; duration.value = data.max_session_seconds }
  catch { configured.value = false }
  checked.value = true
})
function start() { connection?.start() }
function end(reason) { return connection?.end(reason) }
onBeforeUnmount(() => end('unmount'))
defineExpose({ end })
</script>

<template>
  <section class="voice-panel" aria-labelledby="voice-title">
    <div class="voice-heading"><h2 id="voice-title">Prefer to talk?</h2><span class="voice-state" role="status">{{ labels[current.state] }}</span></div>
    <p v-if="!checked">Checking voice availability…</p>
    <p v-else-if="!configured">Voice needs an OpenAI API key and backend setup. Text questions are ready below.</p>
    <p v-else>Voice uses your microphone and a paid AI service. This app does not save the audio or transcript. Keep the classroom test under 60 seconds.</p>
    <div class="button-row">
      <button v-if="canStart" class="secondary" :disabled="!checked" @click="start">Start voice · microphone</button>
      <button v-if="['active', 'muted'].includes(current.state)" class="secondary" @click="connection.mute()">{{ current.state === 'muted' ? 'Unmute microphone' : 'Mute microphone' }}</button>
      <button v-if="!canStart" class="stop-button" :disabled="current.state === 'closing'" @click="end('end')">End voice</button>
      <button v-if="current.playbackBlocked" class="primary" @click="connection.enableAudio()">Enable assistant audio</button>
    </div>
    <p v-if="current.message" :role="current.state === 'error' ? 'alert' : 'status'">{{ current.message }}</p>
    <p v-if="configured" class="subtle">Mute keeps the session running. End releases the microphone. Maximum session: {{ duration }} seconds.</p>
    <audio ref="audio" autoplay></audio>
  </section>
</template>
