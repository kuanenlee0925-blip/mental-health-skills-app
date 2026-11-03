<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { api } from './api.js'
import { Pacer } from './pacer.js'
import VoicePanel from './VoicePanel.vue'

const view = ref('home')
const heading = ref(null)
const supportDialog = ref(null)
const supportOpen = ref(false)
const resumeButton = ref(null)
const voicePanel = ref(null)
const reducedMotion = ref(false)
const preferences = reactive({ cue_mode: 'text', use_saved_context: false, text_size: 'standard' })
const preferenceStatus = ref('Loading saved choices…')
const preferenceBusy = ref(true)
const preferencesLoaded = ref(false)
const health = ref(null)
const recentPractice = ref(null)
const recentLoading = ref(true), recentError = ref('')
let recentSerial = 0
const cue = ref(null)
const attempt = ref(null)
const saveState = ref('')
const saveError = ref('')
const localNotice = ref('')
const resultPayload = ref(null)
let engine, ticker, entryTime = performance.now(), lastCheckpoint = 0, focusBeforeSupport
let mediaQuery
const effectiveCue = computed(() => reducedMotion.value ? 'text' : preferences.cue_mode)
const isExercise = computed(() => view.value === 'exercise')
const outcomeText = computed(() => ({ completed: 'Exercise finished.', stopped: 'Exercise stopped.', interrupted: 'Exercise interrupted.' }[attempt.value?.outcome] || 'Exercise ended.'))

