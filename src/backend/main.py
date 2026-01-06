import asyncio
import json
import logging
import sys
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from concurrent.futures import ThreadPoolExecutor

# Adjust path to import local lib
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.shavian import ShavianConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoShavian")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model
# usage: "tiny", "base", "small", "medium", "large"
MODEL_SIZE = "base.en"
logger.info(f"Loading Whisper model: {MODEL_SIZE}...")
try:
    # Run on CPU for broad compatibility, use "cuda" if available
    # For MVP we default to CPU to ensure it runs everywhere without setup
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    sys.exit(1)

converter = ShavianConverter()

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected")

    # We'll accumulate audio here.
    # In a real streaming scenario, we'd use VAD to segment.
    # For this MVP, we might accept chunks and process them periodically or on a signal.
    # But faster-whisper is good at processing full segments.
    # Strategy: Client sends audio chunks.
    # Client sends a JSON message {"action": "process"} to trigger transcription of buffer?
    # Or we just append and transcribe every X seconds?
    # Let's try: Real-time streaming is hard without VAD.
    # Simplest MVP: Client records -> Client stops/pauses -> Client sends full blob -> Server returns text.
    # Slightly better: Client streams, Server accumulates. Client sends "end_speech" marker.

    # Actually, let's look at the specs: "Receives binary audio chunks -> Processes VAD -> Transcribes"
    # Implementing VAD on server side is complex for MVP.
    # Let's assume the client sends a stream of bytes, and we process it.

    # To keep it interactive, maybe we implement a simple silence detection or
    # just transcribe every 1-2 seconds of accumulated audio?
    # Continuous transcription with `faster-whisper` usually involves feeding it a stream.

    # Let's go with a simplified approach for Phase 1:
    # Client sends audio chunks.
    # Every 2 seconds (or if silence), we transcribe the buffer.

    audio_buffer = np.array([], dtype=np.float32)

    try:
        while True:
            # Receive data: can be bytes (audio) or text (commands)
            data = await websocket.receive()

            if "bytes" in data:
                # Append to buffer
                # Assuming Float32 little endian raw PCM 16kHz
                chunk = np.frombuffer(data["bytes"], dtype=np.float32)
                audio_buffer = np.concatenate((audio_buffer, chunk))

                # If buffer is big enough (e.g. > 3 seconds), let's try to transcribe
                # This is a naive "infinite stream" implementation.
                # Better: Client handles the "speech segment" logic (e.g. using RecordRTC with VAD)
                # and sends distinct files/blobs.
                # Let's assume the client is smart enough to send us "sentences".
                pass

            if "text" in data:
                msg = json.loads(data["text"])
                if msg.get("action") == "transcribe":
                    # Transcribe current buffer
                    if len(audio_buffer) > 0:
                        logger.info(f"Transcribing {len(audio_buffer)/16000:.2f}s of audio...")
                        segments, info = model.transcribe(audio_buffer, beam_size=5)

                        full_text = ""
                        for segment in segments:
                            full_text += segment.text + " "

                        full_text = full_text.strip()
                        shavian_text = converter.convert_sentence(full_text)

                        response = {
                            "text": full_text,
                            "shavian": shavian_text
                        }
                        await websocket.send_json(response)

                        # Clear buffer? Or keep context?
                        # Usually clear for "command" style, keep for "dictation".
                        # Let's clear for now to avoid re-transcribing old stuff repeatedly.
                        audio_buffer = np.array([], dtype=np.float32)

                elif msg.get("action") == "clear":
                    audio_buffer = np.array([], dtype=np.float32)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
