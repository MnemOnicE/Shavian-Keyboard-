# Team Memory

## Current Context
**Project:** AutoShavian
**Goal:** Local-first real-time phonetic transcription to Shavian.
**Phase:** Packaging & Polish.

## Key Decisions
*   **Architecture:** Sidecar Pattern (Python Backend + Web Frontend).
*   **Engine:** `faster-whisper` (CTranslate2).
*   **Protocol:** WebSockets.
*   **Privacy:** Strict Local-first (No cloud STT).
*   **Packaging:** PyInstaller `onedir` mode confirmed working.

## Active Constraints
*   **Performance:** Must run on consumer hardware (Bolt).
*   **Accessibility:** UI must be simple and high-contrast (Palette).
*   **Security:** No audio logging to disk (Sentinel).
