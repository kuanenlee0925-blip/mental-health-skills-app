# Part Three clean-checkout review

## Agent verification performed November 2

A source-only copy of the current backend/frontend/scripts was created in an
ignored project-local working directory. It excluded backend/.env, .venv,
node_modules, build output, caches and runtime SQLite. The file hashes are in
[evidence/part3-clean-source.json](evidence/part3-clean-source.json).

From that copy: 22 backend tests, 18 frontend tests, and the Vite build passed.
A fresh default database was created under the copy's own data directory.
Health reported demo mode, configured=true, zero live calls; both conversations
and sessions were empty. This checks that source and database paths do not
accidentally depend on the original runtime records or working directory.

**Limit:** the Python environment and frontend dependency directory were reused
from the authorized local installation. This was not a fresh dependency install,
a Git checkout of a published Part Three commit, or an independent peer test.
The current source is still uncommitted; cloning public main will get Part One.

## Peer check to complete after publication

1. Clone the repository URL in README into a new folder and check out the exact
   submitted commit. Record that hash, OS, Python and Node versions.
2. Follow README's environment creation, pip requirements and npm ci instructions.
   Do not copy backend/.env or the existing SQLite database. Demo mode needs no key.
3. Start both servers with the README commands, open port 5174 and confirm the
   initial history is empty. Use only fictional test inputs.
4. Complete one exercise, change text size/display, send a demo question, and
   refresh. Restart both servers and confirm the same saved IDs and preferences.
5. Try `[demo:fail]` and verify support remains reachable. Run the test/build
   commands. Record actual output and any setup problem; do not mark planned
   checks as passed.

Peer name/date/environment/commit/result: **pending**.
