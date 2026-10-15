# Assignment 3.1 — Part One

**Part One design proposal — publication metadata in progress.** October 15, 2026.

Repository: [mental-health-skills-app](https://github.com/kuanenlee0925-blip/mental-health-skills-app).

Submitted design commit: **pending the publication checkpoint.**

## Milestone scope

This milestone presents an implementable design for a localhost mental health
skills coursework prototype using Vue, FastAPI and SQLite. A working application
is not required for Part One. All evaluation will use fictional scenarios; this
prototype must not be offered as a real mental health support service.

## Design status

The student selected **paced breathing (4–6)**. Fictional Alex starts without a
questionnaire and follows six four-second inhales and six six-second exhales.
The intended guided duration is **60 seconds**, with entry/setup estimated
separately at 5–15 seconds and actual timing left for implementation checks.
Stop is immediate. Support is always visible; opening it pauses the cue and
closing it requires explicit Resume or Stop. Result/history are optional next
actions. No typing or emotional disclosure is required to complete the skill.

The [design notes](docs/design-pipeline.md) explain Vue/FastAPI/SQLite separation,
two-call read-only SQL RAG for optional questions, planned records/API contracts,
independent support and deterministic exercise controls, research tradeoffs,
personalization, crisis-text heuristic limits, and travel-project reuse.
The [flow and screen sketches](docs/flow.md) show the main experience.

The proposal prioritizes direct Start over mandatory model intake (D3/R4), a
single action per phase (D2), and persistent support/Stop (R2/R3/D4). Explicit
display/context settings are remembered and changeable (D5), without inferring
distress from clicks (D1). Neutral wording and a text alternative reduce stimulus
(D6). One skill and less initial explanation simplify entry but limit choice and
up-front detail. These are justified design decisions, not proven effectiveness.

## Project documents and evidence

- [README: purpose, selected scope and initial guidelines](README.md)
- [AGENTS: class development and verification rules](AGENTS.md)
- [Design, architecture, planned data and travel-project reuse](docs/design-pipeline.md)
- [Main flow and low-detail screen sketches](docs/flow.md)
- [Verification and curated evidence](docs/verification.md)
- [AI-use disclosure](AI-USE.md)

These relative links are intended to resolve within the published repository.
Before uploading this file alone to Canvas, replace them with accessible links
to the submitted repository version and confirm instructor access.

## What is complete and what the evidence establishes

- The six starter folders and supplied root documents have been created.
- Starter text matched the supplied source at setup; README now includes the
  chosen skill and initial guidelines. AGENTS retains the supplied baseline.
- The earlier travel project's local code, reports and Git history were inspected.
  Reuse is planned; no application code or travel data was copied.
- The existing hotel chatbot's lack of persistent conversations was identified;
  new conversation/session storage is required for this project.
- Figma account access was confirmed and an editable FigJam flow was generated.
  The repository includes the flow so the design is accessible without relying
  on FigJam permissions. No live-interface capture or Design-frame revision was
  performed. The optional Figma activity adds no submission requirement.

No browser exercise behavior, database persistence, timing, live model behavior,
Figma design revision, repository publication or Canvas submission has been
verified. The evidence log distinguishes these gaps from completed inspection.

## Remaining before Part One submission

1. Complete publication metadata and accessible submitted-version links.
2. Student reviews the AI-assisted proposal/disclosure and uploads report.md to
   Assignment 3.1 in Canvas. Publication is not submission.

Open implementation questions: provider/model choice, verified regional resource
copy, heuristic false positives/misses, cue accessibility, timer interruptions
and usefulness of restricted history queries. Actual timing, persistence,
failure behavior and model variation remain later verification work. No live
application demonstration or final fifteen-scenario evaluation is claimed here.
