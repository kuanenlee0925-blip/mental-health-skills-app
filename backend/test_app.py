"""Fictional, isolated integration checks. No runtime DB or live provider calls."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.database import Database
from backend.main import create_app
from backend.provider import Provider, Settings
from backend.retrieval import QUERY, retrieve, validate_plan
from backend.errors import AppError


class AppTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "test.sqlite3")
        self.provider = Provider(Settings())
        self.app = create_app(self.db, self.provider)
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.cid = str(uuid4())
        self.client.post("/api/conversations", json={"id": self.cid}).raise_for_status()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.tmp.cleanup()

    def send(self, text, rid=None):
        return self.client.post(f"/api/conversations/{self.cid}/messages", json={"request_id": rid or str(uuid4()), "content": text})

    def session_payload(self, outcome="stopped", active=4000, revision=1):
        start = datetime(2026, 10, 22, tzinfo=timezone.utc)
        return {"revision": revision, "started_at": start.isoformat(), "ended_at": (start + timedelta(milliseconds=active)).isoformat() if outcome != "in_progress" else None,
                "outcome": outcome, "cue_mode": "text", "wall_ms": active, "excluded_ms": 0, "active_ms": active, "setup_ms": 1000}

    def test_chat_persist_retry_and_restart(self):
        rid = str(uuid4())
        reply = self.send("Explain the steps", rid)
        self.assertEqual(reply.status_code, 200, reply.text)
        self.assertTrue(reply.json()["saved"])
        self.assertEqual(reply.json()["mode"], "demo")
        self.assertEqual(self.send("Explain the steps", rid).json()["reply"]["id"], reply.json()["reply"]["id"])
        with self.db.connect() as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM messages").fetchone()[0], 2)
            self.assertEqual(con.execute("SELECT calls FROM attempts").fetchone()[0], 2)
        with TestClient(create_app(self.db, Provider(Settings()))) as restarted:
            data = restarted.get(f"/api/conversations/{self.cid}/messages").json()
            self.assertEqual([m["sequence"] for m in data["messages"]], [1, 2])
            self.assertEqual(data["messages"][1]["id"], reply.json()["reply"]["id"])

    def test_old_preferences_migrate_without_losing_history(self):
        reply = self.send("Explain the steps").json()
        with self.db.connect() as con:
            con.execute("ALTER TABLE preferences DROP COLUMN text_size")
            con.execute("PRAGMA user_version=1")
        self.db.initialize()
        self.assertEqual(self.db.preferences()["text_size"], "standard")
        saved = self.client.put("/api/preferences", json={"cue_mode": "ring", "use_saved_context": True, "text_size": "large"})
        self.assertEqual(saved.status_code, 200)
        self.db.initialize()
        self.assertEqual(self.db.preferences()["text_size"], "large")
        self.assertIn("Text size is large", self.send("What are my display settings?").json()["reply"]["content"])
        self.assertEqual(self.db.history(self.cid)["messages"][1]["id"], reply["reply"]["id"])
        self.assertEqual(self.client.put("/api/preferences", json={"text_size": "huge"}).status_code, 422)

    def test_failure_retry_does_not_invent_or_duplicate_reply(self):
        rid = str(uuid4())
        self.assertEqual(self.send("[demo:fail]", rid).status_code, 502)
        self.assertEqual(self.send("[demo:fail]", rid).status_code, 502)
        history = self.client.get(f"/api/conversations/{self.cid}/messages").json()
        self.assertEqual(len(history["messages"]), 1)
        self.assertEqual(history["messages"][0]["status"], "failed")
        self.assertEqual(history["requests"][0]["error_code"], "provider_failed")
        self.assertEqual(self.send("a different question", rid).status_code, 409)

    def test_support_rule_skips_both_calls_and_uses_event(self):
        result = self.send("Fictional input: HURT   myself").json()
        self.assertIsNone(result["reply"])
        self.assertIn("coursework", result["event"]["content"])
        with self.db.connect() as con:
            self.assertEqual(con.execute("SELECT calls FROM attempts").fetchone()[0], 0)
            self.assertEqual(con.execute("SELECT count(*) FROM messages WHERE role='assistant'").fetchone()[0], 0)

    def test_missing_configuration_and_budget(self):
        self.provider.settings = Settings(mode="live")
        result = self.send("Explain the steps")
        self.assertEqual(result.status_code, 503)
        self.assertEqual(result.json()["error"]["code"], "not_configured")
        self.provider.settings = Settings(mode="live", api_key="dummy", model="dummy", call_limit=0)
        self.assertEqual(self.send("Explain the steps").json()["error"]["code"], "call_limit")
        self.assertEqual(self.provider.live_calls, 0)

    def test_sessions_idempotency_ordering_and_terminal_guard(self):
        ident = str(uuid4())
        uri = "/api/sessions/" + ident
        initial = self.session_payload("in_progress", 0, 0)
        self.assertEqual(self.client.put(uri, json=initial).status_code, 200)
        final = self.session_payload()
        saved = self.client.put(uri, json=final)
        self.assertEqual(saved.status_code, 200, saved.text)
        self.assertEqual(self.client.put(uri, json=final).json(), saved.json())
        self.assertEqual(self.client.put(uri, json=initial).json()["outcome"], "stopped")
        self.assertEqual(len(self.client.get("/api/sessions").json()), 1)
        self.assertEqual(self.client.put(uri, json=self.session_payload("completed", 60100, 2)).status_code, 409)
        self.assertEqual(self.client.put("/api/sessions/" + str(uuid4()), json=self.session_payload("completed", 59999)).status_code, 422)

    def test_scoped_retrieval_empty_then_saved_history(self):
        self.client.put("/api/sessions/" + str(uuid4()), json=self.session_payload())
        plan = {"sql": QUERY, "params": {"kind": "session"}}
        self.assertEqual(retrieve(self.db, self.cid, False, plan), [])
        rows = retrieve(self.db, self.cid, True, plan)
        self.assertEqual(len(rows), 1)
        self.assertIn("outcome=stopped", rows[0]["content"])
        self.client.put("/api/preferences", json={"cue_mode": "ring", "use_saved_context": True})
        reply = self.send("What was my last session?")
        self.assertEqual(reply.status_code, 200, reply.text)
        self.assertEqual(reply.json()["references"], [rows[0]["record_id"]])
        self.assertTrue(reply.json()["used_saved_context"])

    def test_retrieval_other_conversation_and_user_scope(self):
        self.send("Explain the steps")
        self.client.put("/api/sessions/" + str(uuid4()), json=self.session_payload())
        other_cid = str(uuid4())
        self.db.conversation(other_cid)
        plan = {"sql": QUERY, "params": {"kind": "message"}}
        self.assertEqual(retrieve(self.db, other_cid, False, plan), [])
        self.assertEqual(len(retrieve(self.db, other_cid, True, plan)), 2)
        with self.db.connect() as con:
            con.execute("INSERT INTO demo_users VALUES ('other-user')")
            con.execute("INSERT INTO sessions SELECT ?, 'other-user', revision, skill, skill_version, cue_mode, started_at, ended_at, outcome, wall_ms, excluded_ms, active_ms, setup_ms FROM sessions", (str(uuid4()),))
        self.assertEqual(len(retrieve(self.db, other_cid, True, {"sql": QUERY, "params": {"kind": "session"}})), 1)
        # Even a query that tries to name a different conversation is outside the grammar.
        with self.assertRaises(AppError):
            retrieve(self.db, other_cid, True, {"sql": QUERY.replace("context_records", "messages"), "params": {"kind": "message"}})

    def test_sql_rejects_writes_comments_joins_unions_and_scope_bypass(self):
        for sql in ["DELETE FROM sessions", QUERY + "; DELETE FROM sessions", QUERY + " --comment", QUERY.replace("context_records", "sessions"),
                    QUERY.replace("record_id, kind, occurred_at, content", "*"), QUERY.replace("LIMIT 10", "LIMIT 100"),
                    QUERY + " UNION SELECT 1,2,3,4", QUERY.replace("WHERE kind = :kind", "WHERE 1=1"),
                    QUERY.replace("content FROM", "load_extension('x') FROM")]:
            with self.subTest(sql=sql), self.assertRaises(AppError):
                validate_plan({"sql": sql, "params": {"kind": "session"}})
        self.assertEqual(self.send("[demo:unsafe]").status_code, 422)
        self.assertEqual(self.client.get("/api/sessions").status_code, 200)

    def test_invalid_reference_and_provider_timeout(self):
        original = self.provider.call
        def invalid(stage, system, payload):
            if stage == "answer":
                return {"answer": "Invented", "record_ids": ["session:does-not-exist"]}
            return original(stage, system, payload)
        self.provider.call = invalid
        self.assertEqual(self.send("Explain the steps").json()["error"]["code"], "invalid_references")
        def timeout(*args):
            raise AppError("provider_timeout", "Test timeout", 504)
        self.provider.call = timeout
        self.assertEqual(self.send("Explain again").status_code, 504)
        with self.db.connect() as con:
            self.assertEqual(con.execute("SELECT count(*) FROM messages WHERE role='assistant'").fetchone()[0], 0)

    def test_storage_failure_stops_model_calls(self):
        original = self.db.begin_request
        self.db.begin_request = lambda *args: (_ for _ in ()).throw(sqlite3.OperationalError("fixture only"))
        self.assertEqual(self.send("Explain").status_code, 503)
        self.assertEqual(self.provider.live_calls, 0)
        self.db.begin_request = original

    def test_delete_retains_preferences_and_busy_prevents_midcall_changes(self):
        self.send("Explain")
        self.client.put("/api/preferences", json={"cue_mode": "ring", "use_saved_context": True})
        self.app.state.controller.lock.acquire()
        try:
            self.assertEqual(self.client.request("DELETE", "/api/history", json={"confirm": True}).status_code, 429)
        finally:
            self.app.state.controller.lock.release()
        self.assertEqual(self.client.request("DELETE", "/api/history", json={"confirm": True}).status_code, 200)
        self.assertEqual(self.client.get("/api/conversations").json(), [])
        self.assertEqual(self.client.get("/api/preferences").json()["cue_mode"], "ring")
        with self.db.connect() as con:
            self.assertEqual(con.execute("SELECT count(*) FROM messages").fetchone()[0], 0)
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])


if __name__ == "__main__":
    unittest.main()
