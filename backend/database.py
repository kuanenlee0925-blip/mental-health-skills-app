"""Application-owned SQLite writes. Runtime data is never seeded with conversations."""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
from uuid import uuid4

from .errors import AppError

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "app.sqlite3"
DEMO_USER = "fictional-local-user"
SKILL_CONTENT = (
    "Coursework prototype for fictional testing, not therapy or monitoring. "
    "Paced breathing v1: six cycles, inhale for four seconds and exhale for six, "
    "60 seconds planned total. Text cues are default; an optional ring can be chosen. "
    "Start is optional. Stop ends the exercise immediately without penalty. "
    "Support pauses the cue; closing support requires explicit Resume or Stop. "
    "The app does not assess feelings, diagnose, recommend treatment, or infer improvement. "
    "History shows recorded activity only. If the exercise is uncomfortable, you can stop."
)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class Database:
    def __init__(self, path=DB_PATH):
        self.path = Path(path).resolve()

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path, timeout=3)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        try:
            with con:
                yield con
        finally:
            con.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            version = con.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1, 2):
                raise RuntimeError("Unsupported database schema version; preserve the file.")
            con.executescript("""
                CREATE TABLE IF NOT EXISTS demo_users (id TEXT PRIMARY KEY);
                CREATE TABLE IF NOT EXISTS preferences (
                    user_id TEXT PRIMARY KEY REFERENCES demo_users(id),
                    cue_mode TEXT NOT NULL, use_saved_context INTEGER NOT NULL,
                    updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES demo_users(id),
                    created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    content TEXT NOT NULL, status TEXT NOT NULL, error_code TEXT,
                    refs_json TEXT NOT NULL DEFAULT '[]', used_saved_context INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    request_id TEXT NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
                    sequence INTEGER NOT NULL, role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                    content TEXT NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL, mode TEXT NOT NULL,
                    UNIQUE(conversation_id, sequence), UNIQUE(request_id, role));
                CREATE TABLE IF NOT EXISTS attempts (
                    id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
                    created_at TEXT NOT NULL, status TEXT NOT NULL, mode TEXT NOT NULL,
                    calls INTEGER NOT NULL DEFAULT 0, error_code TEXT, refs_json TEXT NOT NULL DEFAULT '[]');
                CREATE TABLE IF NOT EXISTS app_events (
                    id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    request_id TEXT NOT NULL UNIQUE REFERENCES requests(id) ON DELETE CASCADE,
                    content TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES demo_users(id),
                    revision INTEGER NOT NULL, skill TEXT NOT NULL, skill_version TEXT NOT NULL,
                    cue_mode TEXT NOT NULL, started_at TEXT NOT NULL, ended_at TEXT,
                    outcome TEXT NOT NULL, wall_ms INTEGER NOT NULL, excluded_ms INTEGER NOT NULL,
                    active_ms INTEGER NOT NULL, setup_ms INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS skill_content (id TEXT PRIMARY KEY, version TEXT NOT NULL, content TEXT NOT NULL);
            """)
            # Additive migration preserves existing history and display choices.
            columns = {r[1] for r in con.execute("PRAGMA table_info(preferences)")}
            if "text_size" not in columns:
                con.execute("ALTER TABLE preferences ADD COLUMN text_size TEXT NOT NULL DEFAULT 'standard' CHECK(text_size IN ('standard','large'))")
            con.execute("PRAGMA user_version=2")
            con.execute("INSERT OR IGNORE INTO demo_users VALUES (?)", (DEMO_USER,))
            con.execute("INSERT OR IGNORE INTO preferences (user_id,cue_mode,use_saved_context,updated_at) VALUES (?, 'text', 0, ?)", (DEMO_USER, now()))
            con.execute("INSERT OR IGNORE INTO skill_content VALUES ('paced-breathing','1',?)", (SKILL_CONTENT,))
            # A process restart cannot truthfully finish an abandoned provider call.
            con.execute("UPDATE messages SET status='failed' WHERE request_id IN (SELECT id FROM requests WHERE status='pending')")
            con.execute("UPDATE requests SET status='failed', error_code='server_restarted' WHERE status='pending'")
            con.execute("UPDATE attempts SET status='failed', error_code='server_restarted' WHERE status='pending'")

    def conversation(self, ident):
        with self.connect() as con:
            con.execute("INSERT OR IGNORE INTO conversations VALUES (?,?,?)", (ident, DEMO_USER, now()))
            return dict(con.execute("SELECT id,created_at FROM conversations WHERE id=? AND user_id=?", (ident, DEMO_USER)).fetchone())

    def conversations(self):
        with self.connect() as con:
            return [dict(r) for r in con.execute("SELECT id,created_at FROM conversations WHERE user_id=? ORDER BY created_at DESC,id DESC LIMIT 100", (DEMO_USER,))]

    def history(self, ident):
        with self.connect() as con:
            if not con.execute("SELECT 1 FROM conversations WHERE id=? AND user_id=?", (ident, DEMO_USER)).fetchone():
                raise AppError("not_found", "Conversation not found.", 404)
            messages = [dict(r) for r in con.execute("SELECT * FROM messages WHERE conversation_id=? ORDER BY sequence", (ident,))]
            requests = []
            for r in con.execute("SELECT id,status,error_code,refs_json FROM requests WHERE conversation_id=?", (ident,)):
                requests.append({"id": r["id"], "status": r["status"], "error_code": r["error_code"], "references": json.loads(r["refs_json"])})
            events = [dict(r) for r in con.execute("SELECT id,request_id,content,created_at FROM app_events WHERE conversation_id=? ORDER BY created_at", (ident,))]
            return {"messages": messages, "requests": requests, "events": events}

    def preferences(self, value=None):
        with self.connect() as con:
            if value is not None:
                con.execute("UPDATE preferences SET cue_mode=?,use_saved_context=?,text_size=?,updated_at=? WHERE user_id=?", (value.cue_mode, int(value.use_saved_context), value.text_size, now(), DEMO_USER))
            row = dict(con.execute("SELECT cue_mode,use_saved_context,text_size,updated_at FROM preferences WHERE user_id=?", (DEMO_USER,)).fetchone())
            row["use_saved_context"] = bool(row["use_saved_context"])
            return row

    def session(self, ident, value):
        data = value.model_dump(mode="json")
        with self.connect() as con:
            old = con.execute("SELECT * FROM sessions WHERE id=? AND user_id=?", (ident, DEMO_USER)).fetchone()
            if old:
                public = {k: old[k] for k in data}
                if public == data:
                    return self.public_session(old)
                if old["outcome"] != "in_progress" or data["revision"] <= old["revision"]:
                    if data["outcome"] == "in_progress":
                        return self.public_session(old)  # a delayed checkpoint cannot reopen a result
                    raise AppError("session_conflict", "A different result is already saved for this attempt.", 409)
                if data["started_at"] != old["started_at"] or data["cue_mode"] != old["cue_mode"] or data["active_ms"] < old["active_ms"] or data["wall_ms"] < old["wall_ms"]:
                    raise AppError("session_conflict", "Session timing cannot move backwards or change its start.", 409)
            columns = list(data)
            con.execute(
                f"INSERT INTO sessions (id,user_id,skill,skill_version,{','.join(columns)}) VALUES (?,?,?, ?,{','.join('?' for _ in columns)}) "
                f"ON CONFLICT(id) DO UPDATE SET {','.join(f'{c}=excluded.{c}' for c in columns)}",
                (ident, DEMO_USER, "paced-breathing", "1", *data.values()),
            )
            return self.public_session(con.execute("SELECT * FROM sessions WHERE id=?", (ident,)).fetchone())

    @staticmethod
    def public_session(row):
        return {k: row[k] for k in row.keys() if k != "user_id"}

    def sessions(self):
        with self.connect() as con:
            return [self.public_session(r) for r in con.execute("SELECT * FROM sessions WHERE user_id=? ORDER BY started_at DESC,id DESC LIMIT 200", (DEMO_USER,))]

    def delete_history(self):
        with self.connect() as con:
            count = con.execute("DELETE FROM conversations WHERE user_id=?", (DEMO_USER,)).rowcount
            count += con.execute("DELETE FROM sessions WHERE user_id=?", (DEMO_USER,)).rowcount
            return {"deleted": count}

    def begin_request(self, conversation_id, request_id, content, mode):
        with self.connect() as con:
            if not con.execute("SELECT 1 FROM conversations WHERE id=? AND user_id=?", (conversation_id, DEMO_USER)).fetchone():
                raise AppError("not_found", "Conversation not found.", 404)
            old = con.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
            if old:
                if old["conversation_id"] != conversation_id or old["content"] != content:
                    raise AppError("request_conflict", "This request ID belongs to another question.", 409)
                if old["status"] in ("completed", "support"):
                    return None
            else:
                con.execute("INSERT INTO requests(id,conversation_id,content,status) VALUES (?,?,?,'pending')", (request_id, conversation_id, content))
                self.add_message(con, conversation_id, request_id, "user", content, "pending", mode)
            con.execute("UPDATE requests SET status='pending',error_code=NULL WHERE id=?", (request_id,))
            con.execute("UPDATE messages SET status='pending' WHERE request_id=?", (request_id,))
            attempt = str(uuid4())
            con.execute("INSERT INTO attempts(id,request_id,created_at,status,mode) VALUES (?,?,?,'pending',?)", (attempt, request_id, now(), mode))
            return attempt

    @staticmethod
    def add_message(con, conversation_id, request_id, role, content, status, mode):
        seq = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM messages WHERE conversation_id=?", (conversation_id,)).fetchone()[0]
        con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?,?)", (str(uuid4()), conversation_id, request_id, seq, role, content, now(), status, mode))

    def call_started(self, attempt):
        with self.connect() as con:
            con.execute("UPDATE attempts SET calls=calls+1 WHERE id=?", (attempt,))

    def finish(self, conversation_id, request_id, attempt, mode, reply=None, refs=None, saved_context=False, event=None):
        with self.connect() as con:
            status = "support" if event else "completed"
            if event:
                con.execute("INSERT INTO app_events VALUES (?,?,?,?,?)", (str(uuid4()), conversation_id, request_id, event, now()))
            else:
                self.add_message(con, conversation_id, request_id, "assistant", reply, "saved", mode)
            con.execute("UPDATE requests SET status=?,refs_json=?,used_saved_context=? WHERE id=?", (status, json.dumps(refs or []), int(saved_context), request_id))
            con.execute("UPDATE messages SET status='saved' WHERE request_id=?", (request_id,))
            con.execute("UPDATE attempts SET status=?,refs_json=? WHERE id=?", (status, json.dumps(refs or []), attempt))

    def fail(self, request_id, attempt, code):
        with self.connect() as con:
            con.execute("UPDATE requests SET status='failed',error_code=? WHERE id=?", (code, request_id))
            con.execute("UPDATE messages SET status='failed' WHERE request_id=? AND role='user'", (request_id,))
            con.execute("UPDATE attempts SET status='failed',error_code=? WHERE id=?", (code, attempt))

    def reply(self, request_id):
        with self.connect() as con:
            request = con.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
            msg = con.execute("SELECT * FROM messages WHERE request_id=? AND role='assistant'", (request_id,)).fetchone()
            event = con.execute("SELECT id,request_id,content,created_at FROM app_events WHERE request_id=?", (request_id,)).fetchone()
            return {"request_id": request_id, "saved": True, "mode": msg["mode"] if msg else "application",
                    "reply": dict(msg) if msg else None, "event": dict(event) if event else None,
                    "references": json.loads(request["refs_json"]), "used_saved_context": bool(request["used_saved_context"])}
