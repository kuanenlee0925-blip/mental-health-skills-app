# A Little Space — Mental Health Skills App

IST 402 · Assignment 3 · Part Three refinement, with the live-audio class
activity. Selected skill: **paced breathing (4–6)**, chosen October 15, 2026.

A local Vue + FastAPI + SQLite coursework prototype. Six cycles target 60
seconds. The app owns Start, Stop, support and the cue sequence independently
of AI and storage. Use fictional scenarios only; this is not therapy, a
clinical assessment, or a monitored support service.

## Part Three status — November 2, 2026

Direct Pause and saved Larger text are implemented. The additive database
migration preserves existing records. All 40 automated checks and the production
build passed; [18 fictional scenarios and three behavior checks](docs/part3-evaluation.md)
passed. See the [Part Three report draft](submissions/assignment3-part3/report.md),
[design review](docs/part3-design-review.md), [recording guide](docs/part3-recording-guide.md)
and [clean-checkout checklist](docs/part3-clean-checkout.md).

[Live text variation](docs/part3-live-evaluation.md) used all 12 authorized calls: three cases passed, two failed and one partially passed. Prompt revisions are not live-verified. Finished recordings, publication and an independent fresh-checkout test remain pending. Public main still contains
Part One, so a clone does not yet reproduce this local implementation.

## Existing implementation

- Working text/ring breathing cues, explicit Resume, stopped/interrupted outcomes,
  honest save status and retry, plus persistent session and text-chat history.
- Optional Your saved choices shows the local profile and latest saved practice;
  explicitly reuse its display or change it with the normal controls.
- Two-call SQL RAG: restricted scoped retrieval followed by a grounded answer.
  Default **demo responses** use labeled deterministic fixtures. Live text needs
  a separately configured OpenRouter API key and model.
- Live-audio implementation uses native WebRTC, GPT-Live and GPT-6 Luna delegation.
  Its checks use mocks. Real microphone/audio, model access and paid calls remain
  unverified until configured and explicitly tested by the student.
- The original [Part One report](report.md) is preserved. See the separate
  [Part Two report draft](submissions/assignment3-part2/report.md). Part Two is
  local and uncommitted; live model evidence and publication still need finishing.

## Run locally on Windows

Verified tools: Python 3.14.7, Node.js 24.20.0, npm 11.19.0. From the project
root, install the project-local dependencies if needed:

```powershell
python -m venv backend/.venv
& backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend ci
```

Run these in two terminals at the project root:

```powershell
# Terminal 1 — API; one worker, no reload during timing evidence.
& backend/.venv/Scripts/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --no-access-log
```

```powershell
# Terminal 2 — Vue
npm.cmd --prefix frontend run dev
```

