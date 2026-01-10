import asyncio
import json
import logging
import sys
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
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

async def transcribe_buffer(audio_buffer: np.ndarray, websocket: WebSocket):
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

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected")

    audio_buffer = np.array([], dtype=np.float32)
    MAX_BUFFER_SAMPLES = 480000 # 30 seconds at 16kHz

    try:
        while True:
            # Receive data: can be bytes (audio) or text (commands)
            data = await websocket.receive()

            if "bytes" in data:
                # Append to buffer
                # Assuming Float32 little endian raw PCM 16kHz
                chunk = np.frombuffer(data["bytes"], dtype=np.float32)
                audio_buffer = np.concatenate((audio_buffer, chunk))

                # Safety Valve: Check if buffer exceeds 30 seconds
                if len(audio_buffer) > MAX_BUFFER_SAMPLES:
                    logger.info("Buffer exceeded 30s. Triggering auto-transcribe safety valve.")
                    await transcribe_buffer(audio_buffer, websocket)
                    audio_buffer = np.array([], dtype=np.float32)

            if "text" in data:
                msg = json.loads(data["text"])
                if msg.get("action") == "transcribe":
                    await transcribe_buffer(audio_buffer, websocket)
                    audio_buffer = np.array([], dtype=np.float32)

                elif msg.get("action") == "clear":
                    audio_buffer = np.array([], dtype=np.float32)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.close()

# Mount frontend
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
