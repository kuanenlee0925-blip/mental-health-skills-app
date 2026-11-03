# Part Two and live-audio implementation prompts

Curated on October 25, 2026; summaries of the instructions used, not a full chat
export. All scenarios and saved examples are fictional.

## 02 — Build the selected skill

User: "can you start building part 2" and subsequent "keep going".

Implement the chosen paced-breathing flow in Vue/FastAPI/SQLite. Preserve six
4-second inhales and 6-second exhales, direct Start/Stop, independent support,
text-first presentation and explicit history consent. Save actual results and
messages; use strict read-only SQL RAG and stable IDs. Verify one complete
browser/API/database round trip before expanding. Preserve Part One's report.

## 03 — Add the live-audio activity

User: "also do this alone side with part 2" with the Canvas activity.
The user separately approved project-local dependencies and websockets cleanup.

Add native WebRTC to the optional question view. Keep two model roles, prompts,
credentials and session policy in FastAPI. Distinguish Mute from End. Release
tracks on End, failure, navigation and interruptions; cancel late starts. Never
save voice audio or transcripts. Use mocks first and leave the paid microphone
observation to an explicitly started, short student test.

Runtime prompt locations: backend/retrieval.py (query schema/grammar),
backend/chat.py (answer rules and application notice), backend/database.py
(reviewed skill), backend/voice_prompts.py (Live delivery and delegated knowledge).
The text adapter is backend/provider.py; voice model names are server settings in
backend/voice.py and the key-free backend/.env.example.

## Revisions supported by evidence

- A static header disappeared when scrolling history. Made it sticky so the
  support control remains visible; verified in the running browser.
- Demo history initially displayed raw database fields. Changed future fixture
  replies to plain-language seconds/display descriptions. Existing saved replies
  retain their actual original content.
- A pause/Stop browser check rejected a save because rounding wall and excluded
  time separately reduced active time by 1 ms. Round active time itself and
  derive excluded time; the regression test and repeated browser flow pass.
- Canceling a pending voice start can still leave a provider session created by
  a late response. Use request-ID cancellation tombstones and backend sideband
  closure; mock tests cover the race. Real provider closure remains unverified.

Use docs/verification.md for observed results and limitations; do not convert a
mock pass or configuration flag into a claim of working live AI.

## 04 — Prepare the in-class presentation

User: “I'd also need to do this” with the complete four-part presentation rubric.
Prepare an under-five-minute live-demo script, preserve honest mock/live labels,
and make profile/history personalization concrete. Add an optional saved-choices
view with an explicit reuse-display action, using existing records rather than
collecting emotional disclosures. Verify refresh, override and history-sharing
examples. Keep the instructor reference's editable-preference idea; leave its
screening flow outside this app's single-practice scope. Record the selected
frames actually inspected and leave the student's full viewing/rehearsal pending.
