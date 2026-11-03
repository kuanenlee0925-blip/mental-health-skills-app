import test from 'node:test'
import assert from 'node:assert/strict'
import { VoiceSession } from './voice.js'

const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b }); return { promise, resolve, reject } }
function fixture(overrides = {}) {
  const changes = [], calls = [], sent = [], timers = new Map()
  const track = { enabled: true, stopped: false, stop() { this.stopped = true } }
  const stream = { getTracks: () => [track], getAudioTracks: () => [track] }
  const audio = { srcObject: null, paused: false, play: async () => {}, pause() { this.paused = true } }
  const channel = { readyState: 'open', close() { this.readyState = 'closed' }, send(s) { sent.push(JSON.parse(s)); this.onmessage?.({ data: '{"type":"session.closed"}' }) } }
  const peer = { iceGatheringState: 'complete', closed: false, createDataChannel: () => channel,
    addTrack() {}, createOffer: async () => ({ type: 'offer', sdp: 'test-offer' }),
    async setLocalDescription(value) { this.localDescription = value },
    async setRemoteDescription(value) { this.remoteDescription = value },
    close() { this.closed = true }, removeEventListener() {}, addEventListener() {} }
  const request = async (path, options) => {
    calls.push([path, options])
    if (path === '/voice/config') return { configured: true, max_session_seconds: 300 }
    if (path.endsWith('/close')) return { closed: true, pending: false }
    return { session_id: 'live_fixture', sdp: 'test-answer', max_session_seconds: 300 }
  }
  const voice = new VoiceSession({ request, audio, onChange: s => changes.push(s), getMedia: async () => stream,
    createPeer: () => peer, uuid: () => 'fixture-id', makeStream: () => stream,
    schedule(fn, ms) { const token = {}; timers.set(token, { fn, ms }); return token }, cancel(token) { timers.delete(token) }, ...overrides })
  return { voice, changes, calls, sent, track, stream, audio, channel, peer, timers }
}
test('voice waits for session.started, mute preserves session, End releases resources once', async () => {
  const f = fixture()
  await f.voice.start()
  assert.equal(f.voice.state, 'connecting')
  f.channel.onmessage({ data: '{"type":"session.started"}' })
  assert.equal(f.voice.state, 'active')
  f.voice.mute()
  assert.equal(f.voice.state, 'muted'); assert.equal(f.track.enabled, false); assert.equal(f.peer.closed, false)
  f.voice.mute(); assert.equal(f.track.enabled, true)
  const closing = f.voice.end()
  assert.equal(f.track.stopped, true)
  await closing; await f.voice.end()
  assert.equal(f.peer.closed, true); assert.equal(f.audio.srcObject, null)
  assert.equal(f.voice.state, 'closed'); assert.equal(f.sent.length, 1)
  assert.equal(f.calls.filter(([p]) => p.endsWith('/close')).length, 1)
  assert.equal(f.timers.size, 0)
})
test('duplicate Start and late permission grant never activate an ended attempt', async () => {
  const permission = deferred()
  const f = fixture({ getMedia: () => permission.promise })
  const starting = f.voice.start()
  await Promise.resolve(); await Promise.resolve()
  assert.equal(await f.voice.start(), false)
  await f.voice.end()
  permission.resolve(f.stream)
  await starting
  assert.equal(f.track.stopped, true)
  assert.equal(f.voice.state, 'closed')
  assert.equal(f.calls.filter(([p]) => p === '/voice/sessions').length, 0)
})
test('permission denial leaves a recoverable error without a provider session', async () => {
  const f = fixture({ getMedia: async () => { throw Object.assign(new Error('fixture'), { name: 'NotAllowedError' }) } })
  await f.voice.start()
  assert.equal(f.voice.state, 'error')
  assert.match(f.changes.at(-1).message, /denied/)
  assert.equal(f.calls.filter(([p]) => p === '/voice/sessions').length, 0)
})
test('a late SDP response after End is closed at the backend without restoring UI', async () => {
  const answer = deferred(), reached = deferred(), calls = []
  const f = fixture({ request: async path => {
    calls.push(path)
    if (path === '/voice/config') return { configured: true }
    if (path === '/voice/sessions') { reached.resolve(); return answer.promise }
    return { closed: true }
  } })
  const starting = f.voice.start()
  await reached.promise
  await f.voice.end()
  answer.resolve({ session_id: 'late', sdp: 'late answer', max_session_seconds: 300 })
  await starting
  assert.equal(f.peer.remoteDescription, undefined)
  assert.equal(f.peer.closed, true)
  assert.equal(f.voice.state, 'closed')
  assert.ok(calls.some(p => p.endsWith('/close')))
})
test('blocked playback offers a user-gesture retry', async () => {
  const f = fixture()
  await f.voice.start()
  f.channel.onmessage({ data: '{"type":"session.started"}' })
  f.audio.play = async () => { throw new Error('autoplay blocked') }
  await f.voice.enableAudio()
  assert.equal(f.changes.at(-1).playbackBlocked, true)
  f.audio.play = async () => {}
  await f.voice.enableAudio()
  assert.equal(f.changes.at(-1).playbackBlocked, false)
  await f.voice.end()
})
for (const reason of ['navigation', 'support', 'page-exit', 'hidden', 'unmount', 'duration-limit']) {
  test(`${reason} releases microphone, audio, peer and timers`, async () => {
    const f = fixture()
    await f.voice.start()
    f.channel.onmessage({ data: '{"type":"session.started"}' })
    if (reason === 'duration-limit') {
      [...f.timers.values()].find(t => t.ms === 300000).fn()
      await f.voice.task.ending
    } else await f.voice.end(reason)
    assert.equal(f.track.stopped, true); assert.equal(f.peer.closed, true); assert.equal(f.audio.paused, true)
    assert.equal(f.timers.size, 0)
  })
}
test('missing config and provider failure never label voice active', async () => {
  for (const configured of [false, true]) {
    const f = fixture({ request: async path => {
      if (path === '/voice/config') return { configured }
      if (path.endsWith('/close')) return { closed: false }
      throw new Error('Provider failed')
    } })
    await f.voice.start()
    assert.equal(f.voice.state, 'error')
    assert.equal(f.changes.some(c => c.state === 'active'), false)
    if (configured) assert.equal(f.track.stopped, true)
  }
})
