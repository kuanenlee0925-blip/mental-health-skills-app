import test from 'node:test'
import assert from 'node:assert/strict'
import { Pacer } from './pacer.js'

function advance(pacer, start, end) {
  for (let t = start; t <= end; t += 100) pacer.sample(t)
}
test('all twelve phases complete only after the final exhale, including scheduling delay', () => {
  const p = new Pacer(0)
  const observed = []
  for (let t = 0; t < 60000; t += 100) {
    const s = p.sample(t)
    if (t % 10000 === 0 || t % 10000 === 4000) observed.push([s.cycle, s.phase])
    assert.equal(s.state, 'running')
  }
  assert.equal(observed.length, 12)
  assert.deepEqual(observed.at(-1), [6, 'Exhale'])
  assert.equal(p.sample(60087).active_ms, 60087)
  assert.equal(p.state, 'completed')
})
test('support pause freezes remaining cue and explicit resume excludes pause time', () => {
  const p = new Pacer(0)
  advance(p, 0, 2300)
  p.pause(2350)
  assert.equal(p.snapshot(12350).active_ms, 2350)
  assert.equal(p.snapshot(12350).remaining, 2)
  p.resume(12350)
  assert.equal(p.sample(12450).active_ms, 2450)
  p.finish('stopped', 12500)
  assert.equal(p.snapshot(99999).excluded_ms, 10000)
  assert.equal(p.snapshot(99999).active_ms, 2500)
})
test('Stop is terminal; future timer callbacks cannot complete the attempt', () => {
  const p = new Pacer(0)
  advance(p, 0, 4000)
  p.finish('stopped', 4050)
  assert.equal(p.sample(70000).state, 'stopped')
  assert.equal(p.sample(70000).active_ms, 4050)
})
test('large scheduling gaps interrupt instead of catching up or inventing completion', () => {
  const p = new Pacer(0)
  p.sample(100)
  assert.equal(p.sample(65000).state, 'interrupted')
  assert.equal(p.sample(65000).active_ms, 65000)
})
test('stopping during support counts support time only as excluded', () => {
  const p = new Pacer(0)
  p.pause(100)
  const final = p.finish('stopped', 10100)
  assert.equal(final.wall_ms, 10100)
  assert.equal(final.excluded_ms, 10000)
  assert.equal(final.active_ms, 100)
})

test('fractional pause samples keep active time stable across checkpoints and Stop', () => {
  const p = new Pacer(100.2)
  p.pause(1000.6)
  const checkpoint = p.snapshot(5100.8)
  const later = p.snapshot(5101.2)
  const final = p.finish('stopped', 6100.4)
  for (const s of [checkpoint, later, final]) {
    assert.equal(s.active_ms, 900)
    assert.equal(s.wall_ms, s.active_ms + s.excluded_ms)
  }
})
