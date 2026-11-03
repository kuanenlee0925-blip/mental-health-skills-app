"""OpenAI Live creation and bounded cleanup; no audio/transcript persistence."""
from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import re
from threading import Lock, Timer
import time
from uuid import UUID

from dotenv import load_dotenv
from fastapi import APIRouter, Request
import httpx
from pydantic import Field, field_validator
from websockets.sync.client import connect

from .errors import AppError
from .models import Contract
from .voice_prompts import LIVE_INSTRUCTIONS, DELEGATED_INSTRUCTIONS

SESSION_URL = "https://api.openai.com/v1/live/sessions"
SAFE_ID = re.compile(r"[a-zA-Z0-9_-]{1,128}")
# Do not let a global DEBUG setting log handshake credentials or reflected audio.
quiet_logger = logging.Logger("voice-cleanup-private", level=logging.CRITICAL + 1)
quiet_logger.addHandler(logging.NullHandler())
quiet_logger.propagate = False


def bounded_sdp(value):
    if not isinstance(value, str) or not 20 <= len(value) <= 65536 or "\x00" in value:
        raise ValueError("Invalid SDP")
    lines = value.replace("\r\n", "\n").split("\n")
    if lines[0] != "v=0" or not any(line.startswith("m=audio ") for line in lines):
        raise ValueError("An audio SDP description is required")
    if not any(line.startswith("a=fingerprint:") for line in lines) or not any(line.startswith("a=ice-ufrag:") for line in lines):
        raise ValueError("An ICE and DTLS SDP description is required")
    return value


class VoiceOffer(Contract):
    request_id: UUID
    sdp: str = Field(min_length=20, max_length=65536)

    @field_validator("sdp")
    @classmethod
    def validate_sdp(cls, value):
        return bounded_sdp(value)


class VoiceConfig(Contract):
    configured: bool
    max_session_seconds: int


class VoiceAnswer(Contract):
    session_id: str
    sdp: str
    max_session_seconds: int


class VoiceClosed(Contract):
    closed: bool
    pending: bool = False


@dataclass
class VoiceSettings:
    enabled: bool = False
    api_key: str = ""
    live_model: str = "gpt-live-1"
    backend_model: str = "gpt-6-luna"
    max_seconds: int = 300
    session_limit: int = 3

    @classmethod
    def load(cls):
        load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
        def number(name, default, upper):
            try:
                return min(upper, max(1, int(os.getenv(name, str(default)))))
            except ValueError:
                return default
        return cls(os.getenv("VOICE_ENABLED", "false").lower() == "true", os.getenv("OPENAI_API_KEY", ""),
                   os.getenv("VOICE_LIVE_MODEL", "gpt-live-1"), os.getenv("VOICE_BACKEND_MODEL", "gpt-6-luna"),
                   number("VOICE_MAX_SESSION_SECONDS", 300, 300), number("VOICE_SESSION_LIMIT", 3, 10))


class LiveProvider:
    def __init__(self, settings):
        self.settings = settings

    def create(self, offer):
        configuration = {
            "model": self.settings.live_model,
            "instructions": LIVE_INSTRUCTIONS,
            "store": False,
            "audio": {"output": {"voice": "marin"}},
            "delegation": {"type": "responses", "responses": {
                "model": self.settings.backend_model, "instructions": DELEGATED_INSTRUCTIONS,
                "tools": [], "tool_choice": "none", "max_output_tokens": 500,
            }},
            "client": {"data_channel": {
                "allowed_client_events": ["session.close"],
                "allowed_server_events": [{"type": t} for t in ("session.started", "session.closed", "error")],
            }},
        }
        try:
            with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
                started = time.monotonic()
                with client.stream("POST", SESSION_URL, headers={"Authorization": "Bearer " + self.settings.api_key},
                                   json={"session": configuration, "transport": {"type": "webrtc", "sdp": offer}}) as response:
                    if response.status_code != 201:
                        raise AppError("voice_provider_failed", "Voice could not connect. Text chat is still available.", 502)
                    raw = bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw) > 131072 or time.monotonic() - started > 15:
                            raise AppError("voice_provider_timeout", "Voice setup exceeded its response limit. Text chat is still available.", 504)
            data = json.loads(raw)
            ident = data["session"]["id"]
            if not isinstance(ident, str) or not SAFE_ID.fullmatch(ident):
                raise ValueError("invalid session ID")
            try:
                if data["transport"]["type"] != "webrtc":
                    raise ValueError("wrong transport")
                answer = bounded_sdp(data["transport"]["sdp"])
            except (KeyError, TypeError, ValueError):
                self.close(ident)
                raise
            return ident, answer
        except httpx.TimeoutException as exc:
            raise AppError("voice_provider_timeout", "Voice setup timed out. No automatic retry was made.", 504) from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise AppError("voice_invalid_response", "Voice returned an unusable connection. Text chat is still available.", 502) from exc

    def close(self, session_id):
        # Only called with provider IDs validated above and held by this process.
        if not SAFE_ID.fullmatch(session_id):
            return False
        try:
            with connect("wss://api.openai.com/v1/live/sessions/" + session_id + "/attach",
                         additional_headers={"Authorization": "Bearer " + self.settings.api_key},
                         open_timeout=3, close_timeout=1, max_size=262144, max_queue=4,
                         proxy=None, logger=quiet_logger) as ws:
                ws.send(json.dumps({"type": "session.close"}))
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    event = json.loads(ws.recv(timeout=max(0.01, deadline - time.monotonic())))
                    if event.get("type") == "session.closed":
                        return True
                    # Reflected audio/transcript events are discarded, never logged or saved.
        except Exception:
            return False
        return False


