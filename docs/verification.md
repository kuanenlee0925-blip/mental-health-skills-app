## GitHub publication — November 2, 2026

User requested publication. Rechecked 22 backend and 18 frontend tests and Vite
build: all passed; no live calls. Reviewed 74 changed files and checked the Git
index excludes backend/.env and runtime data. Configured-secret scan found no
matches in 81 candidate files. Implementation/evidence commit
[`41bab285ad9b3a085ccc8b8e357ac78e96e11d82`](https://github.com/kuanenlee0925-blip/mental-health-skills-app/commit/41bab285ad9b3a085ccc8b8e357ac78e96e11d82) was pushed to
`codex/part3-refinement`. The report's follow-up documentation commit adds immutable GitHub
links. Main remains Part One. Recordings and independent checkout verification
remain pending.

# Part Three verification — November 2, 2026

Current branch: `codex/part3-refinement`. All checks below were actually run
against fictional data. Twelve live text-model calls were subsequently made;
no real microphone/voice call has been made in this increment. Earlier Part Two evidence is retained below.

| Check | Observed result |
| --- | --- |
| `backend/.venv/Scripts/python.exe -m unittest discover -s backend -p 'test_*.py'` | 22 passed, including v1-to-v2 migration, retained reply ID, larger-text persistence and consented demo context. Starlette's httpx migration warning remains non-failing. |
| `npm.cmd --prefix frontend test` | 18 passed: six pacer and twelve mocked voice lifecycle checks. |
| `npm.cmd --prefix frontend run build` | Passed after the final larger-text CSS refinement. |
| `backend/.venv/Scripts/python.exe -m scripts.evaluate_part3` | 18 fictional scenarios and three cross-case checks passed; JSON and Markdown generated from actual test execution. |
| Clean source snapshot | Tests/build and fresh empty-database startup passed using installed dependencies. Updated preference behavior was rechecked after the last provider change. See part3-clean-checkout.md for the exact limit of this evidence. |
| Real browser full exercise | Completed in 60,013 ms active/wall, no pause, 1,015 ms setup. Session 378787a5-0ae7-4ada-8b23-b394e9e3ba95 displayed in Vue history and present in SQLite/API. |
| Direct Pause → support → Resume → Stop | Active 891 ms, excluded 69,355 ms, wall 70,246 ms, setup 5,640 ms. Session ce084aae-6b43-4f9a-8f3e-d2abcd90d16c saved stopped. No automatic resume. |
| Saved larger text | Selected in browser; remained checked after refresh. Available with ring or text choice. Standard/large sizes validated at API and migration preserved old history. |
| 390 × 640 exercise | Larger-text paused view showed Resume, Stop and Crisis support; support opened. Temporary viewport override reset. |
| Failed demo question and retry | One failed user message; no assistant invention or duplicate. Support opened after failure. Conversation 21ede5d9-4af0-4cd2-a021-cec4d8a1c5bc matched read-only SQLite and API message objects. |
| Actual API process restart | Same conversation history and Part Three session IDs/outcomes/times retained; larger text retained. Schema 2, no foreign-key violations. |
| Secrets/source hygiene | backend/.env is ignored. Presence flags only inspected. Source copy excluded credentials/runtime records. `git diff --check` passed; existing Windows line-ending notices are informational. |

Evidence: [scenario report](part3-evaluation.md),
[scenario JSON](evidence/part3-scenarios.json),
[records and process restart](evidence/part3-record-check.json),
[source snapshot hashes](evidence/part3-clean-source.json),
[larger text](evidence/part3-large-text.png),
[paused mobile view](evidence/part3-narrow-paused.png),
[completion](evidence/part3-completed.png),
[history ID](evidence/part3-history-id.png),
[failed request](evidence/part3-chat-failure.png),
[support after failure](evidence/part3-support-after-failure.png).

After checks, the original ring/standard-text/history-off preferences were restored. The app remains running in explicit demo mode with voice disabled. The optional
live-evaluation command uses an isolated temporary database and a persistent
12-attempt ledger. Its original dry presence check made zero calls. After setup, the explicitly
authorized live batch used twelve calls; all six answers were persisted, with
three passing, two failing and one partial content judgment. See
[the live review](part3-live-evaluation.md) and
[raw evidence](evidence/part3-live.json). Planner and visual-ring prompt wording
were clarified; all eighteen deterministic scenarios passed again. The user
declined additional calls, so those revisions have no live verification. A configured flag must not be reported as a
successful provider call.

Native recording attempt: Snipping Tool was available, but input reported
unavailable geometry and the screenshot did not consistently target Chrome.
No video was captured. The recording guide and HTML process page are supporting
materials, not recordings. Independent fresh dependency installation/peer
checkout, real screen-reader use, live voice, and revised live-prompt behavior remain
unverified. No clinical benefit is claimed.

---

# Part Two verification

Updated October 25, 2026. Runtime observations below were collected October 22
and 24. All inputs and records are fictional. Demo and mock evidence is distinct
from paid/live-model evidence. The Part One log follows as historical context.

## October 25 presentation increment

Added an optional Your saved choices disclosure on the home view, using existing
preference/session APIs. No backend/schema changes. In Chrome, selected Gentle
ring, refreshed and observed the selection retained; then used the latest
practice's display and observed Text cues selected and saved. Read-only SQLite
confirmed text/history-sharing-off and the displayed latest session
d4ce0c55-e0aa-4542-abef-69c4b649c6c5 (279 ms, interrupted, text).
[Profile screenshot](evidence/presentation-saved-choices.png).

In a new fictional conversation, asked “What was my last session?” with history
sharing off, then on. The first demo reply reported no available matching record;
the second described the saved interrupted practice with 0.3 seconds/text cues.
Database request flags were 0 then 1, references empty then the actual session
ID, and ordered messages equaled the API response. These are fixtures, not live
AI. [Comparison screenshot](evidence/presentation-chat-comparison.png) and
[record evidence](evidence/presentation-record-check.json). Restored sharing off.

Frontend checks on October 25: all 18 Node tests passed; production build passed.
The 21 backend checks remain the October 24 run; backend source did not change.
The new loading/empty/error presentation has been code-reviewed, not all manually
fault-injected. No timed student rehearsal has occurred. The
[presentation guide](presentation-guide.md) targets 4:40 and maps each criterion.
The direct instructor video opened successfully; selected opening frames were
inspected. Full playthrough and live-provider testing remain unperformed.

## Reproduce the automated checks

From the project root after the README setup:

```powershell
& backend/.venv/Scripts/python.exe -m unittest discover -s backend -p 'test_*.py' -v
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
```

Latest run, October 24: **21 backend tests passed, 18 frontend tests passed,
production build passed** (14 modules). Backend tests use temporary SQLite files;
voice tests inject fake microphone/peer/provider objects. No microphone permission
or paid call is requested. Starlette reports a TestClient/httpx deprecation warning;
there were no test failures. No clean-checkout test by another person is claimed.

Verified environment: Python 3.14.7, Node.js 24.20.0, npm 11.19.0; Vue 3.5.44,
Vite 7.3.7, plugin-vue 6.0.10; FastAPI 0.141.1, Uvicorn 0.52.4,
python-dotenv 1.2.3, httpx 0.28.1, websockets 17.3. Dependencies were installed
locally after the student's explicit approvals. npm audit reported zero
vulnerabilities at installation; this is not an ongoing security guarantee.

## Expected and observed behavior

| Scenario/check | Expected | Actual evidence |
| --- | --- | --- |
| Complete the selected exercise | Six full 4/6 cycles, completion after last exhale, no input required | Chrome October 22: completed, active/wall 60019 ms, setup 4147 ms, pause 0; [result](evidence/part2-completed.png) |
| Open support during a cue, close it, Stop | Frozen cue, explicit Resume, distinct stopped outcome | Active 3218 ms, paused 49709 ms, wall 52927 ms; [support](evidence/part2-support.png); focus returned to Resume |
| Backend stopped during use | Start/Stop and static support remain usable; no false saved claim | Stopped own API; support opened and exercise stopped at 3851 ms; [failed save](evidence/part2-save-failure.png) |
| Restart API then Retry save | One saved result, earlier records retained | Restarted actual Uvicorn process; same offline attempt saved once; old session/chat IDs retained after browser refresh |
| Optional demo questions | Ordered persisted messages and accurate mode label | Asked about Stop, then latest session with explicit history consent; assistant references matched a saved session |
| Retry a failed question | One failed user message, no invented assistant reply | Sent [demo:fail], clicked Retry; database count remained 1; failed request c3d995c7-816a-4ca0-9229-c28e9f27569e |
| SQL retrieval | Empty context distinguished from rows; unsafe SQL rejected before execution | Backend tests pass for no history consent, saved rows, other conversation/user scope, writes/comments/joins/UNION/functions rejected |
| Check history against SQLite | Same message IDs, content/order/status in API and UI | Read-only SQL message objects equal API objects; visible assistant ID 0be5519e-4ac4-47a3-a07a-b92947a07296 matches; [history](evidence/part2-history.png) |
| Scroll a long history | Crisis support stays visible | Sticky header verified in history screenshot |
| Narrow exercise | Stop and support remain reachable | Actual Vue iframe at 390 x 568 CSS pixels; [cue](evidence/part2-narrow.png); narrow completion measured 60016 ms |
| Keyboard support dismissal | Escape closes dialog, returns to Resume without starting | Observed focused Resume and Paused state in Chrome accessibility tree |
| Pause/Stop after periodic checkpoints | Active time never decreases; terminal result saved | Initial 1 ms rounding bug found, fixed and regression-tested; repeat saved 5040 ms active + 10066 ms paused; [fixed result](evidence/part2-pause-save-fixed.png) |
| Refresh while practicing | Interrupted saved outcome, no automatic resume | Chrome reload recorded 279 ms interrupted; [refresh result](evidence/part2-refresh-interrupted.png) |
| Missing voice configuration | No microphone/provider call; text remains available | Start voice showed unavailable/setup guidance; text question then succeeded in demo mode; [question view](evidence/part2-voice-unconfigured.png) |
| Voice lifecycle/races | Start once, wait for started event, distinguish Mute/End, release resources | 12 frontend voice tests cover denial, late grants/answers, blocked playback, navigation, support, page exit, hidden/unmount/duration and provider failure; mocks only |
| Backend voice boundary | Server owns policy/keys, bounded input, late-cancel cleanup, honest closure | 10 backend voice tests pass, including duplicate/cancel, duration/shutdown, sanitized errors, cross-origin rejection and no voice database records; mocks only |

[Home screenshot](evidence/part2-home.png) shows the running interface. Browser
checks used the Chrome extension through the computer-use tool. The narrow
preview was a temporary iframe harness, removed after checking; it is not a
physical mobile-device test. No external crisis-contact link was activated.

## Database inspection and timing

[Recorded read-only inspection](evidence/part2-record-check.json) contains actual
UUIDs, ordered message metadata and session values. Inspection used Python's
standard sqlite3 module with `Path('data/app.sqlite3').resolve().as_uri() +
'?mode=ro'`, `uri=True`, row_factory=sqlite3.Row, and parameterized queries:

```sql
SELECT * FROM messages WHERE conversation_id = ? ORDER BY sequence;
SELECT id, revision, started_at, ended_at, outcome,
       wall_ms, excluded_ms, active_ms, setup_ms
FROM sessions ORDER BY started_at;
SELECT COUNT(*) FROM messages WHERE content = '[demo:fail]' AND role = 'user';
PRAGMA foreign_key_check;
```

The five message objects for conversation
7b0ca97b-c340-4f99-893e-5553208e4dc1 exactly matched the `messages` array from
GET /api/conversations/{id}/messages. Expanded Vue record details displayed the
same assistant ID/request ID. Foreign-key inspection returned no violations.
There were seven session rows at final inspection: two completed, three stopped,
one interrupted and one unfinished failure record. History-sharing was restored
to false and display to text. Runtime database contents are ignored by Git;
only curated fictional metadata/screenshots are included as evidence.

The full-run timer uses performance.now from first-cue setup to final-step
completion, including scheduling delay, with entry time separately recorded.
Expected 60000 ms; observed 60019 ms. The UI displays 60.0 sec after rounding.
This is an application-instrumented measurement and not proof of clinical benefit
or independent physical timing accuracy. No typed response or Next action is
required. User-chosen support time is recorded separately, not counted in active
practice. Hidden tabs/long scheduling gaps interrupt rather than catch up.

## Failure, fix and limitations

The first narrow pause/Stop save was rejected: rounding wall and excluded time
separately can make their difference fall by 1 ms while paused. SQLite's monotonic
session guard rejected the decrease. The fix rounds active duration directly and
derives excluded duration, preserving the invariant. A fractional-timestamp test
now covers it; the repeated real-browser flow saved session
76f05e5c-425b-45f9-86c8-88f909e9dd78 successfully. The earlier unfinished record
ee4a34a0-f94b-4e64-88fe-df80a53f5b25 remains evidence, not fabricated completion.

Live text-model replies, real voice/audio hardware, provider session closure,
autoplay behavior with actual audio, and the public-demo comparison remain
unverified. Model configuration flags are not live-call evidence. Default mode
makes zero paid calls; no backend/.env was created. The required actual model
contribution must still be demonstrated before calling Part Two complete.

Reduced-motion handling and focus styles are implemented, but OS reduced-motion
and screen-reader behavior were not manually exercised. No full accessibility
audit, cross-browser matrix, clean-checkout reproduction, Figma interface capture,
student recording or Canvas submission is claimed. A forced process/network
failure can leave remote voice closure unconfirmed; the UI says so.

## Historical Part One checkpoint

The remainder describes October 15 only; its outstanding app checks have since
been partially addressed by the evidence above.

# Verification and curated evidence

October 15, 2026. This records design/document inspection, not a working app test.
Historical startup observations below describe the state at that checkpoint.

## Actual checks and observations

| Check | Expected | Observed |
| --- | --- | --- |
| Inspect new project | Preserve existing work | Existing .git directory found; no application source or commits; branch master |
| Compare starter documents with supplied text | Exact baseline contents | README.md and AGENTS.md matched the extracted supplied blocks |
| Inspect base structure | Six empty startup folders | frontend, backend, data, docs, prompts and handoffs existed; no supporting files at the startup checkpoint |
| Inspect travel source/history | Find relevant prior patterns without modifying them | Reviewed local source, README, AGENTS, handoff, research and submission notes; older commits and uncommitted renamed app are distinct |
| Check travel conversation persistence | Determine actual reuse boundary | HotelChat.vue and documented audit show no persistent conversation history; plan new storage here |
| Read Figma activity | Determine milestone impact | It explicitly adds no submission/grading requirement and requires initial design guidelines before interface building |
| Discover Figma integration | Determine current availability | Initially available, not installed; tools subsequently became available |
| Check Figma account | Confirm the actual connected account/plan | Account-information call succeeded: handle Brian, Starter plan, View seat; design-context, screenshot and live capture tools exposed; specific file access not yet checked |
| Check new planning files | Preserve startup structure and undecided design | Six required folders and five documents exist; all five README design placeholders remain unchanged; git diff --check returned no errors (new documents remain untracked) |
| Inspect submission/disclosure draft links | Refer to existing local documents and distinguish incomplete work | report.md and AI-USE.md were created; all relative Markdown targets in the report/planning files exist; publication and design decisions remain explicitly pending |
| Record student skill choice | Do not substitute an unselected lecture example | Student said “ok lets do first” after reviewing the skill list, selecting paced breathing; initial guidelines and proposal were then drafted |
| Generate experience diagram | Create the planned flow as an editable artifact | Figma generate_diagram succeeded; FigJam board 5Yv6ahXxwccAIgLu7nM0HV returned, with a full Mermaid copy and sketches saved in docs/flow.md; external instructor access is unverified |
| Create requested repository | Use the connected user's actual account | Verified account, checked name availability, then created public kuanenlee0925-blip/mental-health-skills-app with existing Git authentication; no credentials were printed or added to project files |
| Check completed design package | Consistent local artifacts and preserved class rules | All local Markdown link targets exist; code fences balance; AGENTS matches the supplied baseline; README design placeholders are filled; frontend/backend/data contain only .gitkeep |
| Check ignore rules | Exclude credentials, runtime SQLite, dependencies and builds | git check-ignore matched backend/.env, data/app.sqlite3, backend/.venv/example, frontend/node_modules/example and frontend/dist/example |
| Check timing arithmetic | State intended duration without claiming a measurement | Six cycles of 4 + 6 seconds calculate to 60 seconds; entry estimate and exclusions are documented separately; no runtime timing test performed |
| Inspect staged whitespace | Detect new formatting issues while preserving supplied text | The initial staged check flagged only a trailing blank line in the instructor-supplied AGENTS.md. Preserve that exact baseline; check all other staged files separately rather than silently changing class instructions |
| Publish design checkpoint | Remote main identifies the committed design | Created local codex/part1-design checkpoint 3b4cc735801de28db4f410b11fa756df3ba3080a, created initial main from it, pushed main, and compared git ls-remote with local HEAD: matched |
| Check public repository access | Instructor can reach repository without authentication | Unauthenticated HTTP GET of the repository returned 200; individual pinned document checks are recorded below after verification |
| Check pinned public documents | Submitted links point to actual checkpoint content | Unauthenticated raw GETs for README, AGENTS, AI-USE, design-pipeline, flow and verification all returned 200; each matched git show at 3b4cc735801de28db4f410b11fa756df3ba3080a after line-ending normalization |
| Check final report metadata | Usable when uploaded as a standalone file | Eight unique GitHub links; no relative-only document links, pending commit fields or draft-publication warnings remain; final report/publication notes are a separate bookkeeping update from the assessed design |

Travel test counts and live-call results appear in the earlier project's reports.
They were not rerun here and are not evidence of Assignment 3 behavior.

## Selected prompts, changes and decisions

| User/context | Resulting action or decision |
| --- | --- |
| "I juat need to submit part one today" | Prioritize the design milestone; identify later implementation/evaluation separately |
| User supplied R1–R4 / D1–D6 table | Use the supplied research rather than inventing findings or requiring an external dataset |
| "use this folder history to kind of help you build this" | Read Travel Application source and history; document patterns and gaps without modifying that project |
| Newly supplied startup activity | Revised the earlier plan: create only the exact starter and folders; leave the suggested breathing skill unselected |
| Newly supplied Figma activity | Inspect its requirements and integration availability; retain the student's skill choice as a prerequisite |
| “ok lets do first” | Select paced breathing; propose six 4/6 cycles, direct Start, optional chat and explicit Stop/support behavior |
| “can't you just make me a new one” | Create the new GitHub coursework repository and prepare the authorized publication |

Revised approach: the agent initially proposed paced breathing as a manageable
scope. The supplied startup instructions explicitly reserve the skill/design
decision for the student. The starter therefore preserves the undecided fields;
no breathing interface or design selection was silently implemented. After the
student selected paced breathing, the proposal and README were completed.

Design revision: use the hotel chatbot's two-call retrieval pattern only for
optional questions outside the exercise. A generated introduction was considered
as an entry feature, but making it a gate would add waiting/reading and could
delay the skill. Direct Start with optional explanation is the selected proposal
(D3/R4); less explanation is immediately visible. This is design reasoning, not
a tested user preference or a measured usability improvement.

Access limitation: the earlier Kaggle page-open attempt returned a title but no
usable dataset description or sample conversations. Do not claim dataset review.

## Not yet checked

- Exercise timing, Stop, interruption or support-panel behavior.
- Browser, keyboard, narrow-screen and reduced-motion behavior.
- SQLite persistence, duplicate prevention and API/history agreement.
- SQL retrieval validation, provider failures and stale responses.
- Live model behavior or live-interface capture/Design-frame implementation.
- Instructor's own Canvas/permission experience and access to the FigJam board;
  repository publication and unauthenticated repository-page access were checked.

The design proposal and sketches are now present. Define focused expected results
before implementation.
Use fictional fixtures and mocks for routine checks. Record live calls separately;
do not label plans as passes. The final milestone's fifteen scenarios and three
cross-case behavior checks are later requirements, not completed evidence here.
