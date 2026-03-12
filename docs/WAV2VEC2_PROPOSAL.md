# Wav2Vec2Phoneme Integration Proposal

This document outlines a phased implementation plan for true Speech-to-Phoneme transcription using the Wav2Vec2Phoneme model to facilitate direct phonetic sound to Shavian character conversion. This addresses the challenge of recognizing a speaker's unique accent, rather than transcribing to English text and then converting standard English dictionary phonetics.

## Objective
Migrate the `AutoShavian` backend transcription engine from Faster-Whisper (Speech-to-Text) to `Wav2Vec2Phoneme` (Speech-to-Phoneme), enabling "Direct to Shavian" translation based on actual spoken sounds, all while preserving the local-first, zero-cost (free models) principles of the project.

## Phased Approach

### Phase 1: Research & Environment Testing (Current Architecture Unaffected)
1. **Model Evaluation:** Test `Wav2Vec2Phoneme` checkpoints from Hugging Face (`facebook/wav2vec2-lv-60-espeak-cv-ft` or similar open-source weights). Ensure these models run effectively on typical CPU environments, matching our commitment to low hardware thresholds.
2. **Prototype Script:** Create a standalone Python script (`tests/test_wav2vec2.py`) to load the model via `transformers`, process a `.wav` file, and output the raw IPA string.
3. **Hardware & Resource Profiling:** Monitor memory usage. Transformers with large models can consume significant RAM. Ensure we can quantize (INT8) or find a sufficiently small model size that mimics our current Whisper `base.en` resource footprint.

### Phase 2: Shavian Mapping Adjustment
1. **Direct Phoneme Mapping:** Wav2Vec2Phoneme outputs an uninterrupted string of phonemes. We need to evaluate its output structure.
2. **Update `shavian.py`:** Create a new method in `ShavianConverter` that maps *raw IPA phoneme streams* directly to Shavian, without relying on `eng_to_ipa` word boundary lookups. This will involve handling coarticulation and dealing with the continuous phonetic stream which might not have clear word separations.

### Phase 3: Backend Integration (Dual Model System)
1. **Model Manager:** Update `src/backend/main.py` to support loading *either* Whisper or Wav2Vec2.
2. **WebSocket Routing:** When the UI toggle is set to "Direct to Shavian", route the incoming VAD audio buffers to the Wav2Vec2 inference engine instead of Whisper.
3. **Environment Updates:** Add `transformers`, `torch`, and any other required libraries to `requirements.txt`. (Note: PyTorch can be a very large dependency; we must evaluate the impact on the final `PyInstaller` package size).

### Phase 4: Full Deployment & Deprecation of Whisper (Optional)
1. **Evaluate:** If Wav2Vec2Phoneme performs well enough to handle standard dictation AND true phonetic Shavian transcription, we could theoretically deprecate Whisper entirely. However, Whisper provides English word boundaries which are useful for standard dictation modes.
2. **Packaging:** Update `autoshavian.spec` PyInstaller configuration to handle the new `transformers` dependencies and model weights.

## Environmental & Cost Constraints
* **Cost:** 100% Free. We will exclusively use models available on Hugging Face Model Hub under open licenses (Apache 2.0 or MIT).
* **Local First:** All model weights will be downloaded and executed locally. No cloud APIs will be used.
* **CPU Priority:** The implementation must prioritize CPU execution using `torch` CPU builds to ensure broad system compatibility without requiring CUDA drivers.
* **Package Size:** Integrating `torch` and `transformers` will drastically increase the packaged size of the application. We will investigate minimal dependencies (e.g., using ONNX Runtime for inference instead of full PyTorch) to keep the download size manageable.
