"""Validated HTTP contracts; persistence and business rules live elsewhere."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ConversationInput(Contract):
    id: UUID


class Conversation(Contract):
    id: str
    created_at: str


class Question(Contract):
    request_id: UUID
    content: str = Field(min_length=1, max_length=1200)

    @field_validator("content")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("Enter a question.")
        return value.strip()


class Preferences(Contract):
    cue_mode: Literal["text", "ring"] = "text"
    use_saved_context: bool = False
    text_size: Literal["standard", "large"] = "standard"


class SavedPreferences(Preferences):
    updated_at: str


class SessionInput(Contract):
    revision: int = Field(ge=0)
    started_at: datetime
    ended_at: datetime | None = None
    outcome: Literal["in_progress", "completed", "stopped", "interrupted"]
    cue_mode: Literal["text", "ring"]
    wall_ms: int = Field(ge=0, le=604800000)
    excluded_ms: int = Field(ge=0, le=604800000)
    active_ms: int = Field(ge=0, le=604800000)
    setup_ms: int = Field(ge=0, le=604800000)

    @model_validator(mode="after")
    def timing(self):
        if self.started_at.tzinfo is None or (self.ended_at and self.ended_at.tzinfo is None):
            raise ValueError("Use timestamps with a timezone.")
        if self.active_ms != self.wall_ms - self.excluded_ms:
            raise ValueError("Active duration must equal wall duration minus excluded pauses.")
        if self.outcome == "in_progress" and self.ended_at is not None:
            raise ValueError("An unfinished session has no end time.")
        if self.outcome != "in_progress" and self.ended_at is None:
            raise ValueError("A terminal session needs an end time.")
        if self.ended_at and self.ended_at < self.started_at:
            raise ValueError("End time cannot precede start time.")
        if self.outcome == "completed" and not 60000 <= self.active_ms <= 90000:
            raise ValueError("Completed pacing must last 60–90 seconds.")
        return self


class Session(SessionInput):
    id: str
    skill: str
    skill_version: str


class Message(Contract):
    id: str
    conversation_id: str
    request_id: str
    sequence: int
    role: Literal["user", "assistant"]
    content: str
    created_at: str
    status: str
    mode: str


class RequestRecord(Contract):
    id: str
    status: str
    error_code: str | None
    references: list[str]


class AppEvent(Contract):
    id: str
    request_id: str
    content: str
    created_at: str


class ConversationHistory(Contract):
    messages: list[Message]
    requests: list[RequestRecord]
    events: list[AppEvent]


class ChatReply(Contract):
    request_id: str
    saved: bool
    mode: str
    reply: Message | None = None
    event: AppEvent | None = None
    references: list[str] = Field(default_factory=list)
    used_saved_context: bool = False


class DeleteInput(Contract):
    confirm: Literal[True]


class DeleteResult(Contract):
    deleted: int


class Health(Contract):
    mode: str
    configured: bool
    live_calls: int
    live_call_limit: int
