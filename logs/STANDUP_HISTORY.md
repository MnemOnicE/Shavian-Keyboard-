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
