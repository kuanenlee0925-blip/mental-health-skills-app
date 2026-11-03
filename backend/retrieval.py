"""A deliberately small SQL language, followed by read-only scoped execution."""
import re
import sqlite3
import time
from uuid import UUID

from .database import DEMO_USER
from .errors import AppError

QUERY = "SELECT record_id, kind, occurred_at, content FROM context_records WHERE kind = :kind ORDER BY occurred_at DESC LIMIT 10"
SCHEMA = (
    "context_records(record_id TEXT, kind TEXT, occurred_at TEXT, content TEXT). "
    "kind is message, session, or preference. Records already have server-enforced user/consent scope. "
    "Return JSON only: {\"sql\": \"" + QUERY + "\", \"params\": {\"kind\": \"session\"}}. "
    "Choose kind=session for practice/activity history: last saved practice, last exercise, duration, stopped or completed. "
    "Practice and exercise are synonyms for session, NOT chat messages. For example, 'what was my last saved practice?' requires kind=session. "
    "Choose preference for display/settings and message only for recalling what was said in a conversation. "
    "Use exactly these four columns, this table, kind=:kind, descending time, and a LIMIT from 1 to 10."
)
PATTERN = re.compile(
    r"SELECT record_id, kind, occurred_at, content FROM context_records WHERE kind = :kind ORDER BY occurred_at DESC LIMIT ([1-9]|10)", re.I
)


def validate_plan(plan):
    if not isinstance(plan, dict) or set(plan) != {"sql", "params"}:
        raise AppError("retrieval_rejected", "The proposed history query was rejected.", 422)
    sql, params = plan["sql"], plan["params"]
    if not isinstance(sql, str) or len(sql) > 500 or not PATTERN.fullmatch(" ".join(sql.split())):
        raise AppError("retrieval_rejected", "The proposed history query was rejected.", 422)
    if not isinstance(params, dict) or set(params) != {"kind"} or params["kind"] not in ("message", "session", "preference"):
        raise AppError("retrieval_rejected", "The proposed history filter was rejected.", 422)
    return " ".join(sql.split()), params


def retrieve(db, conversation_id, use_saved_context, plan):
    sql, params = validate_plan(plan)
    ident = str(UUID(conversation_id))
    con = sqlite3.connect(db.path.as_uri() + "?mode=ro", uri=True, timeout=2)
    con.row_factory = sqlite3.Row
    try:
        scope = f"c.user_id='{DEMO_USER}'" if use_saved_context else f"c.user_id='{DEMO_USER}' AND c.id='{ident}'"
        view = f"""SELECT 'message:' || m.id AS record_id, 'message' AS kind,
            m.created_at AS occurred_at, m.role || ': ' || m.content AS content
            FROM messages m JOIN conversations c ON c.id=m.conversation_id
            WHERE {scope} AND m.status='saved'"""
        if use_saved_context:
            view += f""" UNION ALL SELECT 'session:' || id, 'session', started_at,
                'outcome=' || outcome || '; cue_mode=' || cue_mode || '; active_ms=' || active_ms || '; excluded_ms=' || excluded_ms
                FROM sessions WHERE user_id='{DEMO_USER}'
                UNION ALL SELECT 'preference:' || user_id, 'preference', updated_at,
                'cue_mode=' || cue_mode || '; use_saved_context=' || use_saved_context || '; text_size=' || text_size
                FROM preferences WHERE user_id='{DEMO_USER}'"""
        # The interpolation above contains only trusted constants and a parsed UUID.
        # No model text is interpolated into the view, its scope, or bound values.
        con.execute("CREATE TEMP VIEW context_records AS " + view)
        con.execute("PRAGMA query_only=ON")
        allowed_tables = {"messages", "conversations", "sessions", "preferences"}

        def authorize(action, table, column, database, source):
            if action == sqlite3.SQLITE_SELECT:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ:
                if table == "context_records" and column in {"record_id", "kind", "occurred_at", "content"}:
                    return sqlite3.SQLITE_OK
                if source == "context_records" and table in allowed_tables:
                    return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        con.set_authorizer(authorize)
        deadline = time.monotonic() + 0.1
        ticks = 0

        def budget():
            nonlocal ticks
            ticks += 1
            return int(ticks > 1000 or time.monotonic() > deadline)

        con.set_progress_handler(budget, 100)
        records, chars = [], 0
        for row in con.execute(sql, params).fetchmany(10):
            record = dict(row)
            size = sum(len(str(v)) for v in record.values())
            if chars + size > 8000:
                break
            records.append(record)
            chars += size
        return records
    except sqlite3.DatabaseError as exc:
        raise AppError("retrieval_failed", "Saved context could not be read. You can retry the question.", 503) from exc
    finally:
        con.close()
