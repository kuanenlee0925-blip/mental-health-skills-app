// Native WebRTC lifecycle, with dependency injection for tests that never open a microphone.
export class VoiceSession {
  constructor({ request, audio, onChange, getMedia = () => navigator.mediaDevices.getUserMedia({ audio: true, video: false }),
    createPeer = () => new RTCPeerConnection(), makeStream = track => new MediaStream([track]),
    uuid = () => crypto.randomUUID(), schedule = setTimeout, cancel = clearTimeout }) {
    Object.assign(this, { request, audio, onChange, getMedia, createPeer, makeStream, uuid, schedule, cancel })
    this.task = null
    this.state = 'idle'
  }
  publish(task, state, message = '', blocked = task?.playbackBlocked || false) {
    if (this.task !== task) return
    task.playbackBlocked = blocked
    this.state = state
    this.onChange({ state, message, playbackBlocked: blocked })
  }
  alive(task) { return !!task && this.task === task && !task.ended }
  later(task, fn, ms) {
    const timer = this.schedule(fn, ms)
    task.timers.add(timer)
    return timer
  }
  async start() {
    if (this.task && !['closed', 'error', 'idle'].includes(this.state)) return false
    const task = { id: this.uuid(), ended: false, timers: new Set(), stream: null, peer: null, channel: null, requested: false, confirmed: false, muted: false }
    this.task = task
    this.publish(task, 'permission', 'Checking voice setup…')
    try {
      const config = await this.request('/voice/config')
      if (!this.alive(task)) return false
      if (!config.configured) throw new Error('Voice needs backend setup and an OpenAI API key. Text chat is still available.')
      this.publish(task, 'permission', 'Waiting for microphone permission…')
      const stream = await this.getMedia()
      if (!this.alive(task)) { stream.getTracks().forEach(track => track.stop()); return false }
      task.stream = stream
      const peer = this.createPeer()
      task.peer = peer
      stream.getAudioTracks().forEach(track => peer.addTrack(track, stream))
      // The data channel must exist before the browser creates its SDP offer.
      const channel = peer.createDataChannel('oai-events')
      task.channel = channel
      channel.onmessage = event => this.handleEvent(task, event)
      channel.onerror = () => this.fail(task, 'The voice connection failed. Text chat is still available.')
      peer.onconnectionstatechange = () => {
        if (this.alive(task) && ['failed', 'disconnected'].includes(peer.connectionState)) this.fail(task, 'The voice connection was lost. The microphone has been released.')
      }
      peer.ontrack = event => {
        if (!this.alive(task)) { event.track?.stop(); return }
        this.audio.srcObject = event.streams?.[0] || this.makeStream(event.track)
        this.enableAudio(task)
      }
      this.publish(task, 'connecting', 'Connecting voice…')
      const offer = await peer.createOffer()
      if (!this.alive(task)) return false
      await peer.setLocalDescription(offer)
      if (!this.alive(task)) return false
      await this.waitForIce(task)
      if (!this.alive(task)) return false
      task.requested = true
      const answer = await this.request('/voice/sessions', { method: 'POST', body: { request_id: task.id, sdp: peer.localDescription.sdp } })
      if (!this.alive(task)) {
        // A canceled POST may already have created a remote session. Ask the backend
        // to close that owned attempt; never apply a stale answer to a new peer.
        this.closeRemote(task)
        return false
      }
      task.maxSeconds = answer.max_session_seconds
      task.sessionId = answer.session_id
      await peer.setRemoteDescription({ type: 'answer', sdp: answer.sdp })
      if (!this.alive(task)) return false
      if (!task.active) task.startDeadline = this.later(task, () => this.fail(task, 'Voice did not become active. Text chat is still available.'), 10000)
      return true
    } catch (error) {
      if (!this.alive(task)) return false
      const message = error?.name === 'NotAllowedError' ? 'Microphone permission was denied. You can keep using text chat.'
        : error?.name === 'NotFoundError' ? 'No microphone was found. You can keep using text chat.'
        : error?.message || 'Voice could not start. You can keep using text chat.'
      await this.fail(task, message)
      return false
    }
  }
  waitForIce(task) {
    const peer = task.peer
    if (peer.iceGatheringState === 'complete') return Promise.resolve()
    return new Promise((resolve, reject) => {
      const cleanup = () => { peer.removeEventListener('icegatheringstatechange', changed); this.cancel(timer); task.cancelIce = null }
      const changed = () => { if (peer.iceGatheringState === 'complete') { cleanup(); resolve() } }
      const timer = this.later(task, () => { cleanup(); reject(new Error('Voice connection preparation timed out. Text chat is still available.')) }, 8000)
      task.cancelIce = () => { cleanup(); reject(new Error('Voice setup canceled.')) }
      peer.addEventListener('icegatheringstatechange', changed)
    })
  }
  handleEvent(task, event) {
    let data
    try { data = JSON.parse(event.data) } catch { return }
    if (data.type === 'session.closed') {
      task.confirmed = true
      task.closedSignal?.()
      if (this.alive(task)) this.end('remote-close')
      return
    }
    if (!this.alive(task)) return
    if (data.type === 'session.started') {
      if (task.active) return
      task.active = true
      this.cancel(task.startDeadline)
      this.publish(task, 'active', 'Microphone on. You can interrupt or end at any time.')
      this.later(task, () => this.end('duration-limit'), Math.min(300, task.maxSeconds || 300) * 1000)
    } else if (data.type === 'error') {
      // Never render raw provider errors, event snapshots, audio, or transcripts.
      this.fail(task, 'Voice reported an error. Text chat is still available.')
    }
  }
  async enableAudio(task = this.task) {
    if (!this.alive(task)) return
    try {
      await this.audio.play()
      if (this.alive(task)) this.publish(task, this.state, task.muted ? 'Microphone muted. Audio and the paid session continue.' : 'Assistant audio enabled.', false)
    } catch {
      if (this.alive(task)) this.publish(task, this.state, 'Select Enable assistant audio to hear the response.', true)
    }
  }
  mute() {
    const task = this.task
    if (!this.alive(task) || !['active', 'muted'].includes(this.state)) return
    task.muted = !task.muted
    task.stream.getAudioTracks().forEach(track => { track.enabled = !task.muted })
    this.publish(task, task.muted ? 'muted' : 'active', task.muted ? 'Microphone muted. Audio and the paid session continue.' : 'Microphone on. You can interrupt or end at any time.')
  }
  releaseMedia(task) {
    task.stream?.getTracks().forEach(track => track.stop())
    // Audio belongs to the current task. A stale cleanup must not silence a new one.
    if (this.task === task) {
      this.audio.pause()
      this.audio.srcObject?.getTracks?.().forEach(track => track.stop())
      this.audio.srcObject = null
    }
  }
  releaseTransport(task) {
    task.cancelIce?.()
    task.timers.forEach(timer => this.cancel(timer))
    task.timers.clear()
    if (task.channel) { task.channel.onmessage = null; task.channel.onerror = null; task.channel.close() }
    if (task.peer) { task.peer.ontrack = null; task.peer.onconnectionstatechange = null; task.peer.close() }
  }
  closeRemote(task) {
    if (!task.requested || task.confirmed) return Promise.resolve(task.confirmed)
    return this.request('/voice/sessions/' + task.id + '/close', { method: 'POST', body: {} , keepalive: true })
      .then(result => {
        task.confirmed ||= result.closed
        if (this.task === task && this.state === 'closed' && task.confirmed) this.publish(task, 'closed', 'Microphone released. Voice session closure confirmed.')
        return task.confirmed
      }).catch(() => false)
  }
  end(reason = 'end') {
    const task = this.task
    if (!task || task.ended) return task?.ending || Promise.resolve()
    task.ended = true
    this.releaseMedia(task) // no network operation can delay microphone release
    task.timers.forEach(timer => this.cancel(timer))
    task.cancelIce?.()
    this.publish(task, 'closing', 'Microphone released. Closing the voice session…')
    const remote = this.closeRemote(task)
    task.ending = (async () => {
      if (task.channel?.readyState === 'open' && !task.confirmed) {
        await new Promise(resolve => {
          const timer = this.schedule(resolve, 600)
          task.closedSignal = () => { this.cancel(timer); resolve() }
          try { task.channel.send(JSON.stringify({ type: 'session.close' })) } catch { task.closedSignal() }
        })
      }
      this.releaseTransport(task)
      this.publish(task, 'closed', task.confirmed ? 'Microphone released. Voice session closure confirmed.' : 'Microphone released. Provider closure is not yet confirmed.')
      // Remote cleanup may complete after the local controls have finished closing.
      remote.then(() => {})
    })()
    return task.ending
  }
  async fail(task, message) {
    if (!this.alive(task)) return
    await this.end('error')
    this.publish(task, 'error', message)
  }
}
