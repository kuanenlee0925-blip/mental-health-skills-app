# Part Three recording guide

Two recordings are required, or one with marked sections. **No completed video
has been captured yet.** The installed Snipping Tool was inspected, but native
input could not reliably target the Chrome window. The written process page is
not a substitute for a recording.

Use only the fictional Alex scenario. Record the app window, without private
tabs, credentials, or personal data. Read/rewrite this script so you can explain
it yourself. No microphone or paid voice session is required inside the app.
The current demo server is explicitly pinned to mock mode.

## A. Application demonstration (about 3 minutes)

1. Home: “This is A Little Space, a coursework prototype. Alex is a fictional
   student taking a short break. It is not therapy or a monitored service.”
2. Open Your saved choices, toggle Larger text, and refresh. “The app remembers
   choices I make. It does not guess my feelings. I can change or reset them.”
3. Start: “The app shows one breathing cue at a time: four seconds in, six out,
   repeated six times. The planned active duration is sixty seconds.”
4. Pause, open and close support, then Resume: “Pausing is optional. Nothing
   continues until I choose Resume. Stop and support stay available.”
5. Let one attempt complete. Show saved duration and View history. “This is the
   recorded time. Pauses and setup are separate. Stopped and interrupted attempts
   have different labels, and activity is not a measure of improvement.”
6. Ask a question with history sharing off, then on: “Text answers can use the
   records I explicitly share. These responses are labeled demo fixtures.”
   The separate live evidence has now been reviewed: 12 calls found missed history
   and one incorrect ring-sound description. Explain these limitations; the
   current app demo remains mocked.

## B. Process screencast (about 2 minutes)

1. In Ask a question send `[demo:fail]`. Show the error and press Retry once.
   “This is an intentional mock provider failure. One question remains saved
   as failed; the app does not make up an answer or duplicate my message.”
2. Open Crisis support. “A failed model does not remove this route. The app
   does not wait for a classifier to decide whether support is allowed.”
3. Open [the process evidence page](evidence/part3-process.html) in a browser.
   Show failure → evidence → decision. “Testing also found a surprising one-
   millisecond rounding bug. Separate rounding made active time decrease while
   paused, so the database rejected a checkpoint. We preserved that old record
   and added a regression test.”
4. Show the `snapshot` excerpt. “The clock uses the paused or finished instant
   to freeze active time. We round active time directly and derive excluded time
   from wall minus active. That keeps the saved timing consistent. This code
   controls the exercise; the language model cannot change it.”
5. Show the scenario report. “Eighteen fictional scenarios and three cross-case
   checks passed. They cover normal use, interruptions, retry, consent, unsafe
   SQL, missing configuration and failures. This is not clinical testing.”

## Before adding the links to report.md

Play both files to confirm readable text and understandable narration. Upload
them to your permitted course file service and check access with the intended
reviewer permissions. Replace the report's pending recording lines with actual
links. Do not submit an inaccessible local path, the instructor's demo, or the
written process page as your recorded demonstration.


Live process option: show part3-live-evaluation.md beside the raw JSON. Explain:
“The API saved all replies, but that did not prove their quality. Two answers
missed the practice record and one described a sound that does not exist. I
clarified the prompts, reran mocks and preserved the failures. I kept the
12-call limit, so I have not verified the revised prompts live.”
