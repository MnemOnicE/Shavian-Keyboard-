import sys
import os
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio

# Add src and tests/mocks to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "mocks")))

# Mock missing dependencies BEFORE importing the module that uses them
mock_np = MagicMock()
sys.modules["numpy"] = mock_np
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["faster_whisper"] = MagicMock()
sys.modules["backend.vad"] = MagicMock()

from backend.main import transcribe_buffer

class TestTranscribeBufferEmpty(unittest.TestCase):
    def run_async(self, coro):
        return asyncio.run(coro)

    @patch("backend.main.get_model")
    def test_transcribe_buffer_empty_segments(self, mock_get_model):
        # Setup mocks
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([], None) # Empty segments list
        mock_get_model.return_value = mock_model

        mock_websocket = AsyncMock()

        audio_buffer = [0] * 16000 # Dummy buffer
        self.run_async(transcribe_buffer(audio_buffer, mock_websocket))

        # Verify websocket.send_json was NOT called
        mock_websocket.send_json.assert_not_called()

    @patch("backend.main.get_model")
    def test_transcribe_buffer_whitespace_segments(self, mock_get_model):
        # Setup mocks
        mock_segment = MagicMock()
        mock_segment.text = "   " # Whitespace text
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_get_model.return_value = mock_model

        mock_websocket = AsyncMock()

        audio_buffer = [0] * 16000
        self.run_async(transcribe_buffer(audio_buffer, mock_websocket))

        # Verify websocket.send_json was NOT called
        mock_websocket.send_json.assert_not_called()

    @patch("backend.main.get_model")
    def test_transcribe_buffer_happy_path(self, mock_get_model):
        # Setup mocks
        mock_segment = MagicMock()
        mock_segment.text = "Hello"
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ([mock_segment], None)
        mock_get_model.return_value = mock_model

        mock_websocket = AsyncMock()

        audio_buffer = [0] * 16000
        self.run_async(transcribe_buffer(audio_buffer, mock_websocket))

        # Verify websocket.send_json WAS called
        mock_websocket.send_json.assert_called_once()
        args, kwargs = mock_websocket.send_json.call_args
        response = args[0]
        assert response["text"] == "Hello"
        assert "shavian" in response
        assert "english_with_ipa" in response

if __name__ == "__main__":
    unittest.main()
