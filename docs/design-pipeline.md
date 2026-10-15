# Part One design — paced breathing

October 15, 2026. The student selected paced breathing. This interaction and
architecture proposal was drafted with AI assistance for student review.
It describes planned behavior, not an implemented or clinically evaluated app.

## Task, scope and sources

Alex is a fictional student between study tasks who wants to try a brief exercise
without describing feelings. Offer six cycles: inhale for four seconds, exhale
for six. The first version supports one skill. Grounding, STOP, reframing,
speech, accounts and clinical assessments are outside the initial scope.

The research source is the supplied R1–R4 / D1–D6 table. Its mention counts
describe participant feedback, not clinical effectiveness. The assignment's
skill descriptions supply reviewed domain content. The startup and Figma
activities supply development context. No additional dataset is required.
The optional Kaggle page could not be inspected beyond its title; no dataset
conversations were used.

## Main experience

See [the flow and screen sketches](flow.md), including the editable FigJam link
and repository-local flow. Repeated support edges are omitted for readability;
the support control is present in every view/state.

| View | Main content/action | Other choices and failure behavior |
| --- | --- | --- |
| Entry | “Paced breathing · about 60 seconds” and Start | Show display choice; optional explanation/questions, history, preference reset and support. No mandatory intake. Start never waits for chat. |
| Exercise | One phase: Inhale or Exhale, countdown, secondary cycle number | Stop and support stay visible. Text cue is default; optional ring uses the same timer. No chat or dashboard. |
| Support / paused | Freeze the current phase; display support information | Stop remains available. Closing support shows Resume and Stop; never resume automatically. Stop exits immediately. |
| Result | Neutral “Exercise finished” or “Exercise stopped,” plus actual save status | Optional history, entry or another attempt. No praise, streaks, penalty, restart pressure or required emotional rating. |
| History | Ordered actual messages and session table | Show time, duration and completed/stopped/interrupted status. No model call. Distinct empty/loading/failure states. |

Support belongs to the persistent Vue application shell. Chat errors must not
unmount it or cover it. On narrow screens, Stop/support remain reachable without
scrolling past a large graphic. Move focus into support when opened and back to
Resume/Stop when closed. Announce phase changes, not every countdown tick, to
screen readers. Use text labels, visible focus and adequate hit areas.

If the tab becomes hidden or a large timer gap occurs, stop the cue and mark the
attempt interrupted; never rush missed phases or silently mark completion.
A fresh explicit Start creates another attempt. Unexpected interruptions are
recorded separately, not excluded to improve the reported duration.

## Timing and assumptions

Six cycles × (4-second inhale + 6-second exhale) = **60 seconds intended time**.
At 0–4 seconds show Inhale; 4–10 Exhale; repeat through the final exhale at
54–60. Completion follows the sixth exhale, not the start of cycle six.

Measure first displayed exercise instruction through the final planned step,
including render/scheduling delays. Use one monotonic clock and derived phase
boundaries, rather than chained timers that accumulate drift. Target 60 seconds;
completed attempts must later be measured against the ≤90-second assignment
limit. There is no measured app duration yet.

Assume Alex follows automatic cues without typing or pressing Next. Estimate
entry/setup separately at 5–15 seconds for first use, to be measured later.
Optional chat/history is user-chosen setup and has no forced deadline. Model
calls and database writes must not block the cue path, Start, Stop or support.

Record wall-clock elapsed time and excluded user-pause/support time so active
duration is reconstructable. Resume continues the remaining phase. A pause
does not force completion or exit. A failed save says Not saved and does not
change the actual exercise outcome. The 60-second calculation is a design
assumption, not proof of browser timing or effectiveness.

## Research decisions, alternatives and tradeoffs

| Finding | Proposed decision and reason | Alternative / accepted tradeoff | Planned check |
| --- | --- | --- | --- |
| R1: short duration | Six 4/6 cycles target 60 seconds | 90 seconds offers more cycles; accept less practice for lower time demand | Measure first instruction to final exhale including delays |
| R2: frictionless crisis access | Direct, labeled support control opens bundled information | A menu saves space but adds navigation; accept a permanent control | Open from all views and failures without model/backend |
| R3: permission to stop | Immediate Stop; record stopped neutrally | Confirmation avoids mistakes but adds a barrier; accept accidental exits | Stop in both phases and while paused; no surviving timer |
| R4: user controls journey | Explicit Start/Resume; optional questions/history; changeable display | Automatic routing reduces choices but removes control | Start without chat; leave, change settings and return |
| D1: contraction | Hide optional chat/history during exercise; user-selected text-only cue | Automatic distress-based contraction lacks a reliable signal | Change display manually; essential controls remain |
| D2: atomic skill | Show only the current breathing action | Both instructions together preview the sequence but add reading | Inspect representative inhale/exhale states |
| D3: low emotional cost | No required questionnaire, disclosure, rating or exercise typing | Intake might tailor a greeting; accept less personal context | Complete an attempt with no typed content |
| D4: persistent safety | Support is a shell control across views/errors and pause | Chat-only safety can disappear; accept fixed space | Simulate timeout/backend failure; check visibility/focus |
| D5: low-burden personalization | Remember explicit cue/context choices, visibly change/reset | Inferring preferences from stopping could misread behavior | Persist/restart/change/reset; no emotional inference |
| D6: neutral, low stimulus | Text countdown default; optional restrained ring; neutral wording | Praise/celebration adds demand; accept a quieter result | Check reduced motion, contrast, focus, language, narrow width |

