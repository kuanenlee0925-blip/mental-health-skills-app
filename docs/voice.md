# Live audio activity — implementation and manual verification

Scope added by the student on October 22, 2026, alongside Part Two. Read the
complete Canvas activity in the student's existing Chrome tab. No public-demo
or paid session has been started. The class demo video was not played.

## Implemented increment and boundaries

The optional question screen includes VoicePanel.vue and a native
WebRTC lifecycle controller. backend/voice.py and backend/voice_prompts.py
keep credentials, model names, prompts, event permissions and provider URL there.
Reuse FastAPI, HTTPX, and the current Vue styles. Native browser APIs carry
audio; the extra Python websockets dependency supports server-side closure.
No second application, recording, transcript storage, tools, or history upload.

Flow: explicit microphone action → GET /api/voice/config → browser microphone
permission → peer and oai-events data channel → generated offer after ICE
gathering → POST /api/voice/sessions → FastAPI adds policy and calls OpenAI →
validated SDP answer → browser waits for session.started → Active. Keep text
chat available throughout. Muting disables microphone tracks but does not end
the session, assistant playback or billing. End releases tracks immediately.

Use a UUID request_id to prevent duplicate provider starts. The cleanup route
POST /api/voice/sessions/{request_id}/close can mark a pending start canceled;
the backend closes its resulting provider session when that late response arrives.
It can only close IDs owned by this local server, never arbitrary provider IDs.
All session bookkeeping is in memory; audio and transcripts never enter SQLite.
The backend closes by authenticated sideband session.close; the browser also
sends session.close and waits briefly for session.closed before releasing the
peer/data channel. Report finalization honestly. Timers and cleanup cannot
guarantee remote termination after a process crash or loss of all network access.

Lifecycle: Idle → Permission → Connecting → Active ↔ Muted → Closing → Closed.
Denial, unsupported media, malformed SDP, provider/transport/playback failure,
and missing configuration remain distinct from a working call. A blocked audio
element offers an explicit Enable assistant audio control. Support, navigation,
page exit, hidden tab, component unmount and duration limit all trigger cleanup.

## Official sources verified October 22, 2026

- [Create Live session](https://developers.openai.com/api/reference/resources/live/methods/create)
- [Live session lifecycle](https://developers.openai.com/api/docs/guides/live-conversations)
- [Live prompting](https://developers.openai.com/api/docs/guides/live-prompting)
- [Responses delegation](https://developers.openai.com/api/docs/guides/live-delegation)
- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
- [Sideband connection](https://developers.openai.com/api/reference/resources/live/sideband-websocket)

Voice model: gpt-live-1. Delegated model: gpt-6-luna. The two prompt layers are
server-owned. Live handles conversational delivery; delegated Responses handles
reviewed app knowledge. Voice receives no saved text/session history in this
increment. `store: false` disables session retrieval/fork storage; it is not a
general statement about the provider's data-retention policies.

## Pending live checks

After mocks and the production build pass, configure an OpenAI key with model
access in ignored backend/.env and restart FastAPI. Do not paste it into chat.
The live test needs the student's microphone permission and an explicit choice
to start a paid session. Keep the classroom observation under 60 seconds:

1. In the optional question screen, click Start voice and allow the microphone.
2. Wait for Active. Use a fictional question: “What happens if I stop this practice?”
3. Interrupt once, then change the question to “Does opening support pause it?”
4. Mute; verify that the mic is muted while the session can still play audio.
5. Unmute, then End before 60 seconds. Check that the browser mic indicator ends.
6. Open support and navigate away during a separate mock attempt; inspect cleanup.
7. Check SQLite: no voice messages, audio, transcripts or voice session records.
8. Compare the same fictional scenario with the class-linked public demo manually:
   turn-taking, interruption, tone, boundaries. Do not claim either observation
   before actually performing it.

## Verification recorded October 24

All 10 backend voice tests and 12 frontend voice tests passed. These cover input
validation and server-owned policy; duplicate starts and cancellation before or
after a late provider response; missing configuration, permission denial and
provider errors; blocked playback; Mute versus End; and navigation, support,
page-exit, hidden-tab, unmount, duration and shutdown cleanup. Fake media/peer and
provider objects were used. The complete application has 39 passing tests and a
passing Vite build. See [verification](verification.md) for commands/evidence.

In actual Chrome, Start voice without configuration showed the unavailable state
and a subsequent text question still worked. No microphone permission was
requested and no paid call was made. The backend configuration endpoint reports
configured=false. This is failure-path evidence, not a successful voice call.

Source locations: frontend/src/VoicePanel.vue owns the visible controls;
frontend/src/voice.js owns browser media/peer/audio/timers and cleanup;
backend/voice.py owns typed routes, model settings, provider creation and server
cleanup; backend/voice_prompts.py owns LIVE_INSTRUCTIONS and
DELEGATED_INSTRUCTIONS. The live prompt handles conversational delivery and
delegates app knowledge; the delegated prompt contains the reviewed skill and
boundaries. No saved history is supplied to voice.

No code path persists audio or transcripts. The isolated backend creation/close
test checks that database messages/sessions remain empty. Actual provider/hardware
behavior, the sideband closure exchange, a short live observation and the
public-demo comparison are still unverified. A network/process loss can leave
provider closure unconfirmed even after local microphone release.
