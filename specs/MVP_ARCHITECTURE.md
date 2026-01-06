# MVP Architecture: AutoShavian (Local-Hybrid)

## 1. High-Level Overview
**AutoShavian** is a local-first, system-agnostic phonetic transcription tool. It listens to user speech, converts it to text using a local Speech-to-Text (STT) engine, and then transliterates that text into the **Shavian alphabet**.

### Architecture Pattern: Local-Server Hybrid (Sidecar)
To achieve "System Agnostic" behavior while maintaining "Local Performance," we decouple the engine from the UI.
*   **The Engine (Backend):** A Python process managing the heavy ML inference.
*   **The Interface (Frontend):** A lightweight Web Interface (HTML/JS) running in a browser or webview, communicating via WebSockets.

## 2. Component Specifications

### A. The Engine (Backend)
*   **Runtime:** Python 3.10+
*   **Core Library:** `faster-whisper` (CTranslate2 implementation of Whisper).
    *   *Reasoning:* 4x faster than OpenAI's implementation with 2x less memory usage.
*   **API Layer:** `FastAPI` (Async).
*   **Protocol:** WebSockets (`/ws/transcribe`).
    *   *Data Flow:* Receives binary audio chunks -> Processes VAD (Voice Activity Detection) -> Transcribes -> Returns JSON events.
*   **Shavian Converter:** Custom Python module (`pymath` or similar folder structure, likely `src/converter`).
    *   *Logic:* Dictionary-based lookup + Phonetic fallback.
*   **Distribution:** `PyInstaller` (Single binary executable for target OS).

### B. The Interface (Frontend)
*   **Tech Stack:** Vanilla HTML/JS or Vue.js (Lightweight).
*   **Audio Capture:** Browser `MediaStreamAPI`.
    *   *Format:* Float32 PCM (resampled to 16kHz before sending).
*   **Display:**
    *   **Font:** `Inter Alia` (bundled WOFF2).
    *   **Behavior:** Streaming text (append-only log).
*   **State:** Minimal client-side state (Connected/Disconnected, Recording/Paused).

## 3. Data Flow
1.  **User** clicks "Record" in Web UI.
2.  **Frontend** opens WebSocket to `localhost:8000`.
3.  **Frontend** captures microphone audio, downsamples to 16kHz mono.
4.  **Frontend** streams audio chunks (binary) to Backend.
5.  **Backend** (`faster-whisper`) accumulates chunks and detects voice activity.
6.  **Backend** transcribes speech segment -> "Hello World".
7.  **Backend** converts "Hello World" -> "𐑯𐑩𐑤𐑴 𐑢𐑻𐑤𐑛".
8.  **Backend** sends JSON: `{ "text": "Hello World", "shavian": "𐑯𐑩𐑤𐑴 𐑢𐑻𐑤𐑛" }`.
9.  **Frontend** renders the Shavian text.

## 4. Privacy & Security
*   **Offline Requirement:** The app must function with 0 internet access (after initial model download).
*   **Data Persistence:** No audio is saved to disk by default. Logs are ephemeral.

## 5. Roadmap / Phasing
*   **Phase 1 (MVP):** Python script + Browser Tab. Works on dev machine.
*   **Phase 2:** Executable packaging (PyInstaller).
*   **Phase 3:** Native wrapper (if needed) or PWA manifest.
