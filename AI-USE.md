# AI-use disclosure — Part Three update

November 2, 2026. Codex (GPT-6 family; exact model identifier not available in
the tool environment) generated the Pause/larger-text changes, migration check,
scenario/live-evaluation runners, draft report and supporting documentation.
PowerShell, existing Python/Node dependencies, Git, and cua_repl browser tools
were used to verify the source and running app. The Computer Use skill informed
UI verification. No subagents or new dependencies were used in this increment.

Mock evaluation: 18 fictional cases, three cross-case checks; all 40 automated
tests and the Vite build passed. Browser/API/read-only SQLite evidence is
separate from simulated-clock tests. A source-only copy reused the installed
dependencies; no independent peer test is claimed. Native recording failed to
target Chrome reliably; a script and HTML evidence page were prepared instead.
No finished video or student narration is claimed.

Live OpenRouter text: all twelve authorized calls ran using openai/gpt-4.1-mini
at temperature zero, six fictional questions in a temporary database. API/DB
persistence matched, while agent content review found three pass, two fail and
one partial result. Missed session retrieval and an invented ring sound prompted
clarifications. The student declined four additional calls, so those revisions
remain unverified live. Original evidence is preserved. See
[the live review](docs/part3-live-evaluation.md). Official OpenRouter setup/model
pages were checked to help locate the key and public model ID. Credentials were
never printed or included in evidence. No further calls are authorized.

Selected changes/failures/decisions: [Part Three curated log](prompts/03-part3-refinement.md).
The student must review and understand the generated explanation. An AI draft
is not evidence that the student ran a test, watched a video or understood code.

---

# AI-use disclosure — Part Two update

Updated October 25, 2026. The October 15 disclosure below is retained as history.

Presentation preparation: the student supplied the Canvas rubric and asked to
prepare for it. Codex drafted docs/presentation-guide.md, mapped existing behavior
to four criteria, added a small optional saved-profile/latest-practice UI, and
verified preference refresh/reuse plus history-off/on fixture replies in Chrome
and read-only SQLite. Selected opening frames of the instructor's direct video
were reviewed; a full viewing is not claimed. No slide deck, student rehearsal,
live model call or presentation submission was performed.

| Tool/model | Available identifier | Actual role in Part Two |
| --- | --- | --- |
| Codex coding assistant | GPT-6 family; exact selected model/version not exposed | Generated Vue/FastAPI/SQLite implementation, deterministic fixtures, tests, documentation and draft report; reviewed/fixed timer and voice lifecycle failures |
| Shell, file and Git tools | PowerShell, Python 3.14.7, Node.js 24.20.0, npm 11.19.0 | Project-local authorized installs, source edits, test/build runs, read-only SQLite/API comparison, branch/diff inspection |
| Browser control | Chrome via cua_repl extension | Read complete live-audio activity; operated actual local app; verified timing, Stop/support, failures/retry, refresh/restart, narrow iframe and record IDs; captured screenshots |
| OpenAI documentation and web tools | Official Live, delegation, prompting, models and sideband references | Checked provider contract before implementing server-owned two-model voice flow; OpenRouter and framework references informed adapters/setup |
| Helpline lookup connector | Service version not exposed | Verified U.S. support resource destinations before bundling them; no crisis service was contacted |
| Sites / local preview skill | Skill package 1.1.2 at final review | Guided local project preview; no Sites cloud publication or public support deployment |
| Computer-use / OpenAI-docs skills | Installed local skills | Browser workflow and official API reference lookup |
| Application text adapter | OpenRouter model configurable; none selected or called live | Implemented two-call SQL planning/answer API path; all demonstrated replies are clearly labeled deterministic fixtures |
| Application voice adapter | gpt-live-1 and delegated gpt-6-luna in server configuration | Implemented according to official docs; mock tests only, no paid/live conversation |

The student requested Part Two and the live-audio activity, approved dependency
installs and asked the agent to continue. The agent implemented the previously
selected paced-breathing proposal, drafted explanations and ran fictional tests.
The student still needs to review the generated code/report and perform the
credentialed demonstrations; no review or understanding is assumed.

Curated prompts and failed/revised approaches are in
[prompts/02-part2-and-live-audio.md](prompts/02-part2-and-live-audio.md).
The pause-rounding regression, sticky support header and late voice cancellation
are documented in [verification](docs/verification.md). Screenshots and database
metadata contain fictional tests. No keys, real therapy conversations, travel
records or research-participant data were copied into this project.

Part Two remains local and uncommitted. Actual live-model contribution, real audio,
publication and Canvas submission are not claimed. Figma was used for the earlier
flow diagram only; no running-interface capture or design implementation occurred.

## Historical Part One disclosure

The statements below describe the earlier design checkpoint, before implementation.

# AI-use disclosure

Updated October 15, 2026. This disclosure covers the work actually performed for
Assignment 3 so far. Add later tools and uses as they occur.

| Tool / model | Identifier available in this session | Actual role |
| --- | --- | --- |
| OpenAI Codex desktop coding assistant | Exact selected model/version is not exposed in this session; record the visible selector label if available | Interpreted supplied assignments, inspected the local travel project/history, created starter/context files, drafted paced-breathing design/flow/research rationale/API plan/report and verification notes |
| Codex shell/file tools | PowerShell and Git; exact installed versions not checked for this documentation task | Read source, create/check Markdown and ignore rules, create the explicitly requested GitHub repository through existing Git authentication; publication is recorded separately in verification notes; no application dependencies or runtime tests |
| Web browsing tool | Tool identifier/version not exposed | Attempted to open the optional Kaggle dataset page and find its description; no usable sample conversations were reviewed |
| Plugin discovery | Exact service version not exposed | Located the Figma integration and offered its installation |
| Figma MCP / generate_diagram | Exact server version not exposed; local skill package figma 16.0.0 | Verified connected account; generated an editable FigJam experience flow from Mermaid. No live-interface capture, Figma Design-frame implementation or application screenshot |
| GitHub connector | Exact service version not exposed | Confirmed the connected account before repository creation |

## Human and AI contributions

The student supplied the assignment overview, study findings, class startup and
Figma activities, and permission to inspect the Travel Application folder.
The student selected paced breathing with “ok lets do first” on October 15 and
explicitly requested creation of a new GitHub repository using the connected
account. The agent drafted the fictional task, initial flow and detailed design
for review; no student review/approval of every drafted detail is claimed.

AGENTS.md reproduces instructor-provided text. README.md began as that baseline
and now includes AI-assisted project-specific guidelines for the chosen skill.
The design, sketches, evidence notes and report were generated with AI assistance
and require student review and understanding before submission.

No application model has been selected or called for Assignment 3. The travel
project's recorded provider/model and its past test results are historical
context, not this project's model choice or verification evidence.

## Evidence and limitations

See [the curated evidence log](docs/verification.md) for selected instructions,
source observations, the revised approach after receiving the startup activity,
and checks that have not been performed. Publication is reported only once
verified. No human review, working application, clinical effectiveness or Canvas
submission is claimed.

Evidence excludes credentials, local environment-file contents, account email,
internal account identifiers, real personal conversations, and research
participant data. Testing and demonstrations must use fictional scenarios only.
