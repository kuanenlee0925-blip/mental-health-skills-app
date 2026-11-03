"""Voice mocks only: no actual key, microphone, session or billable call."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
import httpx

from backend.database import Database
from backend.errors import AppError
from backend.main import create_app
from backend.provider import Provider, Settings
from backend.voice import LiveProvider, VoiceController, VoiceOffer, VoiceSettings

SDP = "v=0\r\no=- 1 1 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\na=ice-ufrag:fictional\r\na=fingerprint:sha-256 AA:BB\r\n"


class FakeLive:
    def __init__(self):
        self.created, self.closed = [], []

    def create(self, sdp):
        self.created.append(sdp)
        return "live_fictional_1", SDP

    def close(self, ident):
        self.closed.append(ident)
        return True


class VoiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "voice-tests.sqlite3")
        self.fake = FakeLive()
        self.settings = VoiceSettings(enabled=True, api_key="fictional-test-value")
        self.voice = VoiceController(self.settings, self.fake)
        self.client = TestClient(create_app(self.db, Provider(Settings()), self.voice))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.tmp.cleanup()

    def offer(self):
        return {"request_id": str(uuid4()), "sdp": SDP}

    def test_config_contains_no_credentials_or_prompt(self):
        self.assertEqual(self.client.get("/api/voice/config").json(), {"configured": True, "max_session_seconds": 300})
        self.settings.api_key = ""
        self.assertEqual(self.client.post("/api/voice/sessions", json=self.offer()).status_code, 503)
        self.assertEqual(self.fake.created, [])

    def test_invalid_sdp_oversize_and_browser_config_are_rejected(self):
        for extra in [{"sdp": "invalid"}, {"sdp": "x" * 65537}, {"model": "browser-override"}, {"instructions": "browser-policy"}, {"store": True}, {"sdp": SDP + "\x00"}]:
            with self.subTest(extra=list(extra)):
                self.assertEqual(self.client.post("/api/voice/sessions", json={**self.offer(), **extra}).status_code, 422)
        self.assertEqual(self.fake.created, [])

    def test_create_duplicate_end_and_no_voice_database_records(self):
        offer = self.offer()
        result = self.client.post("/api/voice/sessions", json=offer)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(set(result.json()), {"session_id", "sdp", "max_session_seconds"})
        self.assertEqual(self.client.post("/api/voice/sessions", json=offer).status_code, 409)
        self.assertEqual(self.client.post("/api/voice/sessions", json=self.offer()).status_code, 429)
        path = "/api/voice/sessions/" + offer["request_id"] + "/close"
        self.assertTrue(self.client.post(path).json()["closed"])
        self.assertTrue(self.client.post(path).json()["closed"])
        self.assertEqual(self.fake.closed, ["live_fictional_1"])
        with self.db.connect() as con:
            for table in ("messages", "sessions", "conversations", "app_events"):
                self.assertEqual(con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)

    def test_cancel_before_creation_prevents_provider_call(self):
        offer = self.offer()
        self.client.post("/api/voice/sessions/" + offer["request_id"] + "/close")
        self.assertEqual(self.client.post("/api/voice/sessions", json=offer).status_code, 409)
        self.assertEqual(self.fake.created, [])

    def test_late_result_after_cancel_closes_provider_session(self):
        entered, release = Event(), Event()
        def delayed(sdp):
            entered.set()
            release.wait(2)
            return "live_late", SDP
        self.fake.create = delayed
        offer = VoiceOffer(**self.offer())
        with ThreadPoolExecutor() as pool:
            future = pool.submit(self.voice.create, offer)
            self.assertTrue(entered.wait(2))
            self.assertTrue(self.voice.close(str(offer.request_id))["pending"])
            release.set()
            with self.assertRaises(AppError):
                future.result(2)
        self.assertEqual(self.fake.closed, ["live_late"])

    def test_server_timer_and_shutdown_use_same_owned_cleanup(self):
        offer = VoiceOffer(**self.offer())
        self.voice.create(offer)
        timer = self.voice.entries[str(offer.request_id)]["timer"]
        timer.function()
        self.assertEqual(self.fake.closed, ["live_fictional_1"])
        self.voice.shutdown()
        self.assertEqual(len(self.fake.closed), 1)

    def test_failed_closure_is_not_reported_as_confirmed(self):
        self.fake.close = lambda ident: False
        offer = VoiceOffer(**self.offer())
        self.voice.create(offer)
        self.assertFalse(self.voice.close(str(offer.request_id))["closed"])

    def test_cross_origin_paid_creation_is_rejected(self):
        response = self.client.post("/api/voice/sessions", json=self.offer(), headers={"Origin": "https://unrelated.example"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.fake.created, [])

    def test_provider_payload_is_server_owned_and_allowlisted(self):
        captured = []
        def handle(request):
            import json
            captured.append(json.loads(request.content))
            return httpx.Response(201, json={"session": {"id": "live_fixture"}, "transport": {"type": "webrtc", "sdp": SDP}})
        actual_client = httpx.Client
        with patch("backend.voice.httpx.Client", side_effect=lambda **kwargs: actual_client(transport=httpx.MockTransport(handle), **kwargs)):
            result = LiveProvider(self.settings).create(SDP)
        config = captured[0]["session"]
        self.assertEqual(config["model"], "gpt-live-1")
        self.assertFalse(config["store"])
        self.assertEqual(config["delegation"]["responses"]["model"], "gpt-6-luna")
        self.assertEqual(config["delegation"]["responses"]["tools"], [])
        self.assertEqual(config["client"]["data_channel"]["allowed_client_events"], ["session.close"])
        self.assertEqual([s["type"] for s in config["client"]["data_channel"]["allowed_server_events"]], ["session.started", "session.closed", "error"])
        self.assertEqual(result[0], "live_fixture")

    def test_provider_failure_timeout_and_malformed_answer_are_sanitized(self):
        actual_client = httpx.Client
        responses = [httpx.Response(401, text="sensitive fixture error"), httpx.Response(201, json={"bad": "shape"}),
                     httpx.Response(201, json={"session": {"id": "live_malformed"}, "transport": {"type": "webrtc", "sdp": "bad"}})]
        for response in responses:
            provider = LiveProvider(self.settings)
            with patch("backend.voice.httpx.Client", side_effect=lambda **kwargs: actual_client(transport=httpx.MockTransport(lambda request: response), **kwargs)), patch.object(provider, "close", return_value=True) as cleanup:
                with self.assertRaises(AppError) as error:
                    provider.create(SDP)
                self.assertNotIn("sensitive", error.exception.message)
                if "live_malformed" in response.text:
                    cleanup.assert_called_once_with("live_malformed")
        def timeout(request):
            raise httpx.ReadTimeout("fixture secret")
        with patch("backend.voice.httpx.Client", side_effect=lambda **kwargs: actual_client(transport=httpx.MockTransport(timeout), **kwargs)):
            with self.assertRaises(AppError) as error:
                LiveProvider(self.settings).create(SDP)
            self.assertEqual(error.exception.status, 504)


if __name__ == "__main__":
    unittest.main()