function remember(key, value) {
  try {
    if (value === null) sessionStorage.removeItem(key)
    else sessionStorage.setItem(key, JSON.stringify(value))
  } catch { localNotice.value = 'This browser cannot retain an unfinished attempt across refresh.' }
}
function recall(key) {
  try { return JSON.parse(sessionStorage.getItem(key)) } catch { return null }
}
async function navigate(where) {
  if (where !== 'questions') voicePanel.value?.end('navigation')
  view.value = where
  if (where === 'home') { entryTime = performance.now(); refreshRecentPractice() }
  await nextTick()
  heading.value?.focus()
  window.scrollTo({ top: 0, behavior: 'instant' })
}
async function refreshRecentPractice() {
  const serial = ++recentSerial
  recentLoading.value = true; recentError.value = ''
  try {
    const records = await api('/sessions')
    if (serial === recentSerial) recentPractice.value = records[0] || null
  } catch {
    if (serial === recentSerial) { recentPractice.value = null; recentError.value = 'Saved practice is unavailable. You can still start a new practice.' }
  } finally {
    if (serial === recentSerial) recentLoading.value = false
  }
}
async function savePreferences(change) {
  const proposed = { ...preferences, ...change }
  preferenceBusy.value = true
  preferenceStatus.value = 'Saving choice…'
  try {
    const saved = await api('/preferences', { method: 'PUT', body: proposed })
    Object.assign(preferences, { cue_mode: saved.cue_mode, use_saved_context: saved.use_saved_context, text_size: saved.text_size })
    preferencesLoaded.value = true
    preferenceStatus.value = 'Choice saved on this computer.'
  } catch (error) { preferenceStatus.value = 'Choice not saved. ' + error.message }
  finally { preferenceBusy.value = false }
}
function payload() {
  const stamp = engine.snapshot(performance.now())
  const terminal = !['running', 'paused'].includes(stamp.state)
  const data = {
    revision: ++attempt.value.revision,
    started_at: attempt.value.started_at,
    ended_at: terminal ? new Date(Date.parse(attempt.value.started_at) + stamp.wall_ms).toISOString() : null,
    outcome: terminal ? stamp.state : 'in_progress',
    cue_mode: attempt.value.cue_mode,
    wall_ms: stamp.wall_ms, excluded_ms: stamp.excluded_ms, active_ms: stamp.active_ms,
    setup_ms: attempt.value.setup_ms,
  }
  Object.assign(attempt.value, data)
  remember('breathing-pending', { id: attempt.value.id, ...data })
  return data
}
async function persist(data, id = attempt.value.id) {
  if (id === attempt.value?.id) { saveState.value = 'saving'; saveError.value = '' }
  try {
    const saved = await api('/sessions/' + id, { method: 'PUT', body: data })
    if (attempt.value?.id === id && attempt.value.revision === data.revision) {
      saveState.value = 'saved'
      if (saved.outcome !== 'in_progress') remember('breathing-pending', null)
    }
  } catch (error) {
    if (attempt.value?.id === id && attempt.value.revision === data.revision) {
      saveState.value = 'failed'; saveError.value = error.message
    }
  }
}
function startExercise() {
  voicePanel.value?.end('exercise')
  clearInterval(ticker)
  const start = performance.now()
  attempt.value = { id: crypto.randomUUID(), revision: -1, started_at: new Date().toISOString(), cue_mode: effectiveCue.value, setup_ms: Math.round(start - entryTime), outcome: 'in_progress' }
  engine = new Pacer(start)
  cue.value = engine.snapshot(start)
  resultPayload.value = null
  view.value = 'exercise'
  lastCheckpoint = start
  persist(payload())
  nextTick(() => heading.value?.focus())
  ticker = setInterval(() => {
    const now = performance.now()
    cue.value = engine.sample(now)
    if (!['running', 'paused'].includes(cue.value.state)) return finishExercise(cue.value.state)
    // Local refresh recovery is cheap; API checkpoints never hold up the cue.
    if (now - lastCheckpoint >= 5000) {
      lastCheckpoint = now
      persist(payload())
    }
  }, 50)
}
function finishExercise(outcome) {
  if (!engine || !isExercise.value) return
  clearInterval(ticker)
  cue.value = engine.finish(outcome, performance.now())
  resultPayload.value = payload()
  view.value = 'result'
  if (supportOpen.value) closeSupport()
  persist(resultPayload.value)
  nextTick(() => heading.value?.focus())
}
function pauseExercise() {
  if (!engine || !isExercise.value) return
  cue.value = engine.pause(performance.now())
  if (!['running', 'paused'].includes(cue.value.state)) finishExercise(cue.value.state)
  else {
    persist(payload())
    nextTick(() => resumeButton.value?.focus())
  }
}
function resume() {
  cue.value = engine.resume(performance.now())
  lastCheckpoint = performance.now()
  persist(payload())
}
function openSupport() {
  focusBeforeSupport = document.activeElement
  voicePanel.value?.end('support')
  if (isExercise.value) {
    cue.value = engine.pause(performance.now())
    if (!['running', 'paused'].includes(cue.value.state)) finishExercise(cue.value.state)
    else persist(payload())
  }
  supportOpen.value = true
  supportDialog.value.showModal()
}
function closeSupport() {
  supportOpen.value = false
  supportDialog.value.close()
  nextTick(() => {
    if (isExercise.value) resumeButton.value?.focus()
    else if (view.value === 'result') heading.value?.focus()
    else focusBeforeSupport?.focus()
  })
}
function visibilityChanged() {
  if (document.hidden) {
    voicePanel.value?.end('hidden')
    if (isExercise.value) finishExercise('interrupted')
  }
}
function pageLeaving() {
  voicePanel.value?.end('page-exit')
  if (isExercise.value && engine) {
    clearInterval(ticker)
    engine.finish('interrupted', performance.now())
    const data = payload()
    fetch('/api/sessions/' + attempt.value.id, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data), keepalive: true }).catch(() => {})
  }
}

