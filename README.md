# Mental Health Skills App

IST 402 — Assignment 3, Part One design

Selected skill: **paced breathing (4–6)**. The student selected this option on
October 15, 2026. This repository contains design documents, not a running app.

- [Part One report](report.md)
- [Experience flow and screen sketches](docs/flow.md)
- [Design rationale, architecture and data/API plan](docs/design-pipeline.md)
- [Verification and curated evidence](docs/verification.md)
- [AI-use disclosure](AI-USE.md)

## Purpose

Build a local application that lets someone practice a short skill, stop at any
point, and return to useful session history. The interface should ask for little
reading or typing and keep the person in control. A conversational model can
help introduce the skill and explain the app, using reviewed content and saved
context.

This is a coursework prototype, tested only with fictional scenarios. It must
not diagnose, provide therapy, imply human monitoring, or be offered as a real
mental health support service.

## Current milestone

The starter folders and instructor-provided AGENTS.md are in place. Part One
adds the initial design, research rationale and implementation plan. Application
capabilities below are plans. No packages, credentials, server, database or
runnable interface have been added.

## Initial design guidelines

The student chose paced breathing. This initial direction was drafted with AI
assistance for student review; implementation has not begun. Detailed
alternatives, tradeoffs and open questions are in docs/design-pipeline.md.

Class principles to carry into your design:

- Keep the guided skill within 90 seconds at its intended pace. Show one clear
  action at a time and keep reading, typing, and configuration demands low.
- Let people start, stop, skip, and change their choices. Keep support information
  visible and usable independently of model responses.
- Use calm, readable language, sufficient contrast, visible keyboard focus,
  a narrow-screen layout, and an alternative to motion.
- Make personalization understandable and changeable. Keep self-report,
  observed behavior, and interpretation distinct; clicks do not establish an
  emotional state or diagnosis.
- Explain how a design choice follows from a class finding, what alternative
  you considered, and what tradeoff you accepted. Check the running result later.

- **Skill and fictional task:** Alex, a fictional student, wants a short exercise
  between study tasks without describing feelings. Six cycles of a four-second
  inhale and six-second exhale target 60 seconds (R1, D3).
- **Flow and control:** Entry → explicit Start → one breathing cue at a time →
  completed/stopped result → optional history. Stop is always available. Support
  opens from every view; during exercise it pauses the cue, and closing support
  requires an explicit Resume or Stop (R2–R4, D2, D4).
- **Interface:** Start is primary; explanations/chat are optional. Use neutral
  wording, readable contrast, visible focus and a narrow-screen layout. Text
  countdown is default; an expanding ring is optional. No mood questionnaire or
  automatic distress detection (D1–D3, D6).
- **Model and personalization:** Optional questions outside exercise use two-call
  SQL RAG over reviewed content and scoped saved context. The model cannot run
  the exercise or invent advice. Remember explicit display/context choices,
  with change/reset controls. History shows actual messages and sessions rather
  than clinical scores (R4, D5).
- **Alternatives and tradeoffs:** Prefer direct Start over mandatory chatbot
  intake: less reading/disclosure but less initial explanation. One skill is
  simpler but offers less choice. Remembered settings reduce setup but can
  become stale, so show them and allow changes.

These are design plans. Timing, browser behavior, persistence and model output
need implementation and verification in later milestones.

## Technology and separation

- Frontend: Vue with JavaScript, HTML, and CSS. It presents the interface,
  responds to input, and sends HTTP requests to the backend. Node.js provides
  the frontend development tools.
- Backend: Python with FastAPI. It exposes the API, validates requests, applies
  business rules, calls the conversational model, and reads/writes the database.
- Database: SQLite. The planned database is data/app.sqlite3. Only the Python
  backend accesses it; the frontend receives data through the API.

The application runs on localhost.

## Secrets and APIs

Store model-provider API keys and other secrets in `backend/.env`. Keep this
file out of Git with `.gitignore` before adding credentials. Provide a
`backend/.env.example` containing variable names and empty or dummy values so
another developer knows what to configure. The backend must explicitly load its
configuration; placing a file in the folder does not load it automatically.
Never put private keys in Vue code, browser-exposed environment variables,
API responses, logs, screenshots, prompts, or Figma.

