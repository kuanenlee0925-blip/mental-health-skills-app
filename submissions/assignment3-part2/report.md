**Publication note — November 2, 2026:** This historical Part Two draft is retained.
The complete implementation is now published in the [Part Three checkpoint](https://github.com/kuanenlee0925-blip/mental-health-skills-app/commit/41bab285ad9b3a085ccc8b8e357ac78e96e11d82).
See the [current Part Three report](../assignment3-part3/report.md) for later live findings and remaining deliverables.

# Assignment 3.2 — Part Two implementation report (draft)

Updated October 25, 2026. Coursework prototype; fictional testing only.

Repository: https://github.com/kuanenlee0925-blip/mental-health-skills-app

**Submitted-version commit: pending.** Implementation is currently local on
`codex/part2-implementation`, based on `20ad2fad3c3eece7678db12fcd9ce8e3418c3626`.
That base commit contains Part One, not this implementation. Before submitting,
commit/publish the reviewed Part Two version and replace this paragraph with its
exact commit and accessible pinned links. This draft has not been submitted.

## Working scope

A person can complete paced breathing through the Vue interface: six cycles of
4-second inhale and 6-second exhale. Text cues are default; a gentle ring is
optional. Start requires no disclosure or chat. Stop exits immediately. Opening
support pauses the current cue; closing it requires explicit Resume or Stop.
Refresh/leaving interrupts rather than completing unseen steps.

FastAPI stores conversation/message IDs, roles, order, times and request states,
plus session timing/outcomes and explicit preferences in SQLite. The history view
shows actual saved records. Saving can fail without blocking the exercise; a
failed result says so and offers retry. Retry uses the same record identifier.

The October 25 presentation increment adds Your saved choices on the home view:
display/context preferences, the latest actual practice, and an explicit action
to reuse its display. This makes the small local profile and history-based UI
personalization inspectable without adding an intake form or inferred emotions.
The [presentation guide](../../docs/presentation-guide.md) provides a 4:40 target
script covering all four criteria. A timed student rehearsal is still needed.

Optional questions use a two-stage retrieval/answer pipeline. A proposed SQL
query is validated against a restricted read-only grammar and server-scoped view;
the answer receives actual records and reviewed skill content. Only application
code writes to SQLite. Saved-history sharing defaults off and remains changeable.
The model cannot change exercise steps, timing, Stop or support visibility.

**The demonstrated text replies are labeled deterministic demo fixtures.** The
live OpenRouter adapter exists, but an actual model contribution has not yet
been demonstrated. This remains a Part Two requirement to finish with locally
configured credentials and a small fictional live check.

The requested live-audio activity adds WebRTC, visible state, Mute/End and
cleanup, with server-owned OpenAI Live and delegated Responses prompts. It has
mock evidence, not a live microphone/provider observation. It stores no voice
audio or transcripts. Text remains usable when voice is unavailable.

## Evidence and findings

| Check | Observed result |
| --- | --- |
| Full desktop exercise, October 22 | Completed in 60.019 seconds; setup 4.147 seconds, excluded pause time zero; saved session 9518bb91-f46b-4ed0-b532-743995c38029 |
| Support pause and Stop | 3.218 seconds active plus 49.709 seconds paused, stored as stopped; closing support focused Resume without continuing automatically |
| Backend unavailable | Exercise and bundled support still worked; failed result visibly offered Retry save; restart and retry saved one result |
| Refresh | Stored interrupted outcome; no automatic resume or completion |
| Conversation persistence | Five ordered messages in a fictional conversation matched SQLite and API; visible message UUID matched; records survived API restart |
| Provider-failure fixture | Repeated failure retained one failed user message, with no invented assistant reply |
| Narrow layout | Checked actual Vue app in a 390 x 568 CSS-pixel iframe; Stop/support reachable; a completed run measured 60.016 seconds |
| Automated checks | 21 backend tests + 18 frontend tests passed; Vite production build passed on October 24 |
| Presentation increment, October 25 | Ring preference survived refresh; reusing the previous practice restored text; SQLite agreed; demo answers changed appropriately with history sharing off/on. Frontend tests and build passed again. |
| Live voice | Missing configuration leaves text usable; media/connection cleanup checked with mocks only |

Timing uses the app's monotonic clock from starting the first cue through the
final step, including scheduling delay. No typing or Next action is required.
Voluntary support pauses are excluded and setup is reported separately. These
measurements establish software behavior, not clinical effectiveness.

A surprising failure occurred while testing pause/Stop: independently rounding
two durations made active time decrease by 1 ms, and the backend correctly
rejected the save. The corrected timer rounds active time directly and derives
excluded time. A regression test and real-browser repetition passed. The old
unfinished record remains visible as failure evidence rather than being rewritten.

## Design reasoning and reuse

R1/D2 support one cue at a time and a 60-second sequence. R2/R3/D4 support a
persistent support control and immediate Stop independent of AI. R4/D3 support
optional questions and no mandatory emotional disclosure. D5 supports explicit,
visible saved preferences; no emotional state is inferred from clicks. D6 informs
neutral copy, text cues and reduced-motion handling. Limiting the app to one
skill reduces choice but keeps the sequence coherent and reviewable.

Travel Application supplied architectural patterns: Vue-to-FastAPI proxy,
backend-only model calls, restricted SQL planning, transaction/error handling.
Its hotel conversation flow did not persist chat history; this app adds a new
schema and history view. No travel keys, database or personal conversations were
copied. Implementation changed the earlier unsaved-reply proposal: a generated
reply whose database write fails is withheld with a storage error; retry may
regenerate it. Session-result retries retain their exact payload.

## Review links (local until the milestone is published)

- [Setup and source responsibilities](../../README.md)
- [Original design and research rationale](../../docs/design-pipeline.md)
- [Implemented API/data contract](../../docs/part2-contract.md)
- [Actual checks, commands and screenshots](../../docs/verification.md)
- [Read-only database/API evidence](../../docs/evidence/part2-record-check.json)
- [Live-audio implementation and remaining manual check](../../docs/voice.md)
- [Curated prompts and revisions](../../prompts/02-part2-and-live-audio.md)
- [AI-use disclosure](../../AI-USE.md)

Relative links work inside a checkout/GitHub. They are not sufficient for a
standalone Canvas upload: replace them with accessible links pinned to the final
submitted commit. No recording has been made for this milestone.

## Still to finish

1. Configure live text credentials locally, demonstrate actual model replies and
   retrieval, and record their saved IDs and call counts separately from fixtures.
2. Complete the optional audio activity's explicit under-60-second microphone
   test and public-demo comparison with an authorized OpenAI account.
3. Review the code/report, commit and publish the selected version, verify access
   to pinned evidence links, then upload this report as report.md to Part Two.

Screen-reader/OS reduced-motion testing, broad browser/hardware coverage,
clean-checkout reproduction by another person and live-model variation are not
verified. The later Part Three evaluation/recording requirements remain later
work. No Figma live capture, clinical effectiveness or monitored service is claimed.