One initial skill is easier to follow but limits R4's range of skill choices.
Preserve choice of whether/how to participate and do not claim universal
suitability. Counts of starts/stops/completions are behavior, not emotional states.

## Personalization and useful history

Remember cue_mode (text or ring) after an explicit change. Respect the browser's
reduced-motion preference even if ring was previously chosen; show the effective
setting and let it change. Remember use_saved_context, default false, for
including previous conversations/sessions in optional chat. Current-conversation
continuity and reviewed skill content remain available. Show when saved context
is used; let users turn it off and Reset preferences.

No mood score, auto-start, inferred diagnosis, hidden duration change or setup
questionnaire. With one skill, “use my usual skill” adds no meaningful choice;
personalize presentation/context rather than inventing a recommendation system.
Settings can become stale, so keep them visible and changeable.

History has conversation messages and a session table: skill/version, start/end,
active duration, excluded pause/support time and outcome. Retain stopped attempts
neutrally. No health-improvement chart. Offer history deletion with explicit
confirmation because it removes records; this must never block exercise exit.
Preferences reset separately. This is a single fictional demo user on localhost,
without authentication or production privacy guarantees.

## Model role and two-call SQL RAG

Optional questions before/after the exercise explain reviewed steps or recall
factual activity. Example: fictional Alex asks, “What display did I use last
time?” With saved-context permission, retrieve and identify the actual record.
If missing, say there is no saved information. Do not infer benefit, evaluate
symptoms or prescribe treatment.

The model never controls timing, steps, Stop, support visibility, navigation or
writes. No generated introduction is needed to start. A late reply is saved for
later conversation review and must not appear over an exercise. Match request
IDs and ignore superseded UI updates. Render brief plain-text replies.

1. Validate the question and save the submitted message with a stable request ID.
   Send question and relevant schema to the query-planning model call.
2. Validate one simple SELECT from a server-created context_records view. The
   view scopes messages to this conversation and includes this demo user's past
   sessions/preferences/conversations only with saved-context permission.
   Model SQL cannot choose another user or override this scope.
3. Allow only declared columns, bounded kind filters and ordering. Reject writes,
   joins, comments, UNION, arbitrary functions, base-table access and additional
   statements. Use read-only SQLite, query_only, an authorizer, execution budget,
   at most 10 rows and at most 8,000 context characters.
4. Send retrieved IDs/records and reviewed skill content/version to a second
   answer call. Treat stored text as data, not overriding instructions. Require
   supporting IDs for history claims and honest handling of missing records.
5. Validate response shape/length/references, save the actual reply through the
   normal parameterized write path, and report accurate persistence status.

Worked permitted query:

    SELECT record_id, kind, occurred_at, content
    FROM context_records
    WHERE kind = :kind
    ORDER BY occurred_at DESC LIMIT 10

Validate kind as message/session/preference. Build the view's scope in trusted
backend code. Checking only a SELECT prefix is insufficient. Retrieval cannot
write messages, settings or outcomes.

Plan two calls per accepted question, finite 15-second provider timeouts, no
automatic retries, and one active question at a time. Manual retry uses a new
attempt under the same request ID without duplicating the submitted message.
Count both calls; use mocks by default and no more than 50 live calls in a peer
session. Provider/model selection remains an implementation question; do not
assume the earlier travel model is currently available.

Shape/reference validation does not prove semantic or clinical correctness.
Reviewed content, prompt boundaries and fictional checks constrain scope; they
do not establish a clinically effective or reliable support system.

## Crisis-related input and independent support

Support is present regardless of text, classifier decisions or model results.
Bundle its information in the frontend so it opens during backend/provider
failure. Use clearly labeled U.S. classroom-demo resources, verify official
destinations and record dates before implementing usable resource content.
Region coverage is limited; do not infer location from IP/account data.

For optional chat, propose an application-owned phrase heuristic after
case/whitespace normalization. Phrases such as “kill myself,” “end my life,” or
“hurt myself” trigger a fixed coursework-boundary/support notice and skip both
model calls. Save the submitted message and a separate application event; never
present fixed copy as a model reply. Do not automatically start an exercise,
claim someone was alerted, or lock the person into a flow.

This is limited text matching, not distress detection or risk assessment. It can
misread negation/quotation and miss indirect wording, languages or new phrases.
A nonmatch is not evidence of safety. Model instructions also prohibit diagnosis,
therapy, invented advice and monitoring claims, but do not replace the independent
route. Resource copy/destinations and heuristic cases need review before use.

## Architecture, records and API plan

