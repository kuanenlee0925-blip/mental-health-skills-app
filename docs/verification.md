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