Open [the local app](http://127.0.0.1:5174/). Vite proxies /api to FastAPI on
8002, preserving the travel app's ports. Ctrl+C stops each server. SQLite stays
at data/app.sqlite3; startup does not reset history. No .env is needed for demo mode.

## Configure providers separately

Copy backend/.env.example to backend/.env **only if no .env already exists**.
Enter keys locally, never in chat, Vue, Git or screenshots. Restart FastAPI after
changes. Health/config endpoints expose flags, not keys. A configured flag is
not evidence of a successful provider call.

For text: set MODEL_MODE=live, MODEL_API_KEY to an OpenRouter key, and MODEL_NAME
to an available model on that account. Two calls per question, 15-second network
timeouts, no automatic retry or model fallback. LIVE_CALL_LIMIT defaults to 50
per backend process, counting failures. Old demo replies keep their demo label.

For voice: set VOICE_ENABLED=true and OPENAI_API_KEY. Defaults are
VOICE_LIVE_MODEL=gpt-live-1, VOICE_BACKEND_MODEL=gpt-6-luna,
VOICE_MAX_SESSION_SECONDS=300 and VOICE_SESSION_LIMIT=3 attempted creations per
process. Keep the classroom live observation under 60 seconds. Start voice
explicitly; Mute does not end the paid session. End, support, navigation, hidden
tab, page exit and unmount release the mic. Server cleanup also handles late
responses and the duration limit.

Voice starts fresh and receives no saved text/session history. This app does
not save voice audio or transcripts. Provider store:false is a session-retrieval
setting, not a general retention guarantee. Provider closure can remain
unconfirmed after network/process failure. See [voice notes](docs/voice.md).

## Checks

```powershell
& backend/.venv/Scripts/python.exe -m unittest discover -s backend -p 'test_*.py' -v
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run build
& backend/.venv/Scripts/python.exe -m scripts.evaluate_part3
```

Backend tests use temporary SQLite files. Voice tests use fake media/peer/provider
objects and never request a real microphone. In demo text mode, [demo:fail]
simulates a provider failure; [demo:unsafe] proposes a rejected write query.
See [actual verification evidence](docs/verification.md).

## Design and source responsibilities

Direct Start avoids mandatory emotional disclosure (R4, D3); one cue and six
4/6 cycles keep the flow short (R1, D2). Stop and static support are independent
of AI (R2–R3, D4). Text is default, ring is optional and reduced motion overrides
it (D6). Saved choices are explicit; past-history sharing defaults off (D5).
Support pauses the remaining cue until explicit Resume. Hidden tabs or large
scheduling gaps interrupt, rather than complete, unseen steps. No ratings,
streaks, diagnosis or inferred emotional improvement.

| Location | Responsibility |
| --- | --- |
| frontend/src/App.vue, style.css | Views, input, navigation, saved-record presentation |
| frontend/src/pacer.js | Monotonic exercise timing/state |
| frontend/src/api.js | HTTP/JSON and error handling |
| frontend/src/VoicePanel.vue, voice.js | Native WebRTC/audio lifecycle and controls |
| backend/main.py, models.py | Thin routes and typed contracts |
| backend/chat.py | Text controller and two-call orchestration |
| backend/database.py | SQLite models, relations, transactions and writes |
| backend/retrieval.py | Restricted, scoped, read-only retrieval |
| backend/provider.py | Demo/live text adapter |
| backend/voice.py, voice_prompts.py | Voice boundary, prompts, cleanup |
| data/app.sqlite3 | Ignored local runtime data for fictional testing |

The browser never opens SQLite or receives provider keys. This is one fictional
local demo identity, with no authentication. Keep development servers on localhost.

## Documents

- [Original design and rationale](docs/design-pipeline.md)
- [Part One flow and sketches](docs/flow.md)
- [Part Two contracts and implementation differences](docs/part2-contract.md)
- [Voice activity and manual test](docs/voice.md)
- [Under-five-minute presentation guide](docs/presentation-guide.md)
- [Verification](docs/verification.md)
- [Current handoff](handoffs/current.md)
- [AI-use disclosure](AI-USE.md)

Optional live-interface/Figma capture and implementation have not been done.
The existing FigJam flow is a design artifact. Publishing does not submit to Canvas.

## Authorized Part Three live evaluation

After entering your OpenRouter key and model ID locally in backend/.env, run:

```powershell
& backend/.venv/Scripts/python.exe -m scripts.evaluate_live --run-authorized
```

This explicit command selects live text for its isolated fictional test database;
it does not require changing the ordinary demo server. Three cases run twice,
at most twelve provider calls, including failed attempts. It records results in
docs/evidence/part3-live.json and reserves attempts in the ignored
 data/part3-live-budget.json ledger. It refuses to reset an existing ledger.
Never remove that ledger to evade the authorized limit. Voice is not tested.
Do not run this paid command for routine peer checks. Review actual outputs;
API success does not prove answer quality. The twelve-call authorization applies
to this project session, not to arbitrary future repeated runs.

The November 2 allowance is now exhausted (12/12); the user declined additional
calls. The runner refuses to reset its existing ledger. See the live review for
observed failures; keep routine app use in demo mode. Do not rerun paid tests
without a new explicit allowance.
