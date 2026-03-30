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

## Actions Taken (2026-03-30)
* **Autopilot (`/auto`)**: Implemented "Custom Shavian Font Bundling" by updating `src/backend/main.py` to properly resolve the PyInstaller `frontend` path so `NotoSansShavian-Regular.ttf` is successfully mounted and served.
* **Heal (`/heal`)**: Diagnosed and fixed broken test suite. Installed missing dependencies (via `requirements.txt` and system packages for tests: `pytest`, `hypothesis`, `flake8`). Fixed the `pkg_resources` `ModuleNotFoundError` by rolling back to `setuptools<70` (needed for `webrtcvad`). Patched broken websocket payload tests and timeout-prone backend integration tests that hung when faster-whisper omitted silence text.
* **Reflect (`/reflect`)**: Updated `TEAM_MEMORY.md` reflecting successful `/auto` and `/heal` execution.
