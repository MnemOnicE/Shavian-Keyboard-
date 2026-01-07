# Team Memory

## Current Context
**Project:** AutoShavian
**Goal:** Local-first real-time phonetic transcription to Shavian.
**Phase:** Phase 2: Packaging.

## Key Decisions
*   **Architecture:** Sidecar Pattern (Python Backend + Web Frontend).
*   **Engine:** `faster-whisper` (CTranslate2).
*   **Protocol:** WebSockets.
*   **Privacy:** Strict Local-first (No cloud STT).
*   **Model:** `base.en` selected for MVP balance of speed/accuracy.
*   **Frontend:** Vanilla JS with 16kHz audio capture.

## Active Constraints
*   **Performance:** Must run on consumer hardware (Bolt).
*   **Accessibility:** UI must be simple and high-contrast (Palette).
*   **Security:** No audio logging to disk (Sentinel).

## Lessons Learned
*   **MVP Scope:** VAD (Voice Activity Detection) on the server is complex; MVP relies on client-side "Stop Recording" or explicit chunks.
*   **Audio Format:** `faster-whisper` expects 16kHz mono. Browser `AudioContext` resampling is required.