class VoiceController:
    def __init__(self, settings=None, provider=None):
        self.settings = settings or VoiceSettings.load()
        self.provider = provider or LiveProvider(self.settings)
        self.lock = Lock()
        self.entries = {}
        self.starts = 0

    def config(self):
        return {"configured": bool(self.settings.enabled and self.settings.api_key and self.settings.live_model and self.settings.backend_model),
                "max_session_seconds": self.settings.max_seconds}

    def create(self, value):
        if not self.config()["configured"]:
            raise AppError("voice_unconfigured", "Voice needs an OpenAI API key and backend setup. You can keep using text chat.", 503)
        request_id = str(value.request_id)
        with self.lock:
            if request_id in self.entries:
                raise AppError("voice_duplicate", "This voice attempt was already started or canceled. Start a fresh attempt explicitly.", 409)
            if any(e["status"] in ("pending", "active", "closing") for e in self.entries.values()):
                raise AppError("voice_busy", "Another voice session is connecting or active. End it before starting again.", 429)
            if self.starts >= self.settings.session_limit:
                raise AppError("voice_limit", "The voice test limit for this server session has been reached.", 429)
            self.starts += 1
            entry = {"status": "pending", "canceled": False, "session_id": None, "confirmed": False, "timer": None}
            self.entries[request_id] = entry
        try:
            ident, answer = self.provider.create(value.sdp)
            with self.lock:
                entry["session_id"] = ident
                canceled = entry["canceled"]
                entry["status"] = "active"
                if not canceled:
                    timer = Timer(self.settings.max_seconds, lambda: self.close(request_id))
                    timer.daemon = True
                    entry["timer"] = timer
                    timer.start()
            if canceled:
                self.close(request_id)
                raise AppError("voice_canceled", "Voice setup was canceled and cleanup was requested.", 409)
            return {"session_id": ident, "sdp": answer, "max_session_seconds": self.settings.max_seconds}
        except Exception:
            with self.lock:
                if entry["status"] == "pending":
                    entry["status"] = "failed"
            raise

    def close(self, request_id):
        with self.lock:
            entry = self.entries.get(request_id)
            if entry is None:
                # A cancel can beat its POST on the network. Keep a bounded tombstone.
                if len(self.entries) < 100:
                    self.entries[request_id] = {"status": "closed", "canceled": True, "session_id": None, "confirmed": True, "timer": None}
                return {"closed": True, "pending": False}
            entry["canceled"] = True
            if entry["status"] == "pending":
                return {"closed": False, "pending": True}
            if entry["status"] in ("closed", "failed", "closing"):
                return {"closed": entry["confirmed"], "pending": entry["status"] == "closing"}
            entry["status"] = "closing"
            if entry["timer"]:
                entry["timer"].cancel()
            ident = entry["session_id"]
        confirmed = self.provider.close(ident) if ident else True
        with self.lock:
            entry["status"] = "closed"
            entry["confirmed"] = confirmed
        return {"closed": confirmed, "pending": False}

    def shutdown(self):
        for ident in list(self.entries):
            self.close(ident)


def voice_router(controller):
    router = APIRouter(prefix="/api/voice", tags=["voice"])

    @router.get("/config", response_model=VoiceConfig)
    def configuration():
        return controller.config()

    @router.post("/sessions", response_model=VoiceAnswer)
    def create(value: VoiceOffer):
        return controller.create(value)

    @router.post("/sessions/{request_id}/close", response_model=VoiceClosed)
    def close(request_id: UUID):
        return controller.close(str(request_id))

    return router
