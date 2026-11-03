# Part Two implementation contract

October 22, 2026. Implements the selected Part One flow on the
`codex/part2-implementation` branch. Original report.md stays unchanged.

## Increment and checks

Create Vue views in frontend/src; FastAPI models, storage, retrieval and
controllers in backend; SQLite at data/app.sqlite3. Preserve the 4/6 × 6
sequence, explicit Stop/Resume, static support, and optional conversation flow.
First verify backend storage and error behavior, then a browser/API/database
round trip, timing, stop/pause, provider failure and restart persistence.

October 25 presentation increment: the optional home disclosure Your saved
choices combines GET /preferences with the newest GET /sessions record. It
shows actual display/context choices and observed practice outcome/time. The
Use last practice’s display action calls the existing preference PUT only after
an explicit click; it never starts an exercise or infers feelings. Loading/empty/
failure states remain distinct and never block Start. Preference values are
labeled saved only after an acknowledged load/save. No new schema or model call.
The same single local identity owns both preferences and usage history. This
small profile supports D5/R4 while avoiding a mandatory configuration screen.

## Wire contract

All routes start with /api. IDs are UUIDs. JSON error bodies contain
`error: {code, message}`; validation errors use the same envelope. No provider
exception contents or secrets reach the browser. A single fictional demo user
owns all records. Bind only to localhost; there is no authentication.

| Method and path | Input | Output |
| --- | --- | --- |
| GET /health | None | mode, configured flag, call counts; no values of credentials |
| POST /conversations | `{id}` | id and created_at; idempotent |
| GET /conversations | None | ordered conversation rows, at most 100 |
| GET /conversations/{id}/messages | UUID | ordered messages, requests, app events |
| POST /conversations/{id}/messages | `{request_id, content}` (1–1200 chars) | saved actual reply and retrieved record IDs, or fixed app event; mode labeled |
| PUT /sessions/{id} | start/end ISO UTC, outcome, cue_mode, wall_ms, excluded_ms, active_ms | persisted session; idempotent final save, 409 on conflict |
| GET /sessions | None | newest 200 sessions |
| GET /preferences | None | cue_mode, use_saved_context, updated_at |
| PUT /preferences | `{cue_mode: text|ring, use_saved_context: boolean}` | stored preferences |
| DELETE /history | `{confirm: true}` | deleted count; retains preferences |
| GET /voice/config | None | configured flag and max_session_seconds; no key/prompt/model details |
| POST /voice/sessions | `{request_id: UUID, sdp: string}`; 20–65536 chars, audio/ICE/DTLS SDP, no extra fields | session_id, validated SDP answer, max_session_seconds; 422 bad input, 503 unconfigured, 409 duplicate/canceled, 429 busy/limit, 502 provider/answer, 504 timeout |
| POST /voice/sessions/{request_id}/close | UUID identifying a server-owned attempt | `{closed: boolean, pending: boolean}`; late starts are canceled/closed; unconfirmed remote closure is not reported as success |

Session outcomes: in_progress, completed, stopped, interrupted. Client-generated
UUID plus revision prevents a delayed start/checkpoint from overwriting a final
result. All durations are nonnegative milliseconds; active = wall − excluded.
Completed sessions require 60–90 seconds active. Entry/setup time is separate.
Round active time directly and derive excluded time from rounded wall duration;
this prevents fractional pause samples from reducing active time by 1 ms. The
backend rejects backward durations and terminal-result replacement. The support
header stays visible while scrolling; support remains bundled in the frontend.
Interrupted sessions record the last observed cue time; unattended time cannot
be reconstructed after a browser crash and is not labeled a completion.

Example: PUT /sessions/<uuid> with revision 1, stopped, wall_ms 6000,
excluded_ms 2000, active_ms 4000 stores a stopped four-second attempt. Repeating
the identical operation returns the same row, never an additional session.

Message retries retain one request UUID and one user message. A failed model
request has no invented assistant message. The two-call retrieval path records
attempt IDs, actual calls and selected record IDs. Demo mode exercises the same
path with labeled fixture responses; it is not live-model evidence. A generated
reply that cannot be saved returns a storage error, never an apparent saved reply;
retry may regenerate it. This is a deliberate smaller scope than the Part One
proposal's in-memory unsaved-reply cache. Session save retries retain exact data.

The model chooses only a strictly parsed query over a server-scoped view. No
arbitrary SQL is accepted. Read-only SQLite, an authorizer, progress handler,
10-row and 8000-character limits provide additional controls. A history-off
request sees only its conversation. Settings/history changes serialize with chat
to prevent deleting records or changing context consent midway through a call.

## Provider and resource decisions

Default: deterministic demo mode. Live mode uses a separately configured
OpenRouter key/model in ignored backend/.env, 15-second timeout per call, no
automatic retries, maximum 50 calls per process (both stages count). No fallback
to a different/paid model. Travel credentials are not copied.

U.S. support content verified October 22, 2026 with the connected helpline
lookup: 988 Suicide & Crisis Lifeline, phone/SMS 988 and official chat/site
destinations. Bundle those exact returned destinations in Vue. Opening the
panel requires no backend/model/network call; following an external contact
method requires the corresponding phone/network service. U.S. coverage only.

Voice is a separate optional provider path, disabled by default. Backend-owned
OpenAI Live/Responses model names, prompts and event permissions are documented
in [voice notes](voice.md). Default limit: three creation attempts per process,
at most 300 seconds each; the student observation must end before 60 seconds.
This limit is separate from the text adapter's 50-call budget. Voice does not
send saved text history or create database audio/transcript records. Keep peer
testing in mock mode. Real provider use remains unverified.