Vue views/state call FastAPI via HTTP/JSON. Small routes validate; controllers
coordinate chat/history; repositories perform transactions. Only Python opens
data/app.sqlite3 resolved from the project root. Explicitly load backend/.env,
keep it ignored, and never copy the travel .env or database. No packages,
environment files, server or database were created for this design milestone.

| Planned table | Main fields / relationships |
| --- | --- |
| demo_users | ID; one fictional local demo identity |
| conversations | ID, demo_user_id FK, created_at |
| messages | ID, conversation_id FK, sequence, role, content, created_at, request_id; unique conversation/sequence and request/role |
| requests | ID, conversation_id FK, submitted_message_id FK, status/error_code; provider attempts linked by separate attempt IDs |
| sessions | ID, demo_user_id FK, optional conversation_id FK, skill/version, cue_mode, start/end, wall_ms, excluded_ms, active_ms, outcome |
| preferences | demo_user_id PK/FK, cue_mode, use_saved_context, updated_at |
| skill_content | ID/version, reviewed steps/explanation; idempotent seed without overwriting runtime history |
| app_events | ID, conversation_id FK, optional request_id FK, type/time; fixed support notices distinct from model replies |

Use migrations, foreign keys, transactions and parameterized writes. UUID request/
session IDs make retry idempotent. Resume is the same session. On refresh,
reconcile an acknowledged in-progress record to interrupted, never completed.
Do not auto-resume. Unsaved results can remain in memory for explicit Retry save;
disclose that closing the page can lose them. Mock history does not establish
SQLite persistence.

| Endpoint (planned) | Input | Success / failure |
| --- | --- | --- |
| POST /api/conversations | demo context | 201 stable ID; 503 storage |
| POST /api/conversations/{id}/messages | UUID request ID, nonblank question ≤1,200 characters | 200 reply/records/save status or fixed app event; 422 input/retrieval rejected, 429 busy, 502 provider/invalid reply, 504 timeout, 503 configuration/storage |
| GET /api/conversations | server scope, bounded cursor | 200 list/empty; 503 storage; no model call |
| GET /api/conversations/{id}/messages | scoped ID/cursor | 200 ordered messages and request/app-event states; 404 unknown; 503 storage |
| PUT /api/sessions/{id} | UUID, fixed skill/version, valid state/timing | 200 acknowledged record; idempotent final save; 409 conflicting outcome, 422 invalid, 503 storage |
| GET /api/sessions | server scope, bounded cursor | 200 rows/empty; 503 storage; no model call |
| GET / PUT /api/preferences | allowed cue/context fields on PUT | 200 actual settings; 422 invalid, 503 storage; reset uses defaults |
| DELETE /api/history | explicit confirmed scoped request | 204 transactional deletion of sessions/conversations/messages/requests/events; retain preferences/content; 503 storage |

Failures return safe code/message/request ID without credentials, exception dumps
or provider URLs. Failed initial message save prevents model calls while Start/
support remain usable. A generated reply whose save fails is shown as unsaved,
retained for save retry and never falsely marked persistent.

## Lessons and planned reuse from Travel Application

The local Brian Booking Plus source and older Git history were inspected
read-only. Current renamed source includes uncommitted work not represented by
the older branch head. No application code or data has been copied yet.

| Source/pattern | Adaptation / important difference |
| --- | --- |
| frontend/vite.config.js | Vue-to-FastAPI /api proxy; choose ports that preserve existing travel servers |
| backend/hotel_llm.py | Backend-only calls, bounds, safe errors; new config and optional-chat timeout |
| backend/hotel_chat.py | Restricted SQL planning then grounded answer; new scoped context_records view |
| backend/hotel_chat_routes.py | Typed input/thin routes; add stable IDs and persistence outcomes |
| backend/database.py | Transactions, foreign keys, connection cleanup; new schema, no hotel CSV/data |
| frontend/src/HotelChat.vue | Loading/error/plain-text/focus patterns; add independent Stop/support and stale-response handling |
| Reports/fixtures/handoffs | Separate mock/live evidence and preserve failures; hotel checks do not verify this app |

The hotel chatbot did not persist conversations. New conversation/session storage
is required; an in-memory chat draft is not saved history. The hotel's extensive
SQL/record display aids developer verification but would add reading during
breathing; keep developer traces outside the guided view.

## Alternatives, open questions and next milestone

Selected proposal: emphasize Start and make explanation secondary. Alternative:
a longer model introduction above Start. The proposal reduces reading and avoids
provider-dependent entry (D3/R4), at the cost of less up-front explanation.

Open implementation questions: which available model fits the contract; which
verified regional resource copy to bundle; whether cues are understandable at
narrow widths and with assistive technology; heuristic false matches/misses in
fictional scenarios; and whether restricted SQL answers useful history questions.
Use later mock/browser/database checks and a small live-model selection.

Figma is connected and a FigJam flow was generated. No running Vue interface was
captured or implemented from a Figma Design frame. That optional class round trip
remains later work. Part One's flowchart does not establish runtime behavior.
