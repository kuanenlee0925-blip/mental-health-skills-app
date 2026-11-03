"""Backend-only model adapter. Demo fixtures never make an external request."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import time

from dotenv import load_dotenv
import httpx

from .errors import AppError
from .retrieval import QUERY


@dataclass
class Settings:
    mode: str = "demo"
    api_key: str = ""
    model: str = ""
    call_limit: int = 50

    @classmethod
    def load(cls):
        load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
        mode = os.getenv("MODEL_MODE", "demo").lower()
        if mode not in ("demo", "live"):
            mode = "unconfigured"
        try:
            limit = min(50, max(0, int(os.getenv("LIVE_CALL_LIMIT", "50"))))
        except ValueError:
            limit = 0
        return cls(mode, os.getenv("MODEL_API_KEY", ""), os.getenv("MODEL_NAME", ""), limit)


class Provider:
    def __init__(self, settings):
        self.settings = settings
        self.live_calls = 0

    @property
    def configured(self):
        return self.settings.mode == "demo" or (self.settings.mode == "live" and bool(self.settings.api_key and self.settings.model))

    def ensure_capacity(self):
        if not self.configured:
            raise AppError("not_configured", "Live AI is not configured. Breathing and support remain available.", 503)
        if self.settings.mode == "live" and self.live_calls + 2 > self.settings.call_limit:
            raise AppError("call_limit", "The live-call limit has been reached for this server session.", 429)

    def call(self, stage, system, payload):
        if self.settings.mode == "demo":
            return self.demo(stage, payload)
        self.live_calls += 1  # Failed calls count too. Chat controller serializes requests.
        body = {"model": self.settings.model, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ], "temperature": 0, "max_tokens": 700, "response_format": {"type": "json_object"}, "stream": False}
        try:
            start = time.monotonic()
            with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
                with client.stream("POST", "https://openrouter.ai/api/v1/chat/completions", headers={
                    "Authorization": "Bearer " + self.settings.api_key, "Content-Type": "application/json"
                }, json=body) as response:
                    if response.status_code != 200:
                        raise AppError("provider_failed", "AI could not respond. Your question is retained; you can retry.", 502)
                    raw = bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw) > 65536:
                            raise AppError("invalid_reply", "AI returned an unusable response. You can retry.", 502)
                        if time.monotonic() - start > 15:
                            raise AppError("provider_timeout", "AI took too long to respond. You can retry.", 504)
            outer = json.loads(raw)
            content = outer["choices"][0]["message"]["content"]
            if not isinstance(content, str) or len(content) > 12000:
                raise ValueError("invalid content")
            return json.loads(content)
        except httpx.TimeoutException as exc:
            raise AppError("provider_timeout", "AI took too long to respond. You can retry.", 504) from exc
        except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise AppError("provider_failed", "AI could not return a usable response. You can retry.", 502) from exc

    @staticmethod
    def demo(stage, payload):
        question = payload["question"].lower()
        if question == "[demo:fail]":
            raise AppError("provider_failed", "Demo failure: no answer was generated. Your question is retained.", 502)
        if stage == "plan":
            if question == "[demo:unsafe]":
                return {"sql": "DELETE FROM sessions", "params": {}}
            kind = "preference" if any(w in question for w in ("display", "setting", "preference")) else "session" if any(w in question for w in ("session", "last", "history", "record", "practice", "exercise duration")) else "message"
            return {"sql": QUERY, "params": {"kind": kind}}
        records = payload["records"]
        if any(w in question for w in ("last", "history", "record", "display", "setting", "preference", "session")):
            if records:
                r = records[0]
                fields = dict(part.split("=", 1) for part in r["content"].split("; ") if "=" in part)
                if r["kind"] == "session":
                    answer = (f"Your latest saved practice was {fields['outcome'].replace('_', ' ')} after "
                              f"{int(fields['active_ms']) / 1000:.1f} seconds, using {fields['cue_mode']} cues. "
                              f"There were {int(fields['excluded_ms']) / 1000:.1f} seconds of paused time.")
                elif r["kind"] == "preference":
                    answer = f"Your saved display choice is {fields['cue_mode']} cues. Text size is {fields.get('text_size', 'standard')}. Saved-history sharing is {'on' if fields['use_saved_context'] == '1' else 'off'}."
                else:
                    answer = "The matching saved message says: " + r["content"]
                return {"answer": "Demo response Â· " + answer, "record_ids": [r["record_id"]]}
            return {"answer": "Demo response Â· I have no matching saved records available for this question. Past sessions and settings are shared only when you turn on â€˜Use saved historyâ€™. I cannot infer what happened.", "record_ids": []}
        return {"answer": "Demo response Â· The exercise has six cycles: inhale for 4 seconds, then exhale for 6. It takes about 60 seconds. You can stop at any time. Opening support pauses the cue; you choose whether to resume. Text cues are the default.", "record_ids": []}
