// One monotonic clock owns all phases. Rendering and saving never schedule the steps.
export class Pacer {
  constructor(now) {
    this.started = now
    this.last = now
    this.excluded = 0
    this.pauseAt = null
    this.state = 'running'
    this.ended = null
  }
  sample(now) {
    if (this.state !== 'running') return this.snapshot(now)
    if (now - this.last > 1500) return this.finish('interrupted', now)
    this.last = now
    if (now - this.started - this.excluded >= 60000) return this.finish('completed', now)
    return this.snapshot(now)
  }
  pause(now) {
    this.sample(now)
    if (this.state === 'running') {
      this.pauseAt = now
      this.state = 'paused'
    }
    return this.snapshot(now)
  }
  resume(now) {
    if (this.state === 'paused') {
      this.excluded += now - this.pauseAt
      this.pauseAt = null
      this.last = now
      this.state = 'running'
    }
    return this.snapshot(now)
  }
  finish(outcome, now) {
    if (this.ended !== null) return this.snapshot(now)
    if (this.pauseAt !== null) {
      this.excluded += now - this.pauseAt
      this.pauseAt = null
    }
    this.ended = now
    this.state = outcome
    return this.snapshot(now)
  }
  snapshot(now) {
    const end = this.ended ?? now
    const wall = Math.max(0, Math.round(end - this.started))
    // Round active time itself so fractional pause samples cannot make a saved
    // active duration move backwards by 1 ms when wall/excluded round separately.
    const active = Math.min(wall, Math.max(0, Math.round((this.pauseAt ?? end) - this.started - this.excluded)))
    const excluded = wall - active
    const position = Math.min(active, 59999) % 10000
    return {
      state: this.state, wall_ms: wall, excluded_ms: excluded, active_ms: active,
      phase: position < 4000 ? 'Inhale' : 'Exhale',
      remaining: Math.ceil(((position < 4000 ? 4000 : 10000) - position) / 1000),
      cycle: Math.min(6, Math.floor(active / 10000) + 1),
      ringScale: position < 4000 ? 0.78 + 0.22 * position / 4000 : 1 - 0.22 * (position - 4000) / 6000,
    }
  }
}
