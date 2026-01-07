# Project Roadmap

## 🚀 Active Features
- [ ] **PyInstaller Packaging** (Phase 2)
    - [ ] **Spec File:** Create `autoshavian.spec` for single-file executable.
    - [ ] **Asset Bundling:** Ensure `src/frontend` and `faster-whisper` models are bundled correctly.
    - [ ] **Build Script:** Create `scripts/build.sh` or `build.bat`.

## 📅 Planned
- [ ] Custom Shavian Font Bundling
- [ ] Settings Menu (Model Selection: Tiny/Base/Small)

## ✅ Completed
- [x] **Architecture Decision:** Local-Server Hybrid (Sidecar).
- [x] **MVP Implementation** (Phase 1)
    - [x] **Backend:** Setup FastAPI + `faster-whisper`.
    - [x] **Logic:** Implement English -> Shavian converter.
    - [x] **Frontend:** Basic Web UI for recording and displaying text.
    - [x] **Glue:** WebSocket streaming integration.
