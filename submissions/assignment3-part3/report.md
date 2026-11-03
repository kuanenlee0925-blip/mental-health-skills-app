# Assignment 3 — Part Three: Integration, Evaluation, and Demonstration

A Little Space · Paced breathing · November 2, 2026

**Status: local draft; not yet ready for submission.** The implementation and
mock/browser evaluation below are complete. The live selection is complete and exposed two quality problems; the prompt
revisions remain unverified live. Finished recordings, a published submission
commit, and the independent clean-checkout check still need completion. No missing evidence is presented as passed.

Repository: https://github.com/kuanenlee0925-blip/mental-health-skills-app

Submitted commit: **pending**. Work is on local `codex/part3-refinement`, based on
`20ad2fad3c3eece7678db12fcd9ce8e3418c3626`. That base commit does not contain the
Part Two/Three implementation. Do not submit it as the implemented version.

## What is implemented

A localhost Vue/JavaScript interface, Python/FastAPI backend and SQLite database
support one complete paced-breathing skill: six 4-second inhales and 6-second
exhales. Application code owns timing, Pause/Resume, Stop and the independent
crisis-support route. Optional text chat uses a two-call SQL RAG pipeline: propose
a query, validate and execute a bounded scoped read, then answer from reviewed
skill material and the retrieved records. The model never opens SQLite or
changes the exercise sequence.

The app stores actual submitted messages/replies, stable request IDs, failures,
exercise outcomes/timing and explicit preferences. History displays these records;
it never turns activity counts into emotional or clinical claims. Saved-history
sharing starts off and can be changed. The single fictional local profile has
text/ring display, standard/large text and history-sharing choices. Reusing a
previous display takes an explicit click. There is no required questionnaire.

Part Three adds direct Pause and saved Larger text. An additive schema migration
preserves existing history. No additional dependencies were installed. Optional
voice remains mock-tested only, and is not used as evidence of a working live
provider. The app is a coursework prototype, not therapy, diagnosis or monitoring.

## Revisiting the design

The Part One design kept one cue at a time, a 60-second target, optional chat,
and visible Stop/support. Those choices remain grounded in R1–R4 and D1–D6.
Implementation showed that resting should not require opening crisis support:
a direct Pause action adds a small amount of UI while improving control (R3/R4).
Larger text is inside optional saved choices, balancing reading access with
configuration effort (D5/D6). Adaptation uses explicit choices and navigation,
not inferred distress. One skill limits variety but avoids a demanding library
(D2/D3). Full decisions and tradeoffs: [design review](../../docs/part3-design-review.md).

## Evaluation and observed evidence

- [18 fictional scenarios](../../docs/part3-evaluation.md), including ordinary
  conversation, consent changes, pause/stop, interruptions, retry, missing
  configuration, rejected SQL and storage/provider failures. Every row has an
  expected result and an observed assertion outcome. All 18 passed using mocks
  or simulated clocks; none is represented as a live-model observation.
- Three explicit cross-case checks passed: no invented/duplicate saved replies
  across retry/failure/restart; retrieval obeys consent/scope and rejects unsafe
  SQL; only the final planned phase completes an exercise.
- All 22 backend and 18 frontend tests passed; Vite production build passed.
- Actual November 2 Chrome run: **60.013 seconds active**, no excluded pause,
  **1.015 seconds setup**. The full six-cycle sequence was allowed to finish.
  A separate Pause/support/Resume/Stop run recorded 0.891 seconds active,
  69.355 seconds excluded and 5.640 seconds setup.
- Larger text survived browser refresh; the paused exercise's Resume, Stop and
  support remained reachable at 390 × 640. A failed demo request and retry left
  one failed user message, and support still opened. Read-only SQLite agreed
  with the API by record IDs; schema version 2 had no foreign-key violations.
- [Clean source reproduction](../../docs/part3-clean-checkout.md) passed tests,
  build and fresh empty-database startup while reusing installed dependencies.
  This is not a claim of a fresh dependency install or independent peer testing.

[Verification notes](../../docs/verification.md),
[machine-readable scenarios](../../docs/evidence/part3-scenarios.json),
[database/API evidence](../../docs/evidence/part3-record-check.json),
[completed exercise screenshot](../../docs/evidence/part3-completed.png),
[paused mobile screenshot](../../docs/evidence/part3-narrow-paused.png),
[failure screenshot](../../docs/evidence/part3-chat-failure.png).

### Live-model variation — completed with failures

Used OpenRouter `openai/gpt-4.1-mini`, with three fictional cases repeated twice:
**12 calls total**. All six API requests succeeded and actual saved replies
matched SQLite, but content review found **3 pass, 2 fail, 1 partial**. Both
history-on replies missed the available saved practice. History-off replies
correctly admitted missing context. Both boundary replies declined diagnosis
and duration changes, but one invented a ring sound; the ring is visual.

[Full expected/observed review and variation](../../docs/part3-live-evaluation.md)
and [actual outputs/records](../../docs/evidence/part3-live.json) preserve these
results. The history-on wording was identical but references differed; boundary
wording differed, including the unsupported sound claim. Fresh conversations
shared the same temporary fixture database, so this was repeated app behavior,
not a controlled identical-context experiment.

Clarified the retrieval prompt's practice/session mapping and the answer prompt's
visual-ring meaning. Deterministic checks passed after the revision. The student
chose to keep the 12-call limit, so **the revised prompts remain unverified live**.
A valid record ID does not prove relevant or semantically grounded use of it.

### Surprising finding and untested limitation

A paused timer once saved a checkpoint that decreased by **1 millisecond**.
Separately rounding wall and excluded time caused the difference, and the API's
monotonic guard correctly rejected it. The fix rounds active time directly,
then derives excluded time. The old unfinished row remains as evidence, and a
fractional-time regression case now passes. This shows why “saved” needs actual
persistence evidence, not just a pleasant completion screen.

Real screen-reader use and long-term usability have not been tested. A small
fictional evaluation cannot establish clinical effectiveness or prove that a
model always obeys its limits. The phrase-based application notice covers only
specific wording; support therefore stays available independently of detection.

## Demonstration and process screencast

Finished application recording: **pending — insert an accessible video link**.

Process recording: **pending — insert an accessible video link**.

[Recording script](../../docs/part3-recording-guide.md) and
[process evidence page with code explanation](../../docs/evidence/part3-process.html)
are prepared. They are not recordings. The process demonstration should show
`[demo:fail]`, the preserved failed message/no duplicate retry, independent
support, the rounding evidence, and an explanation of `Pacer.snapshot`.

## Reproduction and AI disclosure

Follow [README](../../README.md). Peers should use demo mode with fictional
inputs and no provider key. [AI-USE.md](../../AI-USE.md) and the
[curated Part Three prompt/change log](../../prompts/03-part3-refinement.md)
disclose generated code, evaluation, documentation and revised approaches.
Student understanding and review have not been assumed.

Before uploading this report: review the live findings and finish the recordings,
verify the clean checkout, commit/publish the reviewed source and evidence,
replace the pending commit and video links, and convert relative evidence links
to accessible GitHub links pinned to that actual commit. No Canvas submission
has been made.
