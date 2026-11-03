# Part Three refinements and design review

November 2, 2026. Branch `codex/part3-refinement`. This supplements the
[Part Two API/behavior contract](part2-contract.md); the Part One proposal is
preserved in [design-pipeline.md](design-pipeline.md).

## Changes and rationale

| Choice | Part One intention / implementation learning | Part Three decision and tradeoff |
| --- | --- | --- |
| User control (R3/R4) | Support already paused the cue, but a normal rest required opening support. | Add Pause beside Stop. Resume is explicit and continues the remaining phase. One extra control is justified by direct control; no confirmation or required explanation. |
| Personalization (D5/D6) | Remember display/context choices, with little configuration. | Add Larger text inside optional Your saved choices. Save only an explicit choice; the start screen still needs no setup. Keep text/ring, history consent and reuse-last-display reversible. |
| Atomic steps (R1/D2/D3) | One instruction, six 4/6 cycles, no mandatory disclosure. | Keep one skill and the 60-second sequence. Do not add intake, emotion scoring or a skill library simply to increase feature count. |
| Honest history | Implementation exposed a fractional-rounding save failure. | Preserve the failed historical record and regression test. Record actual stopped/interrupted/completed outcomes, with active/pause/setup time separately. |
| Safety route (R2/D4) | Support must be visible even when chat fails. | Keep bundled support outside the model, independently reachable from home, exercise, history and failed chat. No new classifier or monitoring claim. |
| State adaptation (D1/R4) | The study does not define a reliable distress detector. | Adapt to explicit display/text-size/context preferences and the user's navigation. The exercise hides optional chat/history. Never infer feelings from stops or clicks. |

## Contract increment

`GET /api/preferences` and `PUT /api/preferences` now include `text_size`, one
of `standard` (default) and `large`. Existing cue/context fields are unchanged.
PUT sends the complete preference object; omitted fields use defaults. Invalid
values return the existing 422 `invalid_input` envelope. An unsuccessful save
leaves the acknowledged preference unchanged and reports failure.

Worked example: PUT `{"cue_mode":"ring","use_saved_context":false,"text_size":"large"}`
returns those fields plus `updated_at`. Refresh uses the persisted large text.
Reset preferences writes text cues, history sharing off, and standard size.

SQLite schema version 2 adds one checked `preferences.text_size` column with
standard as its default. Startup preserves all existing records. The migration
and repeat startup are tested against a version-1 fixture. No new dependencies.
Retrieved preference records include the field meaning `text_size=standard|large`;
those records are exposed to answer generation only with saved-history consent.

Pause uses `Pacer.pause`, snapshots/saves the current attempt, and focuses Resume.
No new timer is started. Resume excludes voluntary paused time; Stop stays
terminal. The API and model do not schedule exercise phases. Source owners:
`App.vue` (view/actions), `style.css` (reading sizes), `pacer.js` (clock),
`models.py` (validation), `database.py` (migration/write), `retrieval.py` (context).

## Evaluation and limits

[18 fictional scenarios and three behavior checks](part3-evaluation.md) were
executed with deterministic fixtures/simulated clocks. Browser evidence is in
[verification.md](verification.md). This is software evaluation, not user research
or evidence of clinical benefit. Real screen-reader use, long-term usability,
and live voice remain untested. A preference and a stopped session are not an
emotional assessment.

The live-text runner uses three fictional cases, twice each, with at most twelve
provider calls total. An on-disk counter reserves each attempt before sending;
rerunning refuses to reset that allowance. Live evidence must be reviewed for
accuracy, grounding and variation; HTTP success alone is insufficient. No live
result is claimed until the key/model are configured and calls actually finish.


## Live evaluation revision

The [12-call live selection](part3-live-evaluation.md) exposed missed activity
retrieval and an invented ring sound. Clarified the planner's practice/session
mapping and the answer prompt's visual-ring wording. The source evidence remains
unchanged; these prompt revisions are not verified live because the user retained
the exhausted twelve-call limit. Routine operation stays in demo mode.