Vue calls our FastAPI endpoints using HTTP and JSON. FastAPI validates requests,
calls the external model API, and reads or writes SQLite. Document each endpoint's
input, response, and failure behavior in `docs/design-pipeline.md`. Use finite
timeouts, clear loading and failure states, and a bounded number of provider
calls. A configured key, a mocked response, and a successful live API call are
different checks. Ordinary history browsing should not require a model call.

## Conversations, RAG, and data views

Save submitted user messages and actual model replies in SQLite, linked by a
conversation ID. Keep a message ID, role, content, timestamp, and request status
so the app can reconstruct the conversation in order. Store exercise outcomes
and preferences in related records. A failed model request must not create a
fabricated reply, and a failed database write must not appear as a successful
save. Saved records should survive refresh and backend restart without duplicates.

**Retrieval-augmented generation (RAG)** supplies relevant stored information to
the model before it answers. Use the SQL-based pattern covered in class:

1. FastAPI sends the question and relevant database schema to the model API.
2. The model proposes a retrieval query. FastAPI checks it, restricts it to
   allowed data for the current conversation or demo user, and executes it using
   read-only SQLite access with limits on the results.
3. FastAPI sends the selected records and reviewed skill information in a second
   model call. The answer should identify its supporting records and acknowledge
   missing information instead of inventing history.
4. Backend application code saves the actual reply and returns the result to Vue.

The model never connects directly to SQLite. RAG retrieval cannot insert,
update, or delete records; normal conversation saves use separate, parameterized
backend operations. The query-planning and answer-generation calls both count
toward the API budget. SQLite is sufficient for this baseline; it does not
require a vector database.

Make the saved data visible. Provide a Vue conversation-history view and a
session table or timeline, both populated through FastAPI from SQLite. Show
message order and time, plus exercise duration and stopped/completed status.
Any summary or chart must come from those records and must not imply a diagnosis
or improvement in mental health. During development, also inspect the schema,
relationships, and rows with an available SQLite viewer or read-only queries.
Compare the database, API response, and displayed history for the same fictional
conversation, including after a refresh and backend restart.

## Project folders

```text
project-root/
|-- README.md                 Project purpose and starting direction
|-- AGENTS.md                  Instructions for the coding agent
|-- .gitignore                 Local files to exclude from Git
|-- frontend/                  Vue interface and frontend dependencies
|-- backend/                   Python/FastAPI API and application logic
|   |-- .env                   Local secrets; ignored by Git
|   `-- .env.example           Configuration names with safe placeholders
|-- data/                      Local SQLite database and fictional fixtures
|-- docs/
|   |-- design-pipeline.md     Architecture, behavior, and design decisions
|   `-- verification.md        Checks to run and evidence of what happened
|-- prompts/
|   `-- 01-start.md            First scoped instruction for the agent
`-- handoffs/
    `-- current.md            Current state and next step for a new session
```

This map includes future implementation files. Current design documents are
linked above. Startup created only the folders and two root documents; Part One
adds supporting notes, report and disclosure. Ignore rules are now in place;
verify them again before adding credentials or runtime data. Environment files
and SQLite will be created during implementation. Keep fictional fixtures
separate from runtime records and do not commit the working database.

## Later design workflow

The separate Figma and MCP activity covers building a small interface, bringing
it into editable Figma frames, and using a selected design to guide a Vue
revision. That work comes after this startup step and your initial design
guidelines. Figma edits do not automatically update application code.

## Getting started

Read `AGENTS.md`, then `docs/design-pipeline.md` and `handoffs/current.md`.
Review the initial design before requesting implementation. Part One's report
links to design and evidence; publication does not submit it to Canvas.

Add supporting project notes as work requires them. Installation, interface
building, FastAPI/model connections, SQLite, RAG, and data views are later tasks.
Record actual setup, configuration, run, stop, and test commands here only after
they have been implemented and checked.
