"""Thin HTTP routes. Run one worker, on localhost only."""
from contextlib import asynccontextmanager
import asyncio
import sqlite3
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from .chat import Chat
from .database import Database
from .errors import AppError
from .models import (AppEvent, ChatReply, Conversation, ConversationHistory,
                     ConversationInput, DeleteInput, DeleteResult, Health, Preferences,
                     Question, SavedPreferences, Session, SessionInput)
from .provider import Provider, Settings
from .voice import VoiceController, voice_router


def create_app(database=None, provider=None, voice=None):
    db = database or Database()
    model = provider or Provider(Settings.load())
    controller = Chat(db, model)
    voice_controller = voice or VoiceController()

    @asynccontextmanager
    async def lifespan(app):
        db.initialize()
        try:
            yield
        finally:
            await asyncio.to_thread(voice_controller.shutdown)

    app = FastAPI(title="Paced breathing coursework API", version="0.2.0", lifespan=lifespan)
    app.state.db, app.state.controller = db, controller
    app.include_router(voice_router(voice_controller))

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        host = request.url.hostname
        origin = request.headers.get("origin")
        allowed_origins = {"http://127.0.0.1:5174", "http://localhost:5174", "http://127.0.0.1:8002", "http://localhost:8002"}
        if host not in {"127.0.0.1", "localhost", "testserver"} or (request.method not in {"GET", "HEAD"} and origin and origin not in allowed_origins):
            return JSONResponse(status_code=403, content={"error": {"code": "local_only", "message": "This prototype accepts only its local application origin."}})
        return await call_next(request)

    @app.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}})

    @app.exception_handler(sqlite3.Error)
    async def storage_error(request: Request, exc):
        return JSONResponse(status_code=503, content={"error": {"code": "storage_failed", "message": "Storage is unavailable. This operation is not confirmed saved. You can retry."}})

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc):
        return JSONResponse(status_code=422, content={"error": {"code": "invalid_input", "message": "Check the supplied fields and timing values."}})

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc):
        return JSONResponse(status_code=exc.status_code, content={"error": {"code": "http_error", "message": "This API route or operation is unavailable."}})

    @app.get("/api/health", response_model=Health)
    def health():
        return {"mode": model.settings.mode, "configured": model.configured, "live_calls": model.live_calls, "live_call_limit": model.settings.call_limit}

    @app.post("/api/conversations", response_model=Conversation)
    def create_conversation(value: ConversationInput):
        return db.conversation(str(value.id))

    @app.get("/api/conversations", response_model=list[Conversation])
    def conversations():
        return db.conversations()

    @app.get("/api/conversations/{ident}/messages", response_model=ConversationHistory)
    def messages(ident: UUID):
        return db.history(str(ident))

    @app.post("/api/conversations/{ident}/messages", response_model=ChatReply)
    def submit(ident: UUID, value: Question):
        return controller.submit(str(ident), value)

    @app.put("/api/sessions/{ident}", response_model=Session)
    def save_session(ident: UUID, value: SessionInput):
        return db.session(str(ident), value)

    @app.get("/api/sessions", response_model=list[Session])
    def sessions():
        return db.sessions()

    @app.get("/api/preferences", response_model=SavedPreferences)
    def preferences():
        return db.preferences()

    @app.put("/api/preferences", response_model=SavedPreferences)
    def update_preferences(value: Preferences):
        return controller.change(lambda: db.preferences(value))

    @app.delete("/api/history", response_model=DeleteResult)
    def delete(value: DeleteInput):
        return controller.change(db.delete_history)

    return app


app = create_app()
