import webrtcvad
import numpy as np
import collections

class VadManager:
    """
    Manages Voice Activity Detection (VAD) using webrtcvad.
    Accepts Float32 audio, converts to Int16 for processing,
    and returns segmented audio chunks when speech ends.
    """
    def __init__(self, sample_rate=16000, frame_duration_ms=30, mode=2):
        self.vad = webrtcvad.Vad(mode)
        self.sample_rate = sample_rate
        # frame_length in samples. 30ms @ 16kHz = 480 samples
        self.frame_length = int(sample_rate * frame_duration_ms / 1000)

        # Buffer to accumulate incoming chunks until we have a full frame
        self.buffer = np.array([], dtype=np.float32)

        self.triggered = False
        self.speech_buffer = []  # List of float32 frames

        # Ring buffer for pre-trigger context (approx 300ms)
        self.pre_trigger_buffer = collections.deque(maxlen=10)

        self.consecutive_speech = 0
        self.consecutive_silence = 0

        # Parameters
        self.SPEECH_START_FRAMES = 5   # ~150ms of speech to trigger start
        self.SILENCE_END_FRAMES = 20   # ~600ms of silence to trigger end

    def process_chunk(self, chunk: np.ndarray):
        """
        Input: Float32 chunk (arbitrary size).
        Yields: Float32 array (phrase) whenever a speech segment is finalized.
        """
        self.buffer = np.concatenate((self.buffer, chunk))

        while len(self.buffer) >= self.frame_length:
            # Extract one frame
            frame = self.buffer[:self.frame_length]
            self.buffer = self.buffer[self.frame_length:]

            # Convert to Int16 for WebRTC (expects 16-bit PCM mono)
            # Clipping is good practice before cast
            pcm_frame = (np.clip(frame, -1.0, 1.0) * 32767).astype(np.int16).tobytes()

            is_speech = self.vad.is_speech(pcm_frame, self.sample_rate)

            if is_speech:
                self.consecutive_silence = 0
                self.consecutive_speech += 1
            else:
                self.consecutive_silence += 1
                self.consecutive_speech = 0

            if not self.triggered:
                self.pre_trigger_buffer.append(frame)
                if self.consecutive_speech >= self.SPEECH_START_FRAMES:
                    self.triggered = True
                    # Start of speech detected.
                    # Move everything from pre-trigger buffer to speech buffer
                    for f in self.pre_trigger_buffer:
                        self.speech_buffer.append(f)
                    self.pre_trigger_buffer.clear()
            else:
                # We are in a speech segment
                self.speech_buffer.append(frame)
                if self.consecutive_silence >= self.SILENCE_END_FRAMES:
                    # End of speech detected.
                    self.triggered = False

                    # Yield the accumulated speech
                    if self.speech_buffer:
                        result = np.concatenate(self.speech_buffer)
                        self.speech_buffer = []
                        yield result

                    self.consecutive_speech = 0
                    self.consecutive_silence = 0

    def flush(self):
        """
        Returns any remaining audio in the buffer as a segment.
        Useful when connection closes or user manually stops.
        """
        # If we have pending speech in speech_buffer, return it
        results = []
        if self.triggered and self.speech_buffer:
            results.append(np.concatenate(self.speech_buffer))

        # Reset state
        self.triggered = False
        self.speech_buffer = []
        self.pre_trigger_buffer.clear()
        self.buffer = np.array([], dtype=np.float32)
        self.consecutive_speech = 0
        self.consecutive_silence = 0

        return results