const sessions = ref([]), conversations = ref([]), selectedConversation = ref('')
const historical = ref({ messages: [], requests: [], events: [] })
const historyLoading = ref(false), historyError = ref(''), historyDetailError = ref('')
const deleteConfirm = ref(false)
let historySerial = 0, detailSerial = 0
const formatTime = value => new Date(value).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', second: '2-digit' })
const seconds = value => (value / 1000).toFixed(1)
async function openHistory() {
  navigate('history')
  await refreshHistory()
}
async function refreshHistory() {
  const serial = ++historySerial
  historyLoading.value = true; historyError.value = ''
  try {
    const [s, c] = await Promise.all([api('/sessions'), api('/conversations')])
    if (serial !== historySerial) return
    sessions.value = s; conversations.value = c
    selectedConversation.value = c.some(x => x.id === selectedConversation.value) ? selectedConversation.value : c[0]?.id || ''
    await loadHistorical()
  } catch (error) { if (serial === historySerial) historyError.value = error.message }
  finally { if (serial === historySerial) historyLoading.value = false }
}
async function loadHistorical() {
  const serial = ++detailSerial
  historyDetailError.value = ''
  historical.value = { messages: [], requests: [], events: [] }
  if (!selectedConversation.value) return
  try {
    const data = await api('/conversations/' + selectedConversation.value + '/messages')
    if (serial === detailSerial) historical.value = data
  } catch (error) { if (serial === detailSerial) historyDetailError.value = error.message }
}
async function deleteHistory() {
  historyLoading.value = true
  try {
    await api('/history', { method: 'DELETE', body: { confirm: true } })
    newConversation()
    deleteConfirm.value = false
    await refreshHistory()
  } catch (error) { historyError.value = error.message; historyLoading.value = false }
}

const conversationId = ref(recall('breathing-conversation') || crypto.randomUUID())
const chat = ref({ messages: [], requests: [], events: [] })
const draft = ref(''), chatBusy = ref(false), chatError = ref(''), chatInfo = ref('')
let pendingQuestion = null, chatSerial = 0
async function openQuestions() {
  navigate('questions')
  if (chat.value.messages.length || !recall('breathing-conversation')) return
  const serial = chatSerial
  try {
    const data = await api('/conversations/' + conversationId.value + '/messages')
    if (serial === chatSerial) chat.value = data
  } catch (error) { if (serial === chatSerial) chatError.value = error.message }
}
function newConversation() {
  if (chatBusy.value) return
  ++chatSerial
  conversationId.value = crypto.randomUUID()
  remember('breathing-conversation', null)
  chat.value = { messages: [], requests: [], events: [] }
  draft.value = ''; chatError.value = ''; chatInfo.value = ''; pendingQuestion = null
}
async function submitQuestion() {
  if (chatBusy.value || !draft.value.trim()) return
  const content = draft.value.trim()
  if (!pendingQuestion || pendingQuestion.content !== content) pendingQuestion = { request_id: crypto.randomUUID(), content }
  const request = { ...pendingQuestion }, ident = conversationId.value, serial = chatSerial
  chatBusy.value = true; chatError.value = ''; chatInfo.value = ''
  try {
    await api('/conversations', { method: 'POST', body: { id: ident } })
    remember('breathing-conversation', ident)
    const result = await api('/conversations/' + ident + '/messages', { method: 'POST', body: request })
    if (serial !== chatSerial) return
    chatInfo.value = result.event ? 'Application notice saved.' : 'Reply saved. ' + (result.used_saved_context ? 'Saved history was available for this reply.' : 'Past sessions and other conversations were not shared.')
    draft.value = ''; pendingQuestion = null
  } catch (error) { if (serial === chatSerial) chatError.value = error.message }
  finally {
    try {
      const stored = await api('/conversations/' + ident + '/messages')
      if (serial === chatSerial) chat.value = stored
    } catch { /* The visible error already states that saving is not confirmed. */ }
    if (serial === chatSerial) chatBusy.value = false
  }
}

function motionChanged(event) { reducedMotion.value = event.matches }
onMounted(async () => {
  refreshRecentPractice()
  mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  reducedMotion.value = mediaQuery.matches
  mediaQuery.addEventListener('change', motionChanged)
  document.addEventListener('visibilitychange', visibilityChanged)
  window.addEventListener('pagehide', pageLeaving)
  const pending = recall('breathing-pending')
  if (pending?.id && Number.isInteger(pending.revision)) {
    const { id, ...data } = pending
    if (data.outcome === 'in_progress') {
      data.outcome = 'interrupted'; data.revision++
      data.ended_at = new Date(Date.parse(data.started_at) + data.wall_ms).toISOString()
    }
    attempt.value = { id, ...data }
    resultPayload.value = data
    view.value = 'result'
    persist(data)
    localNotice.value = 'The previous attempt was recovered from this tab. A refreshed exercise never resumes automatically.'
  }
  const results = await Promise.allSettled([api('/preferences'), api('/health')])
  if (results[0].status === 'fulfilled') {
    const p = results[0].value
    Object.assign(preferences, { cue_mode: p.cue_mode, use_saved_context: p.use_saved_context, text_size: p.text_size })
    preferencesLoaded.value = true
    preferenceStatus.value = 'Choices are saved on this computer.'
  } else preferenceStatus.value = 'Saved choices unavailable. Text cues are ready to use.'
  preferenceBusy.value = false
  if (results[1].status === 'fulfilled') health.value = results[1].value
})
onBeforeUnmount(() => {
  pageLeaving()
  clearInterval(ticker)
  document.removeEventListener('visibilitychange', visibilityChanged)
  window.removeEventListener('pagehide', pageLeaving)
  mediaQuery?.removeEventListener('change', motionChanged)
})
</script>

