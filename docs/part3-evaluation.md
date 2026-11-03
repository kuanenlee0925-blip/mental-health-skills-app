# Part Three fictional scenario evaluation

Recorded 2026-11-03T01:41:34.579163+00:00. deterministic fixtures and simulated clock; no live calls.

These observations come from executing assertions in the linked source tests. Timing uses a simulated monotonic clock; browser observations are documented separately.

| ID | Fictional scenario | Expected | Observed |
| --- | --- | --- | --- |
| S01 | Alex asks for the steps, repeats the same request, then restarts the API. | 200 with saved demo reply; same reply ID on retry; exactly two ordered messages after restart. | PASS — All listed assertions passed. |
| S02 | Alex submits [demo:fail] twice with one request ID. | Both return 502; one failed user message, no invented assistant; changing content with that ID returns 409. | PASS — All listed assertions passed. |
| S03 | Fictional role-play includes HURT   myself. | Application support notice, no assistant reply, zero model calls; not a general distress detector. | PASS — All listed assertions passed. |
| S04 | Live settings are absent, then the call budget is zero. | 503 not_configured, then call_limit; zero actual provider calls. | PASS — All listed assertions passed. |
| S05 | An existing v1 profile upgrades, selects larger text, and restarts. | Standard text default; large choice persists; original message ID preserved; invalid size returns 422. | PASS — All listed assertions passed. |
| S06 | Alex stops, retries saving, and a stale checkpoint arrives. | One stopped row; stale checkpoint cannot revert it; terminal overwrite gives 409; 59,999 ms completion gives 422. | PASS — All listed assertions passed. |
| S07 | Alex asks about a past session with sharing off, then on. | Off retrieves no sessions; on retrieves the stopped record and returns its exact reference ID. | PASS — All listed assertions passed. |
| S08 | Alex starts another conversation; a separate fictional user has a record. | No cross-conversation messages without consent; consent never exposes the other user; direct table query rejected. | PASS — All listed assertions passed. |
| S09 | Model proposes a write, extra statement, comment, UNION, wildcard, oversized limit or scope bypass. | All unsafe plans rejected; [demo:unsafe] returns 422; sessions remain readable. | PASS — All listed assertions passed. |
| S10 | Model invents a record ID, then times out. | invalid_references then 504; zero assistant messages persisted. | PASS — All listed assertions passed. |
| S11 | Question storage is unavailable before generation. | 503; zero provider calls; no claim that the operation was saved. | PASS — All listed assertions passed. |
| S12 | Alex deletes fictional history during and after a pending request. | 429 while busy; confirmed deletion then succeeds, keeps ring preference, and has no foreign-key violations. | PASS — All listed assertions passed. |
| S13 | all twelve phases complete only after the final exhale, including scheduling delay | Twelve phases; final phase is sixth exhale; completion at 60,087 ms including scheduling delay. | PASS — All listed assertions passed. |
| S14 | support pause freezes remaining cue and explicit resume excludes pause time | Pause at 2,350 ms freezes cue; explicit resume excludes 10,000 ms; final active time 2,500 ms. | PASS — All listed assertions passed. |
| S15 | Stop is terminal; future timer callbacks cannot complete the attempt | Stop at 4,050 ms stays stopped after a later 70,000 ms callback. | PASS — All listed assertions passed. |
| S16 | large scheduling gaps interrupt instead of catching up or inventing completion | A jump from 100 to 65,000 ms produces interrupted, never completed. | PASS — All listed assertions passed. |
| S17 | stopping during support counts support time only as excluded | Stop during pause records 100 ms active plus 10,000 ms excluded. | PASS — All listed assertions passed. |
| S18 | fractional pause samples keep active time stable across checkpoints and Stop | Fractional pause snapshots all keep active time 900 ms and wall = active + excluded. | PASS — All listed assertions passed. |

## Three cross-case behavior checks

- **B1 — PASS:** Retries, failures, and restarts never invent or duplicate a saved assistant reply. Cases: S01, S02, S10, S11.
- **B2 — PASS:** Retrieved history obeys consent and server scope, and unsafe SQL is rejected. Cases: S07, S08, S09, S10.
- **B3 — PASS:** Only the final planned phase completes an exercise; pauses and interruptions do not silently complete it. Cases: S06, S13, S14, S15, S16, S17, S18.

Reproduce with `backend/.venv/Scripts/python.exe -m scripts.evaluate_part3`. Backend cases use new temporary databases. The delete case affects only its isolated fixture. No paid model or real microphone is used.

Machine-readable evidence and exact test mappings: [part3-scenarios.json](evidence/part3-scenarios.json).
