# AutoShavian Repository Audit Report

## 1. Blueprint Analysis
The AutoShavian project implements a Local-Server Hybrid architecture designed for system-agnostic phonetic speech-to-text conversion into Shavian characters.

### Key Components:
- **Backend (`src/backend`)**: Built with FastAPI. Uses `faster-whisper` for local speech-to-text transcription. Integrates `webrtcvad` for continuous streaming voice activity detection. Communication with the frontend is exclusively over WebSockets.
- **Frontend (`src/frontend`)**: Plain HTML/JS/CSS. Utilizes `AudioWorklet` to stream Float32 audio to the backend. Features a custom font `Noto Sans Shavian` for rendering Shavian text.
- **Library (`src/lib`)**: The `ShavianConverter` module (`shavian.py`) handles translation from English text to IPA and then to Shavian characters, utilizing pre-compiled regex for performance and a fallback mechanism for unknown words.
- **Testing (`tests/`)**: A suite of tests including unit tests (`test_shavian_unit.py`), backend integration (`test_backend.py`), frontend rendering/layout tests (`test_frontend.py`), and benchmarks.
- **Packaging**: Managed by PyInstaller using `autoshavian.spec`, producing a standalone `onedir` distribution bundling both frontend assets and backend logic.


## 2. Debt Evaluation & Remediation
- **Linting Debt (`flake8`)**: Found multiple formatting and unused import errors across `src` and `tests`.
    - **Remediation**: Re-formatted codebase using `black` and `isort`. Used a custom script to resolve unused imports (e.g., `pytest`, `re`) and added `noqa` comments where necessary.
- **Testing Debt (`pytest`)**:
    - The `test_websocket_payload_size.py` tests were failing to catch `WebSocketDisconnect` properly; fixed by patching with `pytest.raises`.
    - `src/backend/main.py` had a syntax error (`keyword argument repeated: allow_methods`) which broke test collection. Fixed by removing the duplicate keyword argument.
    - `test_cors_policy.py` asserted missing headers when a 400 status code is actually returned by Starlette for disallowed methods; updated the assertion.
    - `test_vad_unit.py` had a numpy-like mock array equality error; fixed by casting to list.
    - Added testing dependencies (`hypothesis`, `pytest`, `httpx`, `flake8`) to environment.
- **Result**: All tests now pass successfully (32 passed, 1 deselected UI layout test). Zero flake8 errors.

## 3. Status Check & Roadmap Update
- **Current State vs. Roadmap**:
    - **Custom Shavian Font Bundling**: This was marked as Planned, but `src/frontend/fonts/NotoSansShavian-Regular.ttf` is present, referenced in `src/frontend/index.html`, and PyInstaller's `autoshavian.spec` bundles the entire `src/frontend` directory (`datas=[('src/frontend', 'frontend')]`). Thus, it is fully implemented.
    - **Settings Menu**: Confirmed missing from `index.html` and `main.py` hardcodes `MODEL_SIZE = "base.en"`.
- **Roadmap Changes**:
    - Moved "Custom Shavian Font Bundling" to ✅ Completed.
    - Moved "Settings Menu (Model Selection: Tiny/Base/Small)" into an Active Features section under a new Phase 3.
