import json
import logging
import os
import sys

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel

# Adjust path to import local lib
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.vad import VadManager  # noqa: E402
from lib.shavian import ShavianConverter  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoShavian")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)

# usage: "tiny", "base", "small", "medium", "large"
MODEL_SIZE = "base.en"
_model = None


def get_model():
    """Lazy initialization of the Whisper model."""
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model: {MODEL_SIZE}...")
        try:
            # Run on CPU for broad compatibility, use "cuda" if available
            # For MVP we default to CPU to ensure it runs everywhere without
            # setup
            _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")  # noqa: E501
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            sys.exit(1)
    return _model


converter = ShavianConverter()


async def transcribe_buffer(audio_buffer: np.ndarray, websocket: WebSocket):
    if len(audio_buffer) > 0:
        logger.info(f"Transcribing {len(audio_buffer)/16000:.2f}s of audio...")
        model = get_model()

        segments, info = model.transcribe(audio_buffer, beam_size=5)

        full_text = " ".join([segment.text.strip() for segment in segments if segment.text.strip()])
        if not full_text:
            return
        shavian_text, english_with_ipa = converter.convert_sentence_with_ipa(full_text)  # noqa: E501

        # Only send if there is actual text
        if full_text:
            response = {
                "text": full_text,
                "shavian": shavian_text,
                "english_with_ipa": english_with_ipa,
            }
            await websocket.send_json(response)


@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected")

    # Initialize VAD Manager for this connection
    vad_manager = VadManager()

    # We remove the simple audio_buffer and rely on vad_manager,
    # but we might need to handle the "Safety Valve" manually
    # Actually, VadManager accumulates internally.
    # To implement the Safety Valve, we check vad_manager state.

    # Since VadManager.speech_buffer is a list of arrays, we can estimate size.
    MAX_BUFFER_FRAMES = 1000  # 1000 frames * 30ms = 30 seconds

    # Maximum allowed payload size: 1MB
    MAX_PAYLOAD_SIZE = 1 * 1024 * 1024

    try:
        while True:
            # Receive data: can be bytes (audio) or text (commands)
            data = await websocket.receive()

            if "bytes" in data and len(data["bytes"]) > MAX_PAYLOAD_SIZE:
                logger.warning(
                    "Received binary payload exceeding "
                    "MAX_PAYLOAD_SIZE. Closing connection."
                )
                await websocket.close(code=1009)
                break

            if "text" in data and len(data["text"]) > MAX_PAYLOAD_SIZE:
                logger.warning(
                    "Received text payload exceeding "
                    "MAX_PAYLOAD_SIZE. Closing connection."
                )
                await websocket.close(code=1009)
                break

            if "bytes" in data:
                # Append to buffer
                # Assuming Float32 little endian raw PCM 16kHz
                chunk = np.frombuffer(data["bytes"], dtype=np.float32)

                # Process with VAD
                # process_chunk returns a generator of segments
                for segment in vad_manager.process_chunk(chunk):
                    logger.info("VAD triggered transcription.")
                    await transcribe_buffer(segment, websocket)

                # Safety Valve: Check if internal buffer exceeds limit
                # We check the size of the current accumulating speech buffer
                if len(vad_manager.speech_buffer) > MAX_BUFFER_FRAMES:
                    logger.info(
                        "Buffer exceeded 30s. Triggering "
                        "auto-transcribe safety valve."
                    )
                    segments = vad_manager.flush()
                    for segment in segments:
                        await transcribe_buffer(segment, websocket)

            if "text" in data:
                msg = json.loads(data["text"])
                if msg.get("action") in ("transcribe", "flush"):
                    # Force flush and transcribe
                    segments = vad_manager.flush()
                    for segment in segments:
                        await transcribe_buffer(segment, websocket)

                elif msg.get("action") == "clear":
                    # Flush and discard
                    vad_manager.flush()

                elif msg.get("action") == "translate_text":
                    text = msg.get("text", "")
                    if text:
                        shavian_text, english_with_ipa = (
                            converter.convert_sentence_with_ipa(text)
                        )  # noqa: E501
                        response = {
                            "is_translation": True,
                            "original_text": text,
                            "shavian": shavian_text,
                            "english_with_ipa": english_with_ipa,
                        }
                        await websocket.send_json(response)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.close()


# Mount frontend
def get_frontend_dir():
    if getattr(sys, "frozen", False):
        # PyInstaller onedir mode: sys._MEIPASS or sys.executable dir
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.join(base_path, "frontend")
    else:
        return os.path.join(os.path.dirname(__file__), "..", "frontend")


frontend_dir = get_frontend_dir()
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