<template>
  <div class="app-shell" :class="{ 'practice-shell': isExercise, 'large-text': preferences.text_size === 'large' }">
    <header class="site-header">
      <div class="brand"><span class="brand-mark" aria-hidden="true">◌</span><span>a little space<span class="brand-caption">A SHORT PRACTICE</span></span></div>
      <button class="support-button" @click="openSupport"><span aria-hidden="true">＋</span> Crisis support</button>
    </header>

    <main id="main-content">
      <template v-if="view === 'home'">
        <section class="entry-card">
          <div class="entry-copy">
            <p class="eyebrow">PACED BREATHING · ABOUT 60 SECONDS</p>
            <h1 ref="heading" tabindex="-1">A little space,<br><em>at your own pace.</em></h1>
            <p class="intro">One simple cue at a time.<br>Inhale for 4 seconds. Exhale for 6.</p>
            <button class="primary start-button" @click="startExercise">Start breathing <span aria-hidden="true">↗</span></button>
            <p class="permission">You can stop at any time.</p>
          </div>
          <div class="entry-visual" aria-hidden="true">
            <div class="still-rings"><div class="inner-orbit"></div><span>room<br>to breathe</span></div>
            <div class="visual-caption"><span>6 gentle cycles</span><span>4 in / 6 out</span></div>
          </div>
        </section>
        <section class="choice-row" aria-label="Breathing display">
          <div><span class="small-label">YOUR DISPLAY</span><p>Choose what feels easier to follow.</p></div>
          <div class="segmented" aria-label="Display choice">
            <button :aria-pressed="preferences.cue_mode === 'text'" :disabled="preferenceBusy" @click="savePreferences({ cue_mode: 'text' })">Text cues</button>
            <button :aria-pressed="preferences.cue_mode === 'ring'" :disabled="preferenceBusy" @click="savePreferences({ cue_mode: 'ring' })">Gentle ring</button>
          </div>
        </section>
        <p class="subtle preference-note" role="status">{{ reducedMotion ? 'Reduced motion is on. You’ll see text cues.' : preferenceStatus }}</p>
        <details class="saved-choices">
          <summary>Your saved choices</summary>
          <p class="subtle">One local profile for fictional coursework testing. You can change these choices at any time.</p>
          <p v-if="preferencesLoaded">Saved display: <strong>{{ preferences.cue_mode === 'ring' ? 'Gentle ring' : 'Text cues' }}</strong>. History sharing with text answers is <strong>{{ preferences.use_saved_context ? 'on' : 'off' }}</strong>.</p>
          <p v-else>Saved choices are not available yet. The display controls above show your current choice.</p>
          <label class="context-choice"><input type="checkbox" :checked="preferences.text_size === 'large'" :disabled="preferenceBusy" @change="savePreferences({ text_size: $event.target.checked ? 'large' : 'standard' })"><span>Larger text<span class="subtle">Remember this reading size on this computer.</span></span></label>
          <p class="subtle" role="status">{{ preferenceStatus }}</p>
          <p v-if="recentLoading" role="status">Loading your latest saved practice…</p>
          <p v-else-if="recentError" role="status">{{ recentError }}</p>
          <template v-else-if="recentPractice">
            <p>Your latest saved practice was <strong>{{ recentPractice.outcome === 'in_progress' ? 'unfinished' : recentPractice.outcome }}</strong>, with {{ recentPractice.cue_mode === 'ring' ? 'gentle ring' : 'text' }} cues and {{ seconds(recentPractice.active_ms) }} seconds of practice time.</p>
            <p class="subtle">{{ formatTime(recentPractice.started_at) }} · This records activity, not how you felt.</p>
            <button class="secondary" :disabled="preferenceBusy" @click="savePreferences({ cue_mode: recentPractice.cue_mode })">Use last practice’s display</button>
          </template>
          <p v-else>No saved practice yet. Start whenever you choose.</p>
          <button class="text-button" @click="openHistory">Review history and manage saved information ↗</button>
          <p v-if="reducedMotion" class="subtle">Reduced motion is on, so the exercise uses text even if a ring choice is saved.</p>
        </details>
        <nav class="secondary-links" aria-label="Optional activities">
          <details><summary>How it works <span aria-hidden="true">＋</span></summary><p>Follow six cycles of inhale and exhale cues. There is nothing to type or rate. Stop ends the practice immediately. Pause or opening support holds the current cue; you decide whether to resume.</p></details>
          <button @click="openQuestions">Ask a question <span aria-hidden="true">↗</span></button>
          <button @click="openHistory">Your history <span aria-hidden="true">↗</span></button>
        </nav>
      </template>

      <section v-else-if="view === 'exercise'" class="practice-card" aria-label="Breathing exercise">
        <p class="eyebrow">PACED BREATHING</p>
        <div class="pacer" :class="{ 'with-ring': attempt.cue_mode === 'ring' && !reducedMotion }">
          <div v-if="attempt.cue_mode === 'ring' && !reducedMotion" class="breathing-ring" :style="{ transform: `scale(${cue.ringScale})` }" aria-hidden="true"></div>
          <div class="cue-content">
            <h1 ref="heading" tabindex="-1" aria-live="polite" aria-atomic="true">{{ cue.state === 'paused' ? 'Paused' : cue.phase }}</h1>
            <span class="countdown" aria-hidden="true">{{ cue.remaining }}</span>
            <span class="sr-only">{{ cue.state === 'paused' ? 'Choose Resume or Stop.' : 'Follow the current cue.' }}</span>
            <p class="cycle-label">Cycle {{ cue.cycle }} of 6</p>
          </div>
        </div>
        <div class="button-row practice-actions">
          <button v-if="cue.state === 'paused'" ref="resumeButton" class="primary" @click="resume">Resume</button>
          <button v-else class="secondary" @click="pauseExercise">Pause</button>
          <button class="stop-button" @click="finishExercise('stopped')">Stop</button>
        </div>
        <p class="permission">{{ cue.state === 'paused' ? 'Take your time. Nothing continues until you choose.' : 'You can stop whenever you want.' }}</p>
      </section>

      <section v-else-if="view === 'result'" class="result-card">
        <span class="result-symbol" aria-hidden="true">◌</span>
        <p class="eyebrow">YOUR PRACTICE</p>
        <h1 ref="heading" tabindex="-1">{{ outcomeText }}</h1>
        <p v-if="attempt.outcome === 'interrupted'">The cue stopped because the page was left or its timing was interrupted.</p>
        <p v-else>You can leave it here, or choose what comes next.</p>
        <dl class="result-numbers"><div><dt>Practice time</dt><dd>{{ seconds(attempt.active_ms) }} <span>sec</span></dd></div><div v-if="attempt.excluded_ms"><dt>Time paused</dt><dd>{{ seconds(attempt.excluded_ms) }} <span>sec</span></dd></div></dl>
        <p class="save-label" role="status">{{ saveState === 'saved' ? 'Session saved on this computer.' : saveState === 'saving' ? 'Saving session…' : 'Session not confirmed saved.' }}</p>
        <div v-if="saveState === 'failed'" class="error-box" role="alert"><p>{{ saveError }}</p><p>This result remains in this tab until another practice or browser cleanup replaces it.</p><button @click="persist(resultPayload)">Retry save</button></div>
        <p v-if="localNotice" class="subtle">{{ localNotice }}</p>
        <div class="button-row"><button class="primary" @click="navigate('home')">Back to breathing</button><button class="secondary" @click="openHistory">View history</button></div>
      </section>

      <section v-else-if="view === 'questions'" class="content-card questions-card">
        <button class="back-link" @click="navigate('home')">← Back to breathing</button>
        <div class="section-title"><div><p class="eyebrow">OPTIONAL</p><h1 ref="heading" tabindex="-1">A question, if you like.</h1></div><span class="mode-label">{{ health?.mode === 'demo' ? 'Demo responses · no live AI' : health?.configured ? 'Live AI' : 'AI connection unavailable' }}</span></div>
        <p class="intro-small">Ask about the exercise or your saved activity. Use fictional examples for this coursework prototype.</p>
        <VoicePanel ref="voicePanel" />
        <label class="context-choice"><input type="checkbox" :checked="preferences.use_saved_context" :disabled="preferenceBusy || chatBusy" @change="savePreferences({ use_saved_context: $event.target.checked })"><span>Use saved history<span class="subtle">Include past sessions, settings, and other text conversations in text answers.</span></span></label>
        <p class="subtle" role="status">{{ preferenceStatus }}</p>
        <div class="conversation" aria-label="Current text conversation">
          <p v-if="!chat.messages.length" class="empty-message">You could ask, “What happens when I stop?”</p>
          <article v-for="message in chat.messages" :key="message.id" class="message" :class="message.role"><div class="message-meta">{{ message.role === 'user' ? 'You' : message.mode === 'demo' ? 'Demo reply' : 'AI reply' }} · {{ formatTime(message.created_at) }} · {{ message.status === 'failed' ? 'Question saved; response failed' : message.status }}</div><p>{{ message.content }}</p></article>
          <article v-for="event in chat.events" :key="event.id" class="notice"><span class="small-label">APPLICATION NOTICE</span><p>{{ event.content }}</p><button @click="openSupport">Open crisis support</button></article>
        </div>
        <form @submit.prevent="submitQuestion">
          <label class="small-label" for="question">YOUR QUESTION</label>
          <textarea id="question" v-model="draft" rows="3" maxlength="1200" :disabled="chatBusy" placeholder="Ask about the practice…" required></textarea>
          <div class="form-bottom"><span class="subtle">Optional. You don’t need to share how you feel.</span><button class="primary" :disabled="chatBusy || !draft.trim()">{{ chatBusy ? 'Waiting for response…' : chatError && draft ? 'Retry / send question' : 'Send question' }}</button></div>
        </form>
        <p v-if="chatError" class="error-box" role="alert">{{ chatError }}</p>
        <p v-if="chatInfo" class="subtle" role="status">{{ chatInfo }}</p>
        <div class="question-footer"><button class="text-button" :disabled="chatBusy" @click="newConversation">New text conversation</button><button class="text-button" @click="openHistory">View saved history ↗</button></div>
      </section>

      <section v-else-if="view === 'history'" class="content-card history-card">
        <button class="back-link" @click="navigate('home')">← Back to breathing</button>
        <div class="section-title"><div><p class="eyebrow">SAVED ON THIS COMPUTER</p><h1 ref="heading" tabindex="-1">Your history.</h1></div><button class="secondary" :disabled="historyLoading" @click="refreshHistory">Refresh history</button></div>
        <p class="intro-small">A record of practice, without ratings or interpretations. All activity here is for fictional coursework testing.</p>
        <p v-if="historyLoading" role="status">Loading saved records…</p>
        <p v-if="historyError" class="error-box" role="alert">{{ historyError }}</p>
        <template v-if="!historyLoading && !historyError">
          <h2>Breathing sessions</h2>
          <p v-if="!sessions.length" class="empty-message">No sessions saved yet. There’s nothing you need to catch up on.</p>
          <div v-else class="table-scroll"><table><caption class="sr-only">The latest 200 saved breathing sessions</caption><thead><tr><th scope="col">When</th><th scope="col">Practice time</th><th scope="col">Outcome</th><th scope="col">Details</th></tr></thead><tbody><tr v-for="session in sessions" :key="session.id"><td>{{ formatTime(session.started_at) }}</td><td>{{ seconds(session.active_ms) }} sec</td><td><span class="outcome-badge">{{ session.outcome === 'in_progress' ? 'Unfinished' : session.outcome }}</span></td><td><details><summary>Record details</summary><p class="record-id">{{ session.id }}</p><p>{{ session.cue_mode }} cues · {{ seconds(session.excluded_ms) }} sec paused · {{ seconds(session.wall_ms) }} sec total · {{ seconds(session.setup_ms) }} sec setup</p></details></td></tr></tbody></table></div>
          <div class="history-conversations"><h2>Text conversations</h2><p class="subtle">Voice audio and transcripts are not saved by this app.</p>
            <p v-if="!conversations.length" class="empty-message">No text conversations saved yet.</p>
            <template v-else><label for="conversation">Choose a conversation</label><select id="conversation" v-model="selectedConversation" @change="loadHistorical"><option v-for="conversation in conversations" :key="conversation.id" :value="conversation.id">{{ formatTime(conversation.created_at) }} · {{ conversation.id.slice(0, 8) }}</option></select><p class="record-id">Conversation {{ selectedConversation }}</p><p v-if="historyDetailError" role="alert" class="error-box">{{ historyDetailError }}</p>
              <article v-for="message in historical.messages" :key="message.id" class="message" :class="message.role"><div class="message-meta">{{ message.sequence }} · {{ message.role === 'user' ? 'You' : message.mode === 'demo' ? 'Demo reply' : 'AI reply' }} · {{ formatTime(message.created_at) }} · {{ message.status === 'failed' ? 'Question saved; response failed' : message.status }}</div><p>{{ message.content }}</p><details><summary>Record details</summary><p class="record-id">Message {{ message.id }}<br>Request {{ message.request_id }}</p></details></article>
              <article v-for="event in historical.events" :key="event.id" class="notice"><span class="small-label">APPLICATION NOTICE</span><p>{{ event.content }}</p></article>
            </template>
          </div>
          <details class="manage-history"><summary>Manage saved information</summary><button class="secondary" :disabled="preferenceBusy" @click="savePreferences({ cue_mode: 'text', use_saved_context: false, text_size: 'standard' })">Reset preferences</button><p class="subtle">{{ preferenceStatus }}</p><button class="text-button" @click="deleteConfirm = true">Delete saved sessions and text conversations</button><div v-if="deleteConfirm" class="error-box"><p>Delete all saved sessions and text conversations from this local app? This cannot be undone. Preferences stay saved.</p><div class="button-row"><button class="secondary" @click="deleteConfirm = false">Keep history</button><button class="danger" @click="deleteHistory">Delete history</button></div></div></details>
        </template>
      </section>
    </main>

    <footer class="site-footer"><span>Coursework prototype · Fictional testing only</span><span>Not therapy or a monitored support service.</span></footer>

    <dialog ref="supportDialog" class="support-dialog" aria-labelledby="support-title" @cancel.prevent="closeSupport">
      <p class="eyebrow">UNITED STATES & TERRITORIES</p>
      <h2 id="support-title">Crisis support</h2>
      <p v-if="isExercise" class="pause-notice">Your exercise is paused. You can stop at any time.</p>
      <p>988 Suicide & Crisis Lifeline connects people in suicidal crisis or emotional distress with crisis counselors.</p>
      <div class="support-resource"><h3>988 Suicide & Crisis Lifeline</h3><p>Call <a href="tel:988?oai_link_source=model_response_hotline">988</a> or text <a href="sms:988?oai_link_source=model_response_hotline">988</a></p><p><a href="https://988lifeline.org/chat/?oai_link_source=model_response_hotline" target="_blank" rel="noopener noreferrer">https://988lifeline.org/chat/</a></p><p><a href="https://988lifeline.org?oai_link_source=model_response_hotline" target="_blank" rel="noopener noreferrer">https://988lifeline.org</a></p></div>
      <p class="subtle">U.S. resources · verified October 22, 2026. This app does not contact anyone or monitor your safety. Contact links open an external service.</p>
      <div class="button-row"><button v-if="isExercise" class="stop-button" @click="finishExercise('stopped')">Stop exercise</button><button class="primary" autofocus @click="closeSupport">Close support</button></div>
    </dialog>
  </div>
</template>
