# In-class presentation — 4 minute 40 second demo guide

Prepared October 25, 2026 for the [Canvas presentation assignment](https://psu.instructure.com/courses/2484533/assignments/18799655).
The supplied Canvas page shows Tuesday, October 27 at 3:59 p.m.; the instructions
also list October 29 for students assigned that date. Follow your assigned Canvas
date. Present the running app in under five minutes. No additional upload is required.

This is a rehearsal script, not a record of a timed student rehearsal. Practice it
once with a stopwatch and aim for 4:40 so you have a margin for clicks.

## Before class

1. Start FastAPI and Vue using the two commands in [README](../README.md). Open
   http://127.0.0.1:5174/ and keep both terminals running.
2. Use fictional Alex: a student between study tasks who wants a brief practice
   without describing feelings. Alex is the scenario, not a diagnosis or an
   actual named account. The app stores one local profile of explicit choices.
3. Confirm at least one fictional session exists in Your history. Do not delete
   prior evidence. Set Text cues and leave Use saved history off initially.
4. Open Ask a question and choose New text conversation for the demonstration.
   This does not delete earlier conversations. Return to the home screen.
5. Keep this guide beside you and the app on the presentation screen. Have
   [timing evidence](evidence/part2-completed.png) and
   [verification](verification.md) ready as backups.
6. Check the actual mode label. Currently it is **Demo responses · no live AI**.
   The script below openly demonstrates fixtures. Do not call them live AI.
   Actual model contribution for Part Two still needs credentials and a separately
   recorded live check. Voice is implemented but unverified live; omit the voice
   call from this short presentation unless it has been verified beforehand.

## What to click and say

### 0:00–0:20 — Introduce the person and scope

**Show:** home screen.

**Say:** “This is A Little Space, a coursework prototype for a short breathing
practice. My fictional user is Alex, a student between study tasks who wants a
brief exercise without explaining their feelings. It is not therapy, diagnosis,
or a monitored support service.”

### 0:20–1:00 — User state, adaptation and override (25 points)

**Do:** select Gentle ring, wait for the saved message, refresh, and show that the
selection remains. Expand Your saved choices. Use last practice’s display or
select Text cues to show that the choice is reversible.

**Say:** “The information I use is Alex’s explicit display preference, not a guess
about distress. The ring option changes the pacing display; text provides a
quieter alternative. This choice survives refresh because it is saved in SQLite.
Alex can change it, or explicitly reuse the display from the latest practice.
The browser’s reduced-motion preference takes priority. I don’t infer a diagnosis
or emotional state from stopping or clicking.”

**If asked:** the app contracts during the exercise by hiding optional chat/history.
That is a change based on the chosen activity, not automatic distress detection.

### 1:00–2:25 — Skill walkthrough and research (25 points)

**Do:** Start breathing and let all six cycles finish. Keep the app visible;
switching away can interrupt it. Talk while its 60-second sequence runs. Then
start a second short attempt, open Crisis support, close it, show Paused/Resume,
and choose Stop. Wait for the save confirmation.

**Say during the first run:** “Each cycle is four seconds in and six seconds out.
Six cycles target 60 seconds. R1 favors a short exercise, and D2 supports one
action at a time. D3 led me to avoid required typing or emotional ratings.
The app—not the model—controls these steps. One measured run took 60.019 seconds,
with 4.147 seconds of setup recorded separately.”

**Say during support/Stop:** “R2 and D4 led to this persistent support route. It
works even when the backend or model fails. Support pauses the cue. Closing it
does not restart the exercise; Alex chooses Resume or Stop. Stop has no
confirmation barrier, which supports R3 and user control.”

Do not activate an external crisis-contact link during the demonstration.

### 2:25–3:05 — Profile, history and accessibility (25 points)

**Do:** Back to breathing → Your saved choices. Show the new stopped practice,
its display and duration. Click Use last practice’s display. Then Your history
→ expand that session’s Record details.

**Say:** “My minimal profile stores the chosen display and whether saved history
may be used in text answers. Each practice stores its actual display, timing and
outcome. This latest-practice option personalizes the interface from a real
record, but only after Alex chooses it. A stopped practice stays stopped; it does
not mean the person improved or felt worse. Text controls, keyboard focus and
an optional ring reduce interaction effort.”

**If asked:** choices update through FastAPI to SQLite. History can be reviewed;
preferences can be reset. Multiple named profiles are outside this version.
The small profile avoids extra setup while supporting an explicit correction.

### 3:05–4:20 — Chatbot tone, personalization and limits (25 points)

**Do:** open Ask a question. With Use saved history off, ask:

> What was my last session?

Show the answer that it has no matching available history. Turn sharing on, wait
for the saved message, then ask the same question again. Show the recorded
outcome/duration/display in the reply. If time permits, ask “What display did I
save?” to show profile-based context. The optional third question is not needed
to finish within the time limit.

**Say:** “These responses are labeled demo fixtures. They exercise the same
retrieval and persistence path, but I have not verified a real model call yet.
With sharing off, past practice is unavailable to the answer. With permission,
the answer can use the actual saved session. The wording is factual and neutral:
no judgment, invented feelings or claim that completing an exercise helped.
The live prompt restricts answers to reviewed skill content and retrieved records.
The model explains; it cannot change the steps, exits, support or database.”

If configured and genuinely tested before class, replace the first two sentences
with an accurate statement naming the actual model and identifying live versus
saved/mock replies. Do not remove the qualification just because a key exists.

### 4:20–4:40 — Close with evidence and one limitation

**Say:** “The automated checks cover storage, retrieval, exercise timing and
voice cleanup. Browser testing caught a one-millisecond pause-rounding error;
I fixed it and verified that the result saves. Real model and voice behavior,
and screen-reader testing, remain unfinished. This evaluates software behavior,
not clinical effectiveness.”

Stop here. Avoid a long source-code tour unless the instructor asks.

## Rubric map and honest readiness

| Criterion | Concrete demonstration | Remaining limitation |
| --- | --- | --- |
| User state/interface adaptation | Explicit Text/Ring choice, persistence, override, exercise-only screen | No mood check-in or distress detector; explain this deliberate assumption |
| Skill/research | Complete six cycles, show support pause and Stop; explain R1–R4/D2–D4 | Prior timing is app-instrumented, not a clinical result |
| Profile/history/accessibility | Saved choices, latest record, explicit reuse, history details | One local profile only; reduced-motion code exists, manual OS/screen-reader check not done |
| Chat tone/limits | Compare history off/on, show actual saved fields, explain prompt limits | Current responses are deterministic mocks; live-model behavior unverified |

The rubric requires working behavior and clear explanations. This guide does not
guarantee full credit, particularly where live-model evidence remains unfinished.
The presentation allows clearly identified mocked/planned features; the separate
Part Two implementation still calls for demonstrating the model's contribution.

## Instructor reference: keep, revise, smallest test

The [direct reference video link](https://pennstateoffice365-my.sharepoint.com/:v:/g/personal/skb5969_psu_edu/IQCEm-SB-LU0RICabs8yR9h0AQ5wzb7T2dAWDsG3CVWlzq0?e=tgHfRY)
opened successfully in Chrome even though the Canvas embed refused to connect.
The player reports a 2:03 video with no sound. Selected opening frames were
inspected, including saved profiles/preferences around 0:09 and the optional
screening flow around 0:23–0:33. A complete playthrough is not claimed.

- **Keep:** reviewable saved preferences and a way to choose/update a profile.
  Our smaller equivalent is Your saved choices with an explicit display override.
- **Revise for this project's scope:** use a display preference instead of adding
  the reference's optional screening flow. This keeps the practice entry short
  and avoids collecting information this app does not need. It is a scope and
  interaction decision, not a clinical assessment of that reference.
- **Smallest test:** choose ring, refresh, confirm it remains selected, then reuse
  the last practice's text display. Confirm SQLite agrees and Start still works
  without a check-in or chat. This round trip was checked on October 25.

Watch the complete short video yourself before presenting if the instructor
expects discussion beyond those inspected interactions.

## If something fails during the live demo

- If the model/provider is unavailable, identify the failure and demonstrate
  breathing/support plus a previously saved reply with its true mode label.
- If saving fails, show the honest error and Retry save; do not claim persistence.
- If a refresh interrupts practice, explain the interrupted outcome and explicitly
  start again. Do not describe it as completed.
- If running short, omit the optional third chatbot question and voice discussion.
  Preserve the four rubric explanations and the visible Stop/support behavior.
