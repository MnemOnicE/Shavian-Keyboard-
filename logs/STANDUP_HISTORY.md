# Standup History

## [2025-12-28] MVP Architecture Debate
**Topic:** MVP Architecture (System Agnostic, Local-first)
**Participants:** Boom, Bolt, Sentinel, Orbit, Palette, Brain.

**Summary:**
The team debated between Native, Web, and Hybrid approaches.
*   **Boom** requested OpenAI Whisper (Cloud).
*   **Sentinel** rejected Cloud for Privacy (Local-first mandate).
*   **Bolt** rejected heavy standard Whisper for `faster-whisper`.
*   **Orbit** suggested a "Sidecar" pattern to allow System Agnostic UI with Local Performance.

**Verdict:**
Adopted **Local-Server Hybrid Architecture**.
*   **Backend:** Python (`faster-whisper`, FastAPI).
*   **Frontend:** Web (HTML/JS) over WebSockets.

## [2026-01-12] Audit & Packaging Verification
**Topic:** Audit & Phase 2 (Packaging)
**Participants:** Brain, Scribe.

**Summary:**
*   **Audit:** Performed a full repository audit. MVP tests passed (Backend, Integration, Shavian Logic).
*   **Packaging:** Verified `autoshavian.spec` by running PyInstaller. Build was successful.
*   **Environment:** Installed necessary dependencies (`hypothesis`, `faster-whisper`, etc.).

**Verdict:**
Phase 2 (Packaging) is verified complete. The artifact is generated in `dist/`.

## [2026-04-01] Repository Audit
**Topic:** System Audit (Blueprint, Debt, Status, Reflect)
**Participants:** Brain

**Summary:**
*   **Blueprint:** Analyzed Local-Server Hybrid architecture (FastAPI/WebSockets/AudioWorklet). Full report logged in `logs/AUDIT_REPORT.md`.
*   **Debt:** Evaluated linting and test coverage. Remedied numerous `flake8` violations across `src` and `tests`. Fixed failing `pytest` cases involving WebSocket exceptions, Starlette CORS responses, and numpy mock arrays. All 32 active tests now pass cleanly.
*   **Status:** Reviewed `ROADMAP.md`. Confirmed that "Custom Shavian Font Bundling" was already completed and bundled via PyInstaller. Transitioning to "Packaging & Polish" phase for the Settings Menu feature.

**Verdict:**
Repository is in a healthy state. Technical debt has been resolved. The roadmap accurately reflects the current state, and the next immediate priority is implementing the Settings Menu for model size selection.
