import sys
import os
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# NOTE: The following mock_modules and sys.modules manipulation is necessary
# because the current testing environment lacks several key dependencies
# (e.g., faster-whisper, fastapi, numpy). This approach allows us to verify
# the logic of transcribe_buffer without requiring a full environment setup.

mock_modules = {
    'faster_whisper': MagicMock(),
    'fastapi': MagicMock(),
    'fastapi.middleware.cors': MagicMock(),
    'fastapi.staticfiles': MagicMock(),
    'numpy': MagicMock(),
    'webrtcvad': MagicMock(),
}

with patch.dict(sys.modules, mock_modules):
    import numpy as np

    # Mock numpy.ndarray for type checking used in transcribe_buffer signature
    class MockNdArray:
        def __init__(self, data):
            self.data = data
        def __len__(self):
            return len(self.data)
        def __truediv__(self, other):
            # Support len(audio_buffer)/16000 calculation in logger
            return len(self.data) / other

    np.ndarray = MockNdArray

    # Pre-mock ShavianConverter and VadManager to avoid actual imports during
    # module-level execution of backend.main
    with patch('lib.shavian.ShavianConverter', MagicMock()), \
         patch('backend.vad.VadManager', MagicMock()):
        import backend.main as main_mod

# NOTE: Using asyncio.run inside synchronous test functions because
# pytest-asyncio is not available/configured in this environment.

def test_transcribe_buffer_empty():
    """Verify that empty audio buffer does not trigger transcription."""
    async def run_test():
        # Setup
        mock_websocket = AsyncMock()
        empty_audio = MockNdArray([])

        with patch.object(main_mod, 'get_model') as mock_get_model:
            # Execute
            await main_mod.transcribe_buffer(empty_audio, mock_websocket)

            # Verify
            mock_get_model.assert_not_called()
            mock_websocket.send_json.assert_not_called()

    asyncio.run(run_test())

def test_transcribe_buffer_no_text():
    """Verify that if transcription yields no text, no message is sent via WebSocket."""
    async def run_test():
        # Setup
        mock_websocket = AsyncMock()
        audio = MockNdArray([0.1] * 16000)
        mock_model = MagicMock()

        # model.transcribe returns (segments, info)
        # segments is an iterator, info is a namedtuple-like object
        mock_model.transcribe.return_value = (iter([]), MagicMock())

        with patch.object(main_mod, 'get_model', return_value=mock_model), \
             patch.object(main_mod, 'converter') as mock_converter:

            # Mock converter to return what's expected for empty string
            mock_converter.convert_sentence_with_ipa.return_value = ("", "")

            # Execute
            await main_mod.transcribe_buffer(audio, mock_websocket)

            # Verify
            mock_model.transcribe.assert_called_once()
            mock_websocket.send_json.assert_not_called()

    asyncio.run(run_test())

def test_transcribe_buffer_with_text():
    """Verify that successful transcription is converted and sent via WebSocket."""
    async def run_test():
        # Setup
        mock_websocket = AsyncMock()
        audio = MockNdArray([0.1] * 16000)
        mock_model = MagicMock()

        mock_segment = MagicMock()
        mock_segment.text = "hello"
        mock_model.transcribe.return_value = (iter([mock_segment]), MagicMock())

        with patch.object(main_mod, 'get_model', return_value=mock_model), \
             patch.object(main_mod, 'converter') as mock_converter:

            mock_converter.convert_sentence_with_ipa.return_value = (
                "𐑣𐑧𐑤𐑴", "hello [/həˈloʊ/]"
            )

            # Execute
            await main_mod.transcribe_buffer(audio, mock_websocket)

            # Verify
            mock_model.transcribe.assert_called_once()
            mock_websocket.send_json.assert_called_once_with({
                "text": "hello",
                "shavian": "𐑣𐑧𐑤𐑴",
                "english_with_ipa": "hello [/həˈloʊ/]"
            })

    asyncio.run(run_test())
